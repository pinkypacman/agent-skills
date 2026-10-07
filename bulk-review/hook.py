#!/usr/bin/env python3
"""PostToolUse hook: after Claude edits a .py file, measure it and report bulk back to Claude.

Never blocks. Compares with the last commit (HEAD) and reports only what the edit made worse;
a file git does not know yet is reported in full. Prints nothing when there is nothing to report.
Wire it as  python3 <this file>  on Edit|Write|MultiEdit.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure  # noqa: E402


def main():
    """Read the hook event, measure the edited .py file, print a report only if needed."""
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    path = Path((event.get('tool_input') or {}).get('file_path') or '')
    if path.suffix != '.py' or not path.is_file():
        return
    report = io.StringIO()
    with contextlib.redirect_stdout(report):
        flagged = measure.report(path, measure.LIMITS, show_all=False, since='HEAD')
    if flagged:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'bulk-review: this edit made code worse past the readability limits.\n'
                                 + report.getvalue()
                                 + 'Use the bulk-review skill: give each item a verdict (real or harmless) '
                                   'and, for real ones, offer the refactor branch. Frozen code is report-only.'}}))


if __name__ == '__main__':
    main()
