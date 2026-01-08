import sys
from .lexer import start
from . import globals as g

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use: python -m lexer.main <file.joovy>")
        sys.exit(1)

    start(sys.argv[1])

    if g.errorCount > 0:
        print(f'\nLexer: found {g.errorCount} errors')
        sys.exit(1)
