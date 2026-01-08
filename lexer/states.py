initState = 0

# Final states
F = {
    2, 9, 13, 14, 21, 22, 24, 26, 27,
    29, 30, 33, 34, 41, 50, 51, 52, 53,
    101, 102
}
# Conditions requiring a character return
Fstar = {2, 9, 13, 14, 22, 27, 30, 34}

# Error states
Ferror = {101, 102}

# State-transition function
stf = {
    # Identifiers and keywords
    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, 'other'): 2,

    # int
    (0, 'Digit'): 4, (4, 'Digit'): 4,

    # numbers like .5
    (0, 'dot'): 5, (5, 'Digit'): 6, (6, 'Digit'): 6,

    # numbers like 2.5 or 2.
    (4, 'dot'): 7, (7, 'Digit'): 8, (8, 'Digit'): 8, (7, 'other'): 9,

    # 2.5e2, 1.2E-3
    (8, 'exp'): 10, (6, 'exp'): 10, (9, 'exp'): 10, (4, 'exp'): 10,
    (10, '+'): 11, (10, '-'): 11, (10, 'Digit'): 12,
    (11, 'Digit'): 12, (12, 'Digit'): 12,

    # Number completion
    (4, 'other'): 13,  # int
    (6, 'other'): 14,  # float (.5)
    (8, 'other'): 14,  # float (2.5)
    (9, 'other'): 14,  # float (2.)
    (12, 'other'): 14, # float (2.5e2)

    # Comparison and assignment operators
    (0, '='): 20, (20, '='): 21, (20, 'other'): 22,  # == or =
    (0, '!'): 23, (23, '='): 24,                      # !=
    (0, '<'): 25, (25, '='): 26, (25, 'other'): 27,  # <= or <
    (0, '>'): 28, (28, '='): 29, (28, 'other'): 30,  # >= or >

    # Comments
    (0, '/'): 31, (31, '/'): 32, (32, 'nl'): 33,
    (32, 'other'): 32, (31, 'other'): 34,  # / or error

    # String literals
    (0, 'dquote'): 40, (40, 'Letter'): 40, (40, 'Digit'): 40,
    (40, 'ws'): 40, (40, 'other'): 40, (40, 'dquote'): 41,

    # Whitespace characters
    (0, 'ws'): 0,
    (0, 'nl'): 50,

    # Arithmetic operators and parentheses
    (0, '+'): 51, (0, '-'): 51, (0, '*'): 51, (0, '^'): 51,
    (0, '('): 52, (0, ')'): 52, (0, '{'): 52, (0, '}'): 52,
    (0, '['): 52, (0, ']'): 52,
    (0, ','): 53, (0, ';'): 53,

    # Error state
    (0, 'other'): 101,
    (23, 'other'): 102,  # ! without =
}
