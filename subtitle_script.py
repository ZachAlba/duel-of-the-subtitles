"""Deprecated shim: use `python -m subtitle_toolkit burn ...` instead.

Kept so existing commands keep working. Forwards the old positional/flag
interface to the new CLI's `burn` subcommand.
"""

import sys

from subtitle_toolkit.cli import main

if __name__ == "__main__":
    print("Note: subtitle_script.py is deprecated; use `python -m subtitle_toolkit burn ...`",
          file=sys.stderr)
    sys.exit(main(["burn"] + sys.argv[1:]))
