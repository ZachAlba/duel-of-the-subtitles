"""Deprecated shim: use `python -m subtitle_toolkit shift|combine ...` instead.

Kept so existing commands keep working. The old subcommand names match the
new CLI's, so arguments forward unchanged.
"""

import sys

from subtitle_toolkit.cli import main

if __name__ == "__main__":
    print("Note: vtt_adjuster.py is deprecated; use `python -m subtitle_toolkit shift|combine ...`",
          file=sys.stderr)
    sys.exit(main(sys.argv[1:]))
