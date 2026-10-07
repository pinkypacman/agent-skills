#!/usr/bin/env python3
"""Helper for the structure skill: inventory a code folder, and check a STRUCTURE.md figure.

Usage:
  structure.py scan  DIR          inventory of DIR: files, aims, definitions, imports, path loads 
  (prints an inventory so the agent knows what to draw)
  
  structure.py check STRUCTURE.md every <b>file</b> [· symbol] named in the figure still exists 
  (check if every file/function named in the figure exists)

Paths in a figure are relative to the folder holding STRUCTURE.md. A path that does not exist
there is tried against each enclosing folder, so write files outside the scope relative to the
project root (e.g. tools/run.py).
Standard library only.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

CODE = {'.py', '.sh', '.yaml', '.yml', '.toml', '.cfg'}
PATH_LITERAL = re.compile(r'[\w./-]+\.py$')
CITATION = re.compile(r'<b>([^<]+?)</b>(?:\s*·\s*([A-Za-z_][\w.]*))?')


def git_root(path: Path) -> Path:
    """Top folder of the git repository holding path (path itself if none)."""
    out = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=path, capture_output=True, text=True)
    return Path(out.stdout.strip()) if out.returncode == 0 else path


def files_in(scope: Path) -> list[Path]:
    """Files git can see under scope (tracked + untracked-not-ignored); nested repos included."""
    out = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                         cwd=scope, capture_output=True, text=True).stdout.splitlines()
    found = [scope / f for f in out if (scope / f).is_file()]
    if not found:  # not a git checkout: fall back to a plain walk
        found = [p for p in scope.rglob('*') if p.is_file()]
    return sorted(p for p in found if p.suffix in CODE and '__pycache__' not in p.parts)


def first_line(text: str) -> str:
    """First non-blank line of text, stripped ('' for empty text)."""
    return text.strip().splitlines()[0].strip() if text and text.strip() else ''


def definitions(tree: ast.Module) -> list[str]:
    """Top-level classes (with their methods) and functions of a module, one string each."""
    out = []
    # top-level statements only: nested helpers are not part of the file's surface
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            out.append(f'class {node.name}' + (f'({", ".join(methods)})' if methods else ''))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(f'def {node.name}')
    return out


def imports_and_loads(tree: ast.Module) -> tuple[list[str], list[str]]:
    """Imported module names, and .py paths written as strings (code loaded by file path)."""
    mods, loads = set(), set()
    # every node, so imports and path strings inside functions count too
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            mods.add('.' * node.level + (node.module or ''))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and PATH_LITERAL.match(node.value):
            loads.add(node.value)
    return sorted(mods), sorted(loads)


class FolderScan:
    """Inventory of one code folder, so the agent drawing its figure knows what is there."""

    def __init__(self, scope: Path):
        """Collect the folder's git-visible files and its crowded config folders."""
        self.scope = scope
        self.files = files_in(scope)
        configs: dict[Path, list[Path]] = {}
        # bucket the non-Python files by folder
        for p in self.files:
            if p.suffix != '.py':
                configs.setdefault(p.parent, []).append(p)
        self.crowded = {d: ps for d, ps in configs.items() if len(ps) > 3}

    def lines(self) -> list[str]:
        """All output lines of the inventory, in print order."""
        out = [f'# scope: {self.scope}   (git root: {git_root(self.scope)})', '']
        out += self.group_configs()
        # describe every file not already summarised as part of a crowded config folder
        for path in self.files:
            if path.suffix != '.py' and path.parent in self.crowded:
                continue
            text = path.read_text(errors='replace')
            out += self.describe_python(path, text) if path.suffix == '.py' else [self.describe_other(path, text)]
        return out

    def group_configs(self) -> list[str]:
        """One line per folder holding more than 3 config files, instead of one line per file."""
        return [f'{d.relative_to(self.scope)}/  [{len(ps)} {"/".join(sorted({p.suffix for p in ps}))} files]'
                for d, ps in sorted(self.crowded.items())]

    def describe_other(self, path: Path, text: str) -> str:
        """One line for a shell or config file: path, length, first comment."""
        head = next((l.lstrip('#').strip() for l in text.splitlines()[:15]
                     if l.startswith('#') and not l.startswith('#!')), '')
        n_lines = text.count('\n') + 1
        return f'{path.relative_to(self.scope)}  [{n_lines} lines]  {head}'

    def describe_python(self, path: Path, text: str) -> list[str]:
        """Lines for one Python file: header, definitions, imports, path loads."""
        rel, lines = path.relative_to(self.scope), text.count('\n') + 1
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return [f'{rel}  [{lines} lines]  (syntax error)']
        main = ' ENTRY' if "__name__ == '__main__'" in text or '__name__ == "__main__"' in text else ''
        out = [f'{rel}  [{lines} lines]{main}  {first_line(ast.get_docstring(tree) or "")}']
        out += [f'    {d}' for d in definitions(tree)]
        mods, loads = imports_and_loads(tree)
        local, other = self.split_imports(mods, path)
        if local:
            out.append(f'    imports (local): {", ".join(local)}')
        if other:
            out.append(f'    imports (other): {", ".join(other)}')
        if loads:
            out.append(f'    loads by path:   {", ".join(loads)}')
        return out

    def split_imports(self, mods: list[str], path: Path) -> tuple[list[str], list[str]]:
        """Divide imports into modules found in this folder (or next to the file) and the rest."""
        def is_local(m: str) -> bool:
            """True for a relative import or a module that exists in the folder or beside the file."""
            head = m.split('.')[0]
            return m.startswith('.') or any((d / head).exists() or (d / f'{head}.py').exists()
                                            for d in (self.scope, path.parent))
        local = [m for m in mods if is_local(m)]
        return local, [m for m in mods if m not in local]


def scan(scope: Path) -> None:
    """Print the inventory of one folder (the `scan` command)."""
    print('\n'.join(FolderScan(scope).lines()))


def defined(path: Path, symbol: str) -> bool:
    """True if the file defines symbol: a plain name anywhere, or a dotted Class.method path."""
    try:
        tree = ast.parse(path.read_text(errors='replace'))
    except SyntaxError:
        return False
    parts = symbol.split('.')
    scope = tree.body
    # follow the dotted path one part at a time
    for i, name in enumerate(parts):
        hit = None
        # a plain name may sit at any depth; a dotted part must sit in the previous part's body
        for node in (ast.walk(tree) if i == 0 and len(parts) == 1 else scope):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                hit = node
                break
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                hit = node
                break
        if hit is None:
            return False
        scope = getattr(hit, 'body', [])
    return True


def check(doc: Path) -> int:
    """Report every figure citation whose file or symbol no longer exists; 1 if any, else 0."""
    base = doc.parent
    problems, seen = [], 0
    # every <b>file</b> [· symbol] citation in the page
    for path_text, symbol in CITATION.findall(doc.read_text()):
        if not PATH_LITERAL.match(path_text) and Path(path_text).suffix not in CODE:
            continue  # bold text that is not a file
        seen += 1
        # inside the folder first, then each enclosing folder (files outside the scope)
        target = next((d / path_text for d in (base, *base.parents) if (d / path_text).is_file()), None)
        if target is None:
            problems.append(f'missing file: {path_text}')
        elif symbol and not defined(target, symbol):
            problems.append(f'missing symbol: {path_text} · {symbol}')
    for p in problems:
        print('FAIL', p)
    print(f'CHECK {"PASS" if not problems else "FAIL"} ({seen} citations, {len(problems)} problems)')
    return 1 if problems else 0


def main():
    """Run the scan or check command from the command line."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('scan').add_argument('dir')
    sub.add_parser('check').add_argument('doc')
    args = ap.parse_args()
    if args.command == 'scan':
        scan(Path(args.dir).resolve())
    else:
        sys.exit(check(Path(args.doc).resolve()))


if __name__ == '__main__':
    main()
