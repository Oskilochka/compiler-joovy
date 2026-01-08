from . import globals as g

# reads the next char from the input stream
def nextChar():
    # index of the curr char
    g.numChar += 1

    # the text limits ? return the char
    return g.sourceCode[g.numChar] if g.numChar < g.lenCode else ''

# returns a char to the input stream
def putCharBack():
    # when a symbol no longer belongs to the curr token and should be processed again
    g.numChar -= 1

# checks if the state is final
def is_final(st, F):
    return st in F
