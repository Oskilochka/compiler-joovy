from . import globals as g
from .states import initState

def fail():
    if g.state == 101:
        print(f'Lexer: ERROR in line {g.numLine}: unexpected symbol "{g.char}"')
    elif g.state == 102:
        print(f'Lexer: ERROR in line {g.numLine}: operator "!" does not supported, please use "!="')
    else:
        print(f'Lexer: ERROR in line {g.numLine}: lexical error')

    g.errorCount += 1
    g.state = initState
    g.lexeme = ''
