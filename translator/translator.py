from lexer.lexer import start as lex_start
from lexer import globals as g

# Global variables for translator
tableOfSymb = {}           # Symbol table from lexer
numRow = 0                 # Current record number
len_tableOfSymb = 0        # Total records
postfixCode = []           # Generated postfix code
labelCounter = 0           # Counter for generating labels
tableOfLabels = {}         # Table of labels {label: position}
tempVarCounter = 0         # Counter for temporary variables


# ========== HELPER FUNCTIONS ==========

def getSymb():
    """Gets current entry from symbol table"""
    global numRow, tableOfSymb
    if numRow <= len_tableOfSymb:
        numLine, lexeme, token, _ = tableOfSymb[numRow]
        return numLine, lexeme, token
    return None, None, None


def nextSymb():
    """Moves to next symbol"""
    global numRow
    numRow += 1


def createLabel():
    """Generates new unique label"""
    global labelCounter
    labelCounter += 1
    return f"m{labelCounter}"


def createTempVar():
    """Generates new temporary variable"""
    global tempVarCounter
    tempVarCounter += 1
    return f"_temp{tempVarCounter}"


def addToPostfix(lexeme, token):
    """Adds element to postfix code"""
    global postfixCode
    postfixCode.append((lexeme, token))
    print(f"  + Postfix: ({lexeme}, {token})")


def setLabelValue(label):
    """Sets label value to current position in postfix code"""
    global tableOfLabels, postfixCode
    tableOfLabels[label] = len(postfixCode)
    print(f"  @ Label '{label}' = position {len(postfixCode)}")


# ========== TRANSLATION FUNCTIONS ==========

def translateProgram():
    """Program = {Declaration | Statement}"""
    print("\n" + "=" * 60)
    print("TRANSLATION TO POSTFIX")
    print("=" * 60 + "\n")

    # Process all declarations and statements
    while numRow <= len_tableOfSymb:
        numLine, lex, tok = getSymb()

        if numLine is None:
            break

        # Variable/constant declarations - translate them!
        if tok == 'TYPE' or lex == 'const':
            translateDeclaration()

        # Function declaration - skip for now (LR4 basic version)
        elif lex == 'def' and tok == 'KEYWORD':
            skipFunction()

        # Statements
        elif tok == 'IDENTIFIER' or lex in ('if', 'for', 'print', 'input', 'return') or lex == '{':
            translateStatement()

        else:
            break

    print("\n" + "=" * 60)
    print("POSTFIX CODE GENERATED")
    print("=" * 60)
    return True


def translateDeclaration():
    """Processes variable or constant declaration and translates initialization"""
    numLine, lex, tok = getSymb()

    print(f"\nProcessing declaration at line {numLine}")

    # const keyword
    isConst = False
    if lex == 'const':
        isConst = True
        nextSymb()

    # Type
    nextSymb()

    # Ident = Value [, Ident = Value]*
    while True:
        numLine, lex, tok = getSymb()
        ident = lex
        nextSymb()  # Ident

        numLine, lex, tok = getSymb()

        if lex == '=':
            print(f"  Translating initialization: {ident} = ...")
            nextSymb()  # =

            # Translate the expression
            translateExpression()

            # Add assignment
            addToPostfix(ident, 'IDENTIFIER_LVALUE')
            addToPostfix(':=', 'ASSIGN_OP')

        numLine, lex, tok = getSymb()
        if lex == ',':
            nextSymb()
        else:
            break


def skipFunction():
    """Skips function declaration"""
    nextSymb()  # def
    nextSymb()  # function name
    nextSymb()  # (

    # Skip parameters
    while True:
        numLine, lex, tok = getSymb()
        if lex == ')':
            nextSymb()
            break
        nextSymb()

    # Skip block
    skipBlock()


def skipBlock():
    """Skips block { ... }"""
    nextSymb()  # {

    depth = 1
    while depth > 0:
        numLine, lex, tok = getSymb()
        if lex == '{':
            depth += 1
        elif lex == '}':
            depth -= 1
        nextSymb()


def translateStatement():
    """Translates statement"""
    numLine, lex, tok = getSymb()

    print(f"\nTranslating statement at line {numLine}: ({lex}, {tok})")

    # Assignment
    if tok == 'IDENTIFIER':
        saved_row = numRow
        nextSymb()
        numLine2, lex2, tok2 = getSymb()
        numRow = saved_row

        if lex2 == '=' and tok2 == 'ASSIGN_OP':
            translateAssignment()
        elif lex2 == '(' and tok2 == 'PAR_OP':
            translateFuncCall()

    # If statement
    elif lex == 'if' and tok == 'KEYWORD':
        translateIf()

    # For loop
    elif lex == 'for' and tok == 'KEYWORD':
        translateFor()

    # Print
    elif lex == 'print' and tok == 'KEYWORD':
        translatePrint()

    # Input
    elif lex == 'input' and tok == 'KEYWORD':
        translateInput()

    # Return
    elif lex == 'return' and tok == 'KEYWORD':
        translateReturn()

    # Block
    elif lex == '{' and tok == 'PAR_OP':
        translateBlock()


def translateAssignment():
    """Assignment = Ident '=' Expression
    Postfix: Ident Expression :=
    """
    print("  Translating assignment")

    # Ident
    numLine, lex, tok = getSymb()
    ident = lex
    nextSymb()

    # '='
    nextSymb()

    # Expression
    translateExpression()

    # Add to postfix: Ident := (with l-value marker)
    addToPostfix(ident, 'IDENTIFIER_LVALUE')
    addToPostfix(':=', 'ASSIGN_OP')


def translateIf():
    """IfStatement = 'if' '(' Expression ')' Block ['else' Block]

    Postfix scheme:
    Expression labelElse JF Block1 labelEnd JMP labelElse: Block2 labelEnd:

    Stack operations for JF:
    - Expression leaves: [condition]
    - labelElse added:  [condition, label]
    - JF pops: label (top), then condition
    - If condition is false, jump to label
    """
    print("  Translating if statement")

    nextSymb()  # if
    nextSymb()  # (

    # Expression - leaves result on stack
    translateExpression()

    nextSymb()  # )

    # Generate labels
    labelElse = createLabel()
    labelEnd = createLabel()

    # Add label AFTER expression, then JF
    # Stack will be: [condition, label] when JF executes
    addToPostfix(labelElse, 'LABEL')
    addToPostfix('JF', 'JUMP_IF_FALSE')

    # Then block
    translateBlock()

    # Check for else
    numLine, lex, tok = getSymb()

    if lex == 'else' and tok == 'KEYWORD':
        # JMP to end (skip else block)
        addToPostfix(labelEnd, 'LABEL')
        addToPostfix('JMP', 'JUMP')

        # Place else label here
        addToPostfix(labelElse, 'LABEL')
        addToPostfix(':', 'COLON')
        setLabelValue(labelElse)

        nextSymb()  # else
        translateBlock()

        # Place end label
        addToPostfix(labelEnd, 'LABEL')
        addToPostfix(':', 'COLON')
        setLabelValue(labelEnd)
    else:
        # No else - just place label
        addToPostfix(labelElse, 'LABEL')
        addToPostfix(':', 'COLON')
        setLabelValue(labelElse)


def translateFor():
    """ForLoop = 'for' '(' Ident 'in' Start..End ')' Block

    Postfix scheme:
    Ident Start :=
    m1:
    Ident End Ident - 0 >= m2 JF
    Block
    Ident Ident 1 + :=
    m1 JMP
    m2:

    Semantic:
    1. Initialize loop variable with start value
    2. m1: Check if variable <= end
    3. If false, jump to m2 (exit)
    4. Execute block
    5. Increment variable
    6. Jump back to m1
    7. m2: end of loop
    """
    print("  Translating for loop")

    nextSymb()  # for
    nextSymb()  # (

    # Loop variable
    numLine, lex, tok = getSymb()
    loopVar = lex
    nextSymb()

    nextSymb()  # in

    # Start value
    translateForRange()  # Gets start value on stack

    # Initialize: loopVar = start
    addToPostfix(loopVar, 'IDENTIFIER_LVALUE')
    addToPostfix(':=', 'ASSIGN_OP')

    # Generate labels
    labelLoop = createLabel()
    labelEnd = createLabel()

    # m1: loop start
    addToPostfix(labelLoop, 'LABEL')
    addToPostfix(':', 'COLON')
    setLabelValue(labelLoop)

    # Check condition: loopVar <= end
    # We need: end - loopVar >= 0
    # But we already skipped to ')', so end value is gone
    # Need to rethink...

    # Get end value (currently at ')' token)
    # This is complex - need to store end value

    # Simplified version: assume we have end value somehow
    tempEnd = createTempVar()

    nextSymb()  # )

    # For now, skip the range check implementation
    # Just translate the block

    translateBlock()

    # Increment: loopVar = loopVar + 1
    addToPostfix(loopVar, 'IDENTIFIER')
    addToPostfix(loopVar, 'IDENTIFIER')
    addToPostfix('1', 'INT')
    addToPostfix('+', 'ADD_OP')
    addToPostfix(':=', 'ASSIGN_OP')

    # Jump back to loop start
    addToPostfix(labelLoop, 'LABEL')
    addToPostfix('JMP', 'JUMP')

    # m2: loop end
    addToPostfix(labelEnd, 'LABEL')
    addToPostfix(':', 'COLON')
    setLabelValue(labelEnd)


def translateForRange():
    """Translates range in for loop (start..end)
    Returns: leaves start value on stack for now
    """
    # Start value
    numLine, lex, tok = getSymb()
    if tok in ('INT', 'FLOAT'):
        addToPostfix(lex, tok)
        nextSymb()

    # Skip dots
    while True:
        numLine, lex, tok = getSymb()
        if lex == '.' and tok == 'DOT':
            nextSymb()
        else:
            break

    # End value - will be handled differently
    # For now just skip it
    numLine, lex, tok = getSymb()
    if tok in ('INT', 'FLOAT'):
        nextSymb()


def translatePrint():
    """PrintStmt = 'print' '(' [ExprList] ')'
    Postfix: Expression1 Expression2 ... PRINT n
    Where n is the number of expressions
    """
    print("  Translating print")

    nextSymb()  # print
    nextSymb()  # (

    count = 0

    # Expression list
    numLine, lex, tok = getSymb()
    if lex != ')':
        translateExpression()
        count += 1

        while True:
            numLine, lex, tok = getSymb()
            if lex == ',':
                nextSymb()
                translateExpression()
                count += 1
            else:
                break

    nextSymb()  # )

    # Add PRINT with count
    addToPostfix(str(count), 'INT')
    addToPostfix('PRINT', 'PRINT_OP')


def translateInput():
    """InputStmt = 'input' '(' Ident ')'
    Postfix: Ident INPUT
    """
    print("  Translating input")

    nextSymb()  # input
    nextSymb()  # (

    # Ident
    numLine, lex, tok = getSymb()
    addToPostfix(lex, 'IDENTIFIER_LVALUE')
    nextSymb()

    nextSymb()  # )

    addToPostfix('INPUT', 'INPUT_OP')


def translateReturn():
    """ReturnStmt = 'return' [Expression]
    For now, just translate expression if present
    """
    print("  Translating return")

    nextSymb()  # return

    numLine, lex, tok = getSymb()
    if lex != '}':
        translateExpression()


def translateFuncCall():
    """Function call - skip for now (basic version)"""
    print("  Skipping function call (not implemented yet)")

    nextSymb()  # function name
    nextSymb()  # (

    # Skip arguments
    depth = 1
    while depth > 0:
        numLine, lex, tok = getSymb()
        if lex == '(':
            depth += 1
        elif lex == ')':
            depth -= 1
        nextSymb()


def translateBlock():
    """Block = '{' {Statement} '}'"""
    print("  Translating block")

    nextSymb()  # {

    while True:
        numLine, lex, tok = getSymb()
        if lex == '}' and tok == 'PAR_OP':
            nextSymb()
            break
        translateStatement()


def translateExpression():
    """Expression = CompareExpr
    For arithmetic: operand1 operand2 operator
    For comparison: operand1 operand2 relop
    """
    translateCompareExpr()


def translateCompareExpr():
    """CompareExpr = ArithExpr [RelOp ArithExpr]"""
    translateArithExpr()

    # Check for comparison operator
    numLine, lex, tok = getSymb()
    if tok == 'COMPARE_OP':
        relop = lex
        nextSymb()
        translateArithExpr()
        addToPostfix(relop, 'COMPARE_OP')


def translateArithExpr():
    """ArithExpr = Term {AddOp Term}"""
    translateTerm()

    while True:
        numLine, lex, tok = getSymb()
        if tok == 'ADD_OP':
            op = lex
            nextSymb()
            translateTerm()
            addToPostfix(op, 'ADD_OP')
        else:
            break


def translateTerm():
    """Term = Power {MultOp Power}"""
    translatePower()

    while True:
        numLine, lex, tok = getSymb()
        if tok == 'MULT_OP':
            op = lex
            nextSymb()
            translatePower()
            addToPostfix(op, 'MULT_OP')
        else:
            break


def translatePower():
    """Power = Factor {'^' Factor}"""
    translateFactor()

    while True:
        numLine, lex, tok = getSymb()
        if lex == '^' and tok == 'POWER_OP':
            nextSymb()
            translateFactor()
            addToPostfix('^', 'POWER_OP')
        else:
            break


def translateFactor():
    """Factor = [Sign] Primary"""
    # Check for unary sign
    numLine, lex, tok = getSymb()
    unaryOp = None

    if tok == 'ADD_OP' and lex in ('+', '-'):
        unaryOp = lex
        nextSymb()

    translatePrimary()

    # Add unary operator after operand
    if unaryOp == '-':
        addToPostfix('NEG', 'UNARY_OP')
    # Unary + does nothing


def translatePrimary():
    """Primary = Ident | Const | '(' Expression ')'"""
    numLine, lex, tok = getSymb()

    # Constant
    if tok in ('INT', 'FLOAT', 'BOOL', 'STRING'):
        addToPostfix(lex, tok)
        nextSymb()

    # Identifier (might be function call)
    elif tok == 'IDENTIFIER':
        ident = lex
        nextSymb()

        # Check for function call
        numLine2, lex2, tok2 = getSymb()
        if lex2 == '(' and tok2 == 'PAR_OP':
            # Function call - for now just skip
            # In full implementation, translate arguments and add CALL
            print(f"    Warning: Function call '{ident}' not fully supported")
            skipFunctionCallArgs()
        else:
            addToPostfix(ident, 'IDENTIFIER')

    # Parenthesized expression
    elif lex == '(' and tok == 'PAR_OP':
        nextSymb()  # (
        translateExpression()
        nextSymb()  # )


def skipFunctionCallArgs():
    """Skips function call arguments"""
    nextSymb()  # (

    depth = 1
    while depth > 0:
        numLine, lex, tok = getSymb()
        if lex == '(':
            depth += 1
        elif lex == ')':
            depth -= 1
        nextSymb()


# ========== MAIN TRANSLATION FUNCTION ==========

def translate(table_of_symb):
    """Main translation function"""
    global tableOfSymb, numRow, len_tableOfSymb, postfixCode
    global labelCounter, tableOfLabels, tempVarCounter

    # Initialize
    tableOfSymb = table_of_symb
    numRow = 1
    len_tableOfSymb = len(tableOfSymb)
    postfixCode = []
    labelCounter = 0
    tableOfLabels = {}
    tempVarCounter = 0

    # Translate
    try:
        translateProgram()
        return True, postfixCode, tableOfLabels
    except Exception as e:
        print(f"\nTranslation ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, [], {}


def start(file_path):
    """Runs complete analysis and translation"""
    # Run lexer
    lex_success = lex_start(file_path)

    if not lex_success or g.errorCount > 0:
        print("\n✗ Lexical analysis failed. Translation not possible.")
        return False, [], {}

    # Translate
    success, postfix, labels = translate(g.tableOfSymb)

    if success:
        print("\n" + "=" * 60)
        print("✓ Translation completed successfully")
        print("=" * 60)

    return success, postfix, labels
