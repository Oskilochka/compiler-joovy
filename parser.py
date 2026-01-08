from lexer.lexer import start as lex_start
from lexer import globals as g

tableOfSymb = {}      # Character table from lexer
numRow = 0            # Current record number in the table
len_tableOfSymb = 0   # Total number of records
indent_level = 0      # Indentation level for output
step_indent = 2       # Step indentation


# Helpers

def nextIndent():
    # Increases indentation
    global indent_level
    indent_level += step_indent
    return ' ' * indent_level


def prevIndent():
    # Decreases indentation
    global indent_level
    indent_level -= step_indent
    return ' ' * indent_level


def getSymb():
    # Gets the current entry from the character table
    global numRow, tableOfSymb
    if numRow <= len_tableOfSymb:
        numLine, lexeme, token, _ = tableOfSymb[numRow]
        return numLine, lexeme, token
    return None, None, None


def nextSymb():
    # Moves to the next character
    global numRow
    numRow += 1


# Errors processing
def failParse(error_type, info):
    if error_type == 'unexpected_end':
        expected = info
        print(f'\nParser ERROR: Unexpected program end.')
        print(f'  Expected: {expected}')

    elif error_type == 'token_mismatch':
        numLine, found_lex, found_tok, exp_lex, exp_tok = info
        print(f'\nParser ERROR: In line {numLine}')
        print(f'  Found: ({found_lex}, {found_tok})')
        print(f'  Expected: ({exp_lex}, {exp_tok})')

    elif error_type == 'unexpected_token':
        numLine, lex, tok, expected = info
        print(f'\nParser ERROR: In line {numLine}')
        print(f'  Unexpected token: ({lex}, {tok})')
        print(f'  Expected: {expected}')

    elif error_type == 'invalid_statement':
        numLine, lex, tok = info
        print(f'\nParser ERROR: In line {numLine}')
        print(f'  Incorrect instruction: ({lex}, {tok})')
        print(f'  Expected: variable declaration, function or instruction')

    else:
        print(f'\nParser ERROR: {error_type}')
        print(f'  Information: {info}')

    raise SystemExit(1)


# Parser function
def parseToken(expected_lex, expected_tok):
    # Checks whether the current token matches the expected one
    global numRow

    indent = nextIndent()

    # Checking the end of the table
    if numRow > len_tableOfSymb:
        failParse('unexpected_end', (expected_lex, expected_tok))

    numLine, lex, tok = getSymb()

    if (lex, tok) == (expected_lex, expected_tok):
        print(f'{indent}✓ Line {numLine}: ({lex}, {tok})')
        nextSymb()
        prevIndent()
        return True
    else:
        failParse('token_mismatch', (numLine, lex, tok, expected_lex, expected_tok))

def parseProgram():
    # Program = {Declaration | Statement}
    indent = nextIndent()
    print(f'{indent}parseProgram()')

    # A program is a sequence of statements and instructions.
    while numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()

        # End of program
        if numLine is None:
            break

        # Variable declaration
        if tok == 'TYPE':
            parseVarDecl()

        # Constant declaration
        elif lex == 'const' and tok == 'KEYWORD':
            parseConstDecl()

        # Function declaration
        elif lex == 'def' and tok == 'KEYWORD':
            parseFuncDecl()

        # Інструкції
        elif tok == 'IDENTIFIER' or lex in ('if', 'for', 'print', 'input', 'return') or lex == '{':
            parseStatement()

        else:
            # Unknown element - end of program
            break

    prevIndent()
    return True

def parseVarDecl():
    #  VarDecl = Type Ident ['=' Expression] {',' Ident ['=' Expression]}
    indent = nextIndent()
    print(f'{indent}parseVarDecl()')

    # Type
    numLine, lex, tok = getSymb()
    if tok != 'TYPE':
        failParse('unexpected_token', (numLine, lex, tok, 'TYPE'))
    print(f'{indent}  Type: {lex}')
    nextSymb()

    # Ident
    numLine, lex, tok = getSymb()
    if tok != 'IDENTIFIER':
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
    print(f'{indent}  Ident: {lex}')
    nextSymb()

    # ['=' Expression]
    numLine, lex, tok = getSymb()
    if lex == '=' and tok == 'ASSIGN_OP':
        nextSymb()
        parseExpression()

    # {',' Ident ['=' Expression]}
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'COMMA':
            nextSymb()

            # Ident
            numLine, lex, tok = getSymb()
            if tok != 'IDENTIFIER':
                failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
            print(f'{indent}  Ident: {lex}')
            nextSymb()

            # ['=' Expression]
            numLine, lex, tok = getSymb()
            if lex == '=' and tok == 'ASSIGN_OP':
                nextSymb()
                parseExpression()
        else:
            break

    prevIndent()
    return True


def parseConstDecl():
    #  ConstDecl = 'const' Type Ident '=' Const {',' Ident '=' Const}
    indent = nextIndent()
    print(f'{indent}parseConstDecl()')

    parseToken('const', 'KEYWORD')

    # Type
    numLine, lex, tok = getSymb()
    if tok != 'TYPE':
        failParse('unexpected_token', (numLine, lex, tok, 'TYPE'))
    print(f'{indent}  Type: {lex}')
    nextSymb()

    # Ident
    numLine, lex, tok = getSymb()
    if tok != 'IDENTIFIER':
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
    print(f'{indent}  Ident: {lex}')
    nextSymb()

    parseToken('=', 'ASSIGN_OP')

    # Const
    numLine, lex, tok = getSymb()
    if tok not in ('INT', 'FLOAT', 'BOOL', 'STRING'):
        failParse('unexpected_token', (numLine, lex, tok, 'CONST'))
    print(f'{indent}  Const: {lex}')
    nextSymb()

    # {',' Ident '=' Const}
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'COMMA':
            nextSymb()

            # Ident
            numLine, lex, tok = getSymb()
            if tok != 'IDENTIFIER':
                failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
            print(f'{indent}  Ident: {lex}')
            nextSymb()

            parseToken('=', 'ASSIGN_OP')

            # Const
            numLine, lex, tok = getSymb()
            if tok not in ('INT', 'FLOAT', 'BOOL', 'STRING'):
                failParse('unexpected_token', (numLine, lex, tok, 'CONST'))
            print(f'{indent}  Const: {lex}')
            nextSymb()
        else:
            break

    prevIndent()
    return True


def parseFuncDecl():
    # FuncDecl = 'def' Ident '(' [ParamList] ')' Block
    indent = nextIndent()
    print(f'{indent}parseFuncDecl()')

    parseToken('def', 'KEYWORD')

    # Ident
    numLine, lex, tok = getSymb()
    if tok != 'IDENTIFIER':
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
    print(f'{indent}  Function: {lex}')
    nextSymb()

    parseToken('(', 'PAR_OP')

    # [ParamList]
    numLine, lex, tok = getSymb()
    if tok == 'IDENTIFIER':
        parseParamList()

    parseToken(')', 'PAR_OP')
    parseBlock()

    prevIndent()
    return True

def parseParamList():
    #  ParamList = Ident {',' Ident}
    indent = nextIndent()
    print(f'{indent}parseParamList()')

    # Ident
    numLine, lex, tok = getSymb()
    if tok != 'IDENTIFIER':
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
    print(f'{indent}  Param: {lex}')
    nextSymb()

    # {',' Ident}
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'COMMA':
            nextSymb()

            numLine, lex, tok = getSymb()
            if tok != 'IDENTIFIER':
                failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
            print(f'{indent}  Param: {lex}')
            nextSymb()
        else:
            break

    prevIndent()
    return True

def parseStatement():
    # Statement = VarDecl | ConstDecl | Assignment | IfStatement | ForLoop | PrintStmt | InputStmt | ReturnStmt | FuncCall | Block
    indent = nextIndent()
    print(f'{indent}parseStatement()')

    numLine, lex, tok = getSymb()

    # VarDecl
    if tok == 'TYPE':
        parseVarDecl()

    # ConstDecl -
    elif lex == 'const' and tok == 'KEYWORD':
        parseConstDecl()

    # Assignment or FuncCall
    elif tok == 'IDENTIFIER':
        # Look ahead
        saved_row = numRow
        nextSymb()
        numLine2, lex2, tok2 = getSymb()
        numRow = saved_row

        if lex2 == '=' and tok2 == 'ASSIGN_OP':
            parseAssignment()
        elif lex2 == '(' and tok2 == 'PAR_OP':
            parseFuncCall()
        else:
            failParse('unexpected_token', (numLine, lex, tok, '= або ('))

    # IfStatement
    elif lex == 'if' and tok == 'KEYWORD':
        parseIfStatement()

    # ForLoop
    elif lex == 'for' and tok == 'KEYWORD':
        parseForLoop()

    # PrintStmt
    elif lex == 'print' and tok == 'KEYWORD':
        parsePrintStmt()

    # InputStmt
    elif lex == 'input' and tok == 'KEYWORD':
        parseInputStmt()

    # ReturnStmt
    elif lex == 'return' and tok == 'KEYWORD':
        parseReturnStmt()

    # Block
    elif lex == '{' and tok == 'PAR_OP':
        parseBlock()

    else:
        failParse('invalid_statement', (numLine, lex, tok))

    prevIndent()
    return True

def parseAssignment():
    #  Assignment = Ident '=' Expression
    indent = nextIndent()
    print(f'{indent}parseAssignment()')

    # Ident
    numLine, lex, tok = getSymb()
    print(f'{indent}  Ident: {lex}')
    nextSymb()

    parseToken('=', 'ASSIGN_OP')
    parseExpression()

    prevIndent()
    return True

def parseIfStatement():
    #  IfStatement = 'if' '(' Expression ')' Block ['else' Block]
    indent = nextIndent()
    print(f'{indent}parseIfStatement()')

    parseToken('if', 'KEYWORD')
    parseToken('(', 'PAR_OP')
    parseExpression()
    parseToken(')', 'PAR_OP')
    parseBlock()

    # ['else' Block]
    numLine, lex, tok = getSymb()
    if lex == 'else' and tok == 'KEYWORD':
        parseToken('else', 'KEYWORD')
        parseBlock()

    prevIndent()
    return True

def parseForLoop():
    """
    ForLoop = 'for' '(' Ident 'in' RangeStart '..' RangeEnd ')' Block

    IMPORTANT: Lexer recognizes '1..5' in different ways:
    - Case 1: '1' '.' '.' '5' (INT, DOT, DOT, INT)
    - Case 2: '1.' '.5' (FLOAT, FLOAT) - dots stick to numbers

    Handle both cases by accepting any combination of numbers and dots
    """
    indent = nextIndent()
    print(f'{indent}parseForLoop()')

    parseToken('for', 'KEYWORD')
    parseToken('(', 'PAR_OP')

    # Ident (loop counter)
    numLine, lex, tok = getSymb()
    if tok != 'IDENTIFIER':
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
    print(f'{indent}  Iterator: {lex}')
    nextSymb()

    parseToken('in', 'KEYWORD')

    # Range start (can be INT or FLOAT like "1." or just "1")
    numLine, lex, tok = getSymb()
    if tok not in ('INT', 'FLOAT'):
        failParse('unexpected_token', (numLine, lex, tok, 'range start (number)'))

    start_value = lex
    print(f'{indent}  Range start: {lex}')
    nextSymb()

    # Range operator ".."
    # Can be represented as:
    # - Two DOT tokens (if it was "1..5")
    # - No DOTs (if lexer made "1." and ".5")
    # - One DOT (if it was "1." and then ".5")

    # Skip all DOT tokens until we find a number
    dot_count = 0
    while True:
        numLine, lex, tok = getSymb()
        if lex == '.' and tok == 'DOT':
            dot_count += 1
            nextSymb()
        else:
            break

    # If start was integer and we have no dots - that's wrong
    # If start was float (1.) and we have dots - that's the range operator
    # Accept any combination with at least context making sense

    # Range end (can be INT or FLOAT like ".5" or just "5")
    numLine, lex, tok = getSymb()
    if tok not in ('INT', 'FLOAT'):
        failParse('unexpected_token', (numLine, lex, tok, 'range end (number)'))

    end_value = lex
    print(f'{indent}  Range end: {lex}')
    nextSymb()

    parseToken(')', 'PAR_OP')
    parseBlock()

    prevIndent()
    return True

def parsePrintStmt():
    # PrintStmt = 'print' '(' [ExprList] ')'
    indent = nextIndent()
    print(f'{indent}parsePrintStmt()')

    parseToken('print', 'KEYWORD')
    parseToken('(', 'PAR_OP')

    # [ExprList]
    numLine, lex, tok = getSymb()
    if lex != ')':
        parseExprList()

    parseToken(')', 'PAR_OP')

    prevIndent()
    return True

def parseInputStmt():
    #  InputStmt = 'input' '(' Ident ')'
    indent = nextIndent()
    print(f'{indent}parseInputStmt()')

    parseToken('input', 'KEYWORD')
    parseToken('(', 'PAR_OP')

    # Ident
    numLine, lex, tok = getSymb()
    if tok != 'IDENTIFIER':
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER'))
    print(f'{indent}  Ident: {lex}')
    nextSymb()

    parseToken(')', 'PAR_OP')

    prevIndent()
    return True

def parseReturnStmt():
    # ReturnStmt = 'return' [Expression]
    indent = nextIndent()
    print(f'{indent}parseReturnStmt()')

    parseToken('return', 'KEYWORD')

    # [Expression]
    numLine, lex, tok = getSymb()
    # If not the end of the block - there is an expression
    if lex != '}' and tok != 'PAR_OP':
        parseExpression()

    prevIndent()
    return True

def parseBlock():
    # Block = '{' {Statement} '}'
    indent = nextIndent()
    print(f'{indent}parseBlock()')

    parseToken('{', 'PAR_OP')

    # {Statement}
    while True:
        numLine, lex, tok = getSymb()
        if lex == '}' and tok == 'PAR_OP':
            break
        parseStatement()

    parseToken('}', 'PAR_OP')

    prevIndent()
    return True

def parseExprList():
    #  ExprList = Expression {',' Expression}
    indent = nextIndent()
    print(f'{indent}parseExprList()')

    parseExpression()

    # {',' Expression}
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'COMMA':
            nextSymb()
            parseExpression()
        else:
            break

    prevIndent()
    return True

def parseExpression():
    # Expression = CompareExpr
    indent = nextIndent()
    print(f'{indent}parseExpression()')

    parseCompareExpr()

    prevIndent()
    return True

def parseCompareExpr():
    # CompareExpr = ArithExpr [RelOp ArithExpr]
    indent = nextIndent()
    print(f'{indent}parseCompareExpr()')

    parseArithExpr()

    # [RelOp ArithExpr]
    numLine, lex, tok = getSymb()
    if tok == 'COMPARE_OP':
        print(f'{indent}  RelOp: {lex}')
        nextSymb()
        parseArithExpr()

    prevIndent()
    return True

def parseArithExpr():
    # ArithExpr = Term {AddOp Term}
    indent = nextIndent()
    print(f'{indent}parseArithExpr()')

    parseTerm()

    # {AddOp Term}
    while True:
        numLine, lex, tok = getSymb()
        if tok == 'ADD_OP':
            print(f'{indent}  AddOp: {lex}')
            nextSymb()
            parseTerm()
        else:
            break

    prevIndent()
    return True

def parseTerm():
    # Term = Power {MultOp Power}
    indent = nextIndent()
    print(f'{indent}parseTerm()')

    parsePower()

    # {MultOp Power}
    while True:
        numLine, lex, tok = getSymb()
        if tok == 'MULT_OP':
            print(f'{indent}  MultOp: {lex}')
            nextSymb()
            parsePower()
        else:
            break

    prevIndent()
    return True

def parsePower():
    # Power = Factor {'^' Factor}
    indent = nextIndent()
    print(f'{indent}parsePower()')

    parseFactor()

    # {'^' Factor}
    while True:
        numLine, lex, tok = getSymb()
        if lex == '^' and tok == 'POWER_OP':
            print(f'{indent}  PowerOp: ^')
            nextSymb()
            parseFactor()
        else:
            break

    prevIndent()
    return True

def parseFactor():
    # Factor = [Sign] Primary
    indent = nextIndent()
    print(f'{indent}parseFactor()')

    # [Sign]
    numLine, lex, tok = getSymb()
    if tok == 'ADD_OP' and lex in ('+', '-'):
        print(f'{indent}  UnaryOp: {lex}')
        nextSymb()

    parsePrimary()

    prevIndent()
    return True

def parsePrimary():
    # Primary = Ident | Const | FuncCall | '(' Expression ')'
    indent = nextIndent()
    print(f'{indent}parsePrimary()')

    numLine, lex, tok = getSymb()

    # Const
    if tok in ('INT', 'FLOAT', 'BOOL', 'STRING'):
        print(f'{indent}  Const: {lex}')
        nextSymb()

    # Ident або FuncCall
    elif tok == 'IDENTIFIER':
        print(f'{indent}  Ident: {lex}')
        nextSymb()

        # Перевірка на FuncCall
        numLine2, lex2, tok2 = getSymb()
        if lex2 == '(' and tok2 == 'PAR_OP':
            parseToken('(', 'PAR_OP')

            # [ArgList]
            numLine3, lex3, tok3 = getSymb()
            if lex3 != ')':
                parseArgList()

            parseToken(')', 'PAR_OP')

    # '(' Expression ')'
    elif lex == '(' and tok == 'PAR_OP':
        parseToken('(', 'PAR_OP')
        parseExpression()
        parseToken(')', 'PAR_OP')

    else:
        failParse('unexpected_token', (numLine, lex, tok, 'IDENTIFIER, CONST або ('))

    prevIndent()
    return True

def parseFuncCall():
    # FuncCall = Ident '(' [ArgList] ')'
    indent = nextIndent()
    print(f'{indent}parseFuncCall()')

    # Ident
    numLine, lex, tok = getSymb()
    print(f'{indent}  Function: {lex}')
    nextSymb()

    parseToken('(', 'PAR_OP')

    # [ArgList]
    numLine, lex, tok = getSymb()
    if lex != ')':
        parseArgList()

    parseToken(')', 'PAR_OP')

    prevIndent()
    return True

def parseArgList():
    # ArgList = Expression {',' Expression}
    indent = nextIndent()
    print(f'{indent}parseArgList()')

    parseExpression()

    # {',' Expression}
    while True:
        numLine, lex, tok = getSymb()
        if lex == ',' and tok == 'COMMA':
            nextSymb()
            parseExpression()
        else:
            break

    prevIndent()
    return True

# Parser
def parse(table_of_symb):
    global tableOfSymb, numRow, len_tableOfSymb, indent_level

    tableOfSymb = table_of_symb
    numRow = 1
    len_tableOfSymb = len(tableOfSymb)
    indent_level = 0

    print('\n' + '=' * 60)
    print('Syntax analysis')
    print('=' * 60 + '\n')

    try:
        parseProgram()
        print('\n' + '=' * 60)
        print('✓ Parser: Parsing completed SUCCESSFULLY')
        print('=' * 60)
        return True

    except SystemExit as e:
        print('\n' + '=' * 60)
        print(f'✗ Parser: Crash with code {e}')
        print('=' * 60)
        return False

def start(file_path):
    # Runs lexical and syntactic analysis of the file
    lex_success = lex_start(file_path)

    if not lex_success:
        print('\n✗ Lexical analysis failed. Syntactic analysis is not possible..')
        return False

    if g.errorCount > 0:
        print(f'\n✗ Found {g.errorCount} lexical errors. Syntactic analysis is not possible.')
        return False

    return parse(g.tableOfSymb)
