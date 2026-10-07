#!/usr/bin/env python3
"""Measure Python files for bulk: file length and per-function size, arguments, branches,
nesting, cyclomatic and cognitive complexity. Prints only what exceeds a limit; exit 1 if any.

Usage:
  measure.py PATH...                 files or folders
  measure.py --changed [DIR]         files changed in git (staged, unstaged, untracked) under DIR
  measure.py --since REF PATH...     report only what got worse than REF (e.g. HEAD); files
                                     unknown to git at REF are reported in full
  measure.py --all PATH...           also list functions within limits

Default limits (override with --max-<name>): file 400 code lines; per function 50 statements,
5 arguments, 12 branches, nesting 5 (pylint max-statements / max-args / max-branches /
max-nested-blocks), cyclomatic 10 (McCabe), cognitive 15 (SonarSource rule S3776).
Documentation (skip with --no-docs): every function has a docstring and every for/while loop has
a comment on its line or the line above; test files and test_* functions are exempt.
Standard library only.
"""
from __future__ import annotations

import argparse
import ast
import io
import subprocess
import sys
import tokenize
from pathlib import Path

LIMITS = dict(file=400, statements=50, args=5, branches=12, nesting=5, complexity=10, cognitive=15,
              missing_doc=0, bare_loops=0)
SIZE_KEYS = ('statements', 'args', 'branches', 'nesting', 'complexity', 'cognitive')
DOC_KEYS = ('missing_doc', 'bare_loops')
FUNCTION_KEYS = SIZE_KEYS + DOC_KEYS
LOOPS = (ast.For, ast.AsyncFor, ast.While)
FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)
BRANCHES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)
NESTING = (*BRANCHES, ast.Match)


# ---------- metrics ----------
def own_nodes(fn):
    """Nodes of fn, not descending into nested functions or classes."""
    stack = list(ast.iter_child_nodes(fn))
    # depth-first walk that stops at nested definitions
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (*FUNCS, ast.ClassDef, ast.Lambda)):
            stack.extend(ast.iter_child_nodes(node))


def nesting_depth(node, depth=0):
    """Deepest stack of nested if/for/while/try/with/match blocks under node."""
    best = depth
    # recurse into children, adding a level for each nesting block
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, (*FUNCS, ast.ClassDef)):
            best = max(best, nesting_depth(child, depth + isinstance(child, NESTING)))
    return best


def cognitive(node, level=0):
    """SonarSource cognitive complexity: +1 per break in linear flow, +nesting level for
    structures nested inside others, +1 per boolean-operator sequence."""
    score = 0
    # score each child construct, then recurse into its body at the right nesting level
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (*FUNCS, ast.Lambda)):
            score += cognitive(child, level + 1)  # nested function: deeper, not a break
        elif isinstance(child, ast.ClassDef):
            continue
        elif isinstance(child, ast.If):
            score += 1 + level + cognitive(ast.Expr(value=child.test), level)
            score += cognitive(ast.Module(body=child.body, type_ignores=[]), level + 1)
            orelse = child.orelse
            # walk the elif chain
            while len(orelse) == 1 and isinstance(orelse[0], ast.If):  # elif: +1, no nesting bonus
                score += 1 + cognitive(ast.Expr(value=orelse[0].test), level)
                score += cognitive(ast.Module(body=orelse[0].body, type_ignores=[]), level + 1)
                orelse = orelse[0].orelse
            if orelse:
                score += 1 + cognitive(ast.Module(body=orelse, type_ignores=[]), level + 1)
        elif isinstance(child, (ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.Match)):
            score += 1 + level + cognitive(child, level + 1)
        elif isinstance(child, ast.Try):
            score += cognitive(ast.Module(body=child.body + child.orelse + child.finalbody,
                                          type_ignores=[]), level)
            for handler in child.handlers:
                score += 1 + level + cognitive(handler, level + 1)
        elif isinstance(child, ast.BoolOp):
            score += 1 + cognitive(child, level)
        elif isinstance(child, ast.comprehension):
            score += 1 + len(child.ifs) + cognitive(child, level)
        else:
            score += cognitive(child, level)
    return score


def simple_body(loop) -> bool:
    """True when a loop's body is a single non-compound statement."""
    return len(loop.body) == 1 and not isinstance(loop.body[0], (*NESTING, *FUNCS, ast.ClassDef))


def function_metrics(fn, comment_lines: set, exempt: bool) -> dict:
    """Size, complexity and documentation numbers for one function (nested ones excluded)."""
    nodes = list(own_nodes(fn))
    # a loop counts as explained if a comment sits on its line or the line above;
    # a loop whose body is one simple statement explains itself
    bare = sum(1 for n in nodes if isinstance(n, LOOPS) and not simple_body(n)
               and not {n.lineno, n.lineno - 1} & comment_lines)
    decisions = sum(isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler,
                                   ast.comprehension, ast.match_case)) for n in nodes)
    decisions += sum(len(n.values) - 1 for n in nodes if isinstance(n, ast.BoolOp))
    a = fn.args
    args = len(a.posonlyargs) + len(a.args) + len(a.kwonlyargs) + bool(a.vararg) + bool(a.kwarg)
    if a.args and a.args[0].arg in ('self', 'cls'):
        args -= 1
    body = ast.Module(body=fn.body, type_ignores=[])
    return dict(statements=sum(isinstance(n, ast.stmt) for n in nodes), args=args,
                branches=sum(isinstance(n, BRANCHES) for n in nodes)
                + sum(len(n.handlers) for n in nodes if isinstance(n, ast.Try)),
                nesting=nesting_depth(fn), complexity=1 + decisions, cognitive=cognitive(body),
                missing_doc=0 if exempt or ast.get_docstring(fn) else 1, bare_loops=0 if exempt else bare,
                line=fn.lineno, lines=(fn.end_lineno or fn.lineno) - fn.lineno + 1)


def functions(tree, prefix=''):
    """Yield (qualified name, node) for every function and method, nested ones included."""
    # descend through classes and functions, building dotted names
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, FUNCS):
            yield prefix + node.name, node
            yield from functions(node, prefix + node.name + '.')
        elif isinstance(node, ast.ClassDef):
            yield from functions(node, prefix + node.name + '.')


def comment_lines(text: str) -> set:
    """Line numbers that carry a # comment."""
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        return {tok.start[0] for tok in tokens if tok.type == tokenize.COMMENT}
    except (tokenize.TokenError, SyntaxError):
        return set()


def file_metrics(text: str, is_test: bool = False) -> dict | None:
    """Code-line count plus per-function metrics; None if the text does not parse."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    code = sum(1 for l in text.splitlines() if l.strip() and not l.strip().startswith('#'))
    comments = comment_lines(text)
    return dict(code_lines=code, functions={
        name: function_metrics(fn, comments, exempt=is_test or fn.name.startswith('test'))
        for name, fn in functions(tree)})


def describe(key: str, value: int, limit: int) -> str:
    """Human wording for one over-limit metric."""
    if key == 'missing_doc':
        return 'no docstring'
    if key == 'bare_loops':
        return f'{value} loop(s) without a comment'
    return f'{key} {value}>{limit}'


# ---------- comparison with a git revision ----------
def text_at(path: Path, ref: str) -> str | None:
    """File content at ref, or None if git does not know the file there."""
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=path.parent,
                         capture_output=True, text=True)
    if top.returncode:
        return None
    rel = path.resolve().relative_to(Path(top.stdout.strip()).resolve())
    out = subprocess.run(['git', 'show', f'{ref}:{rel.as_posix()}'], cwd=path.parent,
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def over(metrics: dict, limits: dict) -> dict:
    """The metrics of one function that exceed their limit."""
    return {k: metrics[k] for k in FUNCTION_KEYS if k in limits and metrics[k] > limits[k]}


def report(path: Path, limits: dict, show_all: bool, since: str | None) -> int:
    """Print what is over the limits in one file (only what got worse when since is set)."""
    is_test = path.name.startswith('test_') or 'tests' in path.parts
    now = file_metrics(path.read_text(errors='replace'), is_test)
    if now is None:
        print(f'{path}: syntax error')
        return 1
    old = None
    if since:
        old_text = text_at(path, since)
        old = file_metrics(old_text, is_test) if old_text is not None else None
    flags, rows = [], []
    if now['code_lines'] > limits['file'] and (old is None or now['code_lines'] > old['code_lines']):
        grew = f' (was {old["code_lines"]})' if old else ''
        flags.append(f'  FILE {now["code_lines"]} code lines > {limits["file"]}{grew}')
    # one verdict line per function that is over a limit
    for name, m in now['functions'].items():
        bad = over(m, limits)
        if old is not None:  # keep only what is new or worse than before
            before = old['functions'].get(name)
            bad = {k: v for k, v in bad.items() if before is None or v > before[k]}
        if bad:
            was = old['functions'].get(name) if old else None
            parts = [describe(k, v, limits[k]) + (f' (was {was[k]})' if was and k in SIZE_KEYS else '')
                     for k, v in bad.items()]
            flags.append(f'  {name} (line {m["line"]}, {m["lines"]} lines): ' + ', '.join(parts))
        elif show_all:
            rows.append(f'  ok {name} (line {m["line"]}): ' + ', '.join(f'{k} {m[k]}' for k in FUNCTION_KEYS))
    if flags or show_all:
        mode = '' if not since else (f', vs {since}' if old else ', new to git')
        print(f'{path}  [{now["code_lines"]} code lines{mode}]')
        for line in flags + rows:
            print(line)
    return len(flags)


# ---------- file selection ----------
def changed(root: Path) -> list[Path]:
    """Python files under root that differ from HEAD or are untracked."""
    def run(*a):
        """Run a git command in root and return its output split into words."""
        return subprocess.run(['git', *a], cwd=root, capture_output=True, text=True).stdout.split()
    top = Path(run('rev-parse', '--show-toplevel')[0])
    names = set(run('diff', '--name-only', 'HEAD')) | set(
        run('ls-files', '--others', '--exclude-standard', '--full-name'))
    return sorted(p for p in (top / n for n in names) if p.suffix == '.py' and p.is_file()
                  and root.resolve() in (p.resolve(), *p.resolve().parents))


def main():
    """Parse arguments, pick the files, report each, exit 1 if anything is over a limit."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--changed', action='store_true')
    ap.add_argument('--since', metavar='REF')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--no-docs', action='store_true', help='skip the docstring / loop-comment checks')
    # one --max-<name> flag per size limit
    for k in ('file', *SIZE_KEYS):
        ap.add_argument(f'--max-{k}', type=int, default=LIMITS[k], dest=k)
    args = ap.parse_args()
    limits = {k: getattr(args, k) for k in ('file', *SIZE_KEYS)}
    if not args.no_docs:
        limits.update({k: LIMITS[k] for k in DOC_KEYS})
    if args.changed:
        files = changed(Path(args.paths[0] if args.paths else '.'))
    else:
        files = []
        # expand folders into their .py files
        for p in map(Path, args.paths):
            files += sorted(p.rglob('*.py')) if p.is_dir() else [p]
    files = [f for f in files if '__pycache__' not in f.parts]
    total = sum(report(f, limits, args.all, args.since) for f in files)
    print(f'MEASURE {"PASS" if not total else f"{total} over limit"} ({len(files)} files)')
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
