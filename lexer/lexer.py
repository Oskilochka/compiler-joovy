from .utils import *
from .tables import *
from .states import *
from .errors import *

def classOfChar(ch):
    if ch in '.':
        return "dot"
    elif ch in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
        return "Letter"
    elif ch in "0123456789":
        return "Digit"
    elif ch in " \t":
        return "ws"
    elif ch in "\n":
        return "nl"
    elif ch == ':':
        return ":"
    elif ch == '=':
        return "="
    elif ch == '/':
        return "/"
    elif ch == '"':
        return "dquote"
    elif ch in "+-*^(){}[],;":
        return ch
    elif ch in "<>!":
        return ch
    elif ch in 'eE':
        return "exp"
    else:
        return 'other'

def nextState(st, classCh):
    try:
        return stf[(st, classCh)]
    except KeyError:
        return stf.get((st, 'other'), 101)

def getToken(st, lex):
    if lex in tokenTable:
        return tokenTable[lex]
    elif st in tokStateTable:
        return tokStateTable[st]
    else:
        return 'UNKNOWN'

def indexIdConst(st, lex):
    if st == 2:
        if lex not in g.tableOfId:
            g.tableOfId[lex] = len(g.tableOfId) + 1
        return g.tableOfId[lex]
    elif st in (13, 14, 9, 41):
        if lex not in g.tableOfConst:
            g.tableOfConst[lex] = len(g.tableOfConst) + 1
        return g.tableOfConst[lex]
    return -1

def processing():
    # New line processing
    if g.state == 50:
        g.numLine += 1
        g.state = initState
        return

    #  Comments processing
    if g.state == 33:
        g.numLine += 1
        g.lexeme = ''
        g.state = initState
        return

    # Identifiers and const
    if g.state in (2, 9, 13, 14):
        token = getToken(g.state, g.lexeme)

        # Key word check
        if g.lexeme in tokenTable and token in ('KEYWORD', 'TYPE', 'BOOL'):
            print(f'{g.numLine:<4d} {g.lexeme:<15s} {token:<15s}')
            g.tableOfSymb[len(g.tableOfSymb) + 1] = (g.numLine, g.lexeme, token, '')
        else:
            # Identifiers and const
            index = indexIdConst(g.state, g.lexeme)
            print(f'{g.numLine:<4d} {g.lexeme:<15s} {token:<15s} {index:<5d}')
            g.tableOfSymb[len(g.tableOfSymb) + 1] = (g.numLine, g.lexeme, token, index)

        g.lexeme = ''
        if g.state in Fstar:
            putCharBack()
        g.state = initState

    # String literals
    elif g.state == 41:
        # Closed " for lexeme
        full_lexeme = '"' + g.lexeme + '"'
        token = 'STRING'
        index = indexIdConst(g.state, full_lexeme)
        print(f'{g.numLine:<4d} {full_lexeme:<15s} {token:<15s} {index:<5d}')
        g.tableOfSymb[len(g.tableOfSymb) + 1] = (g.numLine, full_lexeme, token, index)
        g.lexeme = ''
        g.state = initState

    # Operators (1 - 2 symbols )
    elif g.state in (21, 22, 24, 26, 27, 29, 30, 34, 51, 52, 53):
        if g.state not in (22, 27, 30, 34):
            g.lexeme += g.char

        token = getToken(g.state, g.lexeme)
        print(f'{g.numLine:<4d} {g.lexeme:<15s} {token:<15s}')
        g.tableOfSymb[len(g.tableOfSymb) + 1] = (g.numLine, g.lexeme, token, '')

        g.lexeme = ''
        if g.state in Fstar:
            putCharBack()
        g.state = initState

    # Errors
    elif g.state in Ferror:
        fail()

def lexer_main():
    print(f'{"Line":<4s} {"Lexeme":<15s} {"Token":<15s} {"Index":<5s}')
    print('-' * 50)

    try:
        while g.numChar < g.lenCode - 1:
            g.char = nextChar()
            classCh = classOfChar(g.char)
            g.state = nextState(g.state, classCh)

            if is_final(g.state, F):
                processing()
            elif g.state == initState:
                g.lexeme = ''
            else:
                g.lexeme += g.char

        print('\n' + '=' * 50)
        if g.errorCount == 0:
            print('Lexer: Lexical analysis completed SUCCESSFULLY')
            g.FSuccess = ('Lexer', True)
        else:
            print(f'Lexer: Lexical analysis completed with {g.errorCount} errors')
            g.FSuccess = ('Lexer', False)

    except SystemExit as e:
        print('\n' + '=' * 50)
        print(f'Lexer: Crashing the program with code {e}')
        g.FSuccess = ('Lexer', False)

def start(file_path):
    # Resetting global variables
    g.numLine = 1
    g.numChar = -1
    g.state = 0
    g.lexeme = ""
    g.char = ""
    g.tableOfSymb = {}
    g.tableOfId = {}
    g.tableOfConst = {}
    g.errorCount = 0
    g.FSuccess = None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            g.sourceCode = f.read()
            g.lenCode = len(g.sourceCode)
    except FileNotFoundError:
        print(f'ERROR: File "{file_path}" not found')
        return False

    print(f'\n{"=" * 60}')
    print(f'Lexical analysis of the file: {file_path}')
    print(f'{"=" * 60}\n')

    lexer_main()

    print('\n' + '=' * 50)
    print('DISASSEMBLY TABLE:')
    print(f'{"№":<4s} {"Line":<7s} {"Lexeme":<15s} {"Token":<15s} {"Index":<5s}')
    print('-' * 50)
    for num, (line, lex, tok, idx) in g.tableOfSymb.items():
        idx_str = str(idx) if idx != '' else ''
        print(f'{num:<4d} {line:<7d} {lex:<15s} {tok:<15s} {idx_str:<5s}')

    print('\n' + '=' * 50)
    print('TABLE OF IDENTIFIERS:')
    print(f'{"Identifier":<20s} {"Index":<5s}')
    print('-' * 30)
    for ident, idx in g.tableOfId.items():
        print(f'{ident:<20s} {idx:<5d}')

    print('\n' + '=' * 50)
    print('TABLE OF CONST:')
    print(f'{"Const":<20s} {"Index":<5s}')
    print('-' * 30)
    for const, idx in g.tableOfConst.items():
        print(f'{const:<20s} {idx:<5d}')

    return g.FSuccess[1] if g.FSuccess else False
