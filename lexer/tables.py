tokenTable = {
    'for': 'KEYWORD', 'in': 'KEYWORD',
    'if': 'KEYWORD', 'else': 'KEYWORD',
    'print': 'KEYWORD', 'input': 'KEYWORD',
    'const': 'KEYWORD', 'def': 'KEYWORD',
    'return': 'KEYWORD',

    'int': 'TYPE', 'float': 'TYPE',
    'bool': 'TYPE', 'string': 'TYPE',

    'true': 'BOOL', 'false': 'BOOL',

    '=': 'ASSIGN_OP',
    '+': 'ADD_OP', '-': 'ADD_OP',
    '*': 'MULT_OP', '/': 'MULT_OP',
    '^': 'POWER_OP',

    '==': 'COMPARE_OP', '!=': 'COMPARE_OP',
    '<': 'COMPARE_OP', '<=': 'COMPARE_OP',
    '>': 'COMPARE_OP', '>=': 'COMPARE_OP',

    '(': 'PAR_OP', ')': 'PAR_OP',
    '{': 'PAR_OP', '}': 'PAR_OP',
    '[': 'PAR_OP', ']': 'PAR_OP',
    ',': 'COMMA', ';': 'SEMICOLON',
    '.': 'DOT',

    ' ': 'WS', '\t': 'WS', '\n': 'NL'
}

tokStateTable = {
    2: 'IDENTIFIER',
    9: 'FLOAT',
    13: 'INT',
    14: 'FLOAT',
    41: 'STRING',
    33: 'COMMENT'
}
