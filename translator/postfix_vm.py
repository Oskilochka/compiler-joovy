class PostfixVM:
    """Virtual machine for executing postfix code"""

    def __init__(self, postfix_code, label_table):
        self.code = postfix_code
        self.labels = label_table
        self.stack = []
        self.variables = {}  # Variable storage
        self.ip = 0  # Instruction pointer
        self.output = []  # Output buffer

    def run(self):
        """Executes postfix code"""
        print("\n" + "=" * 60)
        print("EXECUTING POSTFIX CODE")
        print("=" * 60 + "\n")

        try:
            while self.ip < len(self.code):
                lexeme, token = self.code[self.ip]

                if self.debug:
                    print(f"[{self.ip}] Execute: ({lexeme}, {token}) | Stack: {self.stack}")

                self.execute_instruction(lexeme, token)

                # Don't increment IP if it was changed by jump
                if not hasattr(self, '_jumped'):
                    self.ip += 1
                else:
                    delattr(self, '_jumped')

            print("\n" + "=" * 60)
            print("✓ EXECUTION COMPLETED SUCCESSFULLY")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n✗ RUNTIME ERROR at position {self.ip}: {e}")
            print(f"   Instruction: {self.code[self.ip] if self.ip < len(self.code) else 'EOF'}")
            print(f"   Stack: {self.stack}")
            import traceback
            traceback.print_exc()
            return False

    def execute_instruction(self, lexeme, token):
        """Executes single instruction"""

        # Constants
        if token in ('INT', 'FLOAT', 'BOOL', 'STRING'):
            self.push_constant(lexeme, token)

        # Identifier (r-value)
        elif token == 'IDENTIFIER':
            self.push_variable(lexeme)

        # Identifier (l-value for assignment)
        elif token == 'IDENTIFIER_LVALUE':
            self.stack.append(lexeme)  # Just push name for assignment

        # Assignment operator
        elif token == 'ASSIGN_OP':
            self.execute_assign()

        # Arithmetic operators
        elif token == 'ADD_OP':
            self.execute_binary_op(lexeme)

        elif token == 'MULT_OP':
            self.execute_binary_op(lexeme)

        elif token == 'POWER_OP':
            self.execute_binary_op(lexeme)

        # Comparison operators
        elif token == 'COMPARE_OP':
            self.execute_compare(lexeme)

        # Unary operators
        elif token == 'UNARY_OP':
            self.execute_unary(lexeme)

        # Control flow
        elif token == 'COLON':
            pass  # Label definition - already processed

        elif token == 'LABEL':
            # Label reference - push onto stack for jump instructions
            self.stack.append(lexeme)

        elif token == 'JUMP':
            self.execute_jump()

        elif token == 'JUMP_IF_FALSE':
            self.execute_jump_if_false()

        # I/O operations
        elif token == 'PRINT_OP':
            self.execute_print()

        elif token == 'INPUT_OP':
            self.execute_input()

        else:
            print(f"Warning: Unknown token '{token}' for lexeme '{lexeme}'")

    def push_constant(self, lexeme, token):
        """Pushes constant onto stack"""
        if token == 'INT':
            value = int(lexeme)
        elif token == 'FLOAT':
            value = float(lexeme)
        elif token == 'BOOL':
            value = lexeme == 'true'
        elif token == 'STRING':
            # Remove quotes
            value = lexeme.strip('"')
        else:
            value = lexeme

        self.stack.append(value)

    def push_variable(self, name):
        """Pushes variable value onto stack"""
        if name not in self.variables:
            raise RuntimeError(f"Undefined variable '{name}'")

        self.stack.append(self.variables[name])

    def execute_assign(self):
        """Executes assignment: var = value

        Stack before: [... value var_name]
        Stack after:  [...]

        Note: In postfix 'a 10 :=' means push a, push 10, then assign 10 to a
        So we pop in order: var_name (top), value (next)
        """
        if len(self.stack) < 2:
            raise RuntimeError("Stack underflow in assignment")

        var_name = self.stack.pop()  # Top: variable name
        value = self.stack.pop()     # Next: value

        self.variables[var_name] = value

        if self.debug:
            print(f"   Assigned: {var_name} = {value}")

    def execute_binary_op(self, operator):
        """Executes binary arithmetic operation"""
        if len(self.stack) < 2:
            raise RuntimeError(f"Stack underflow for operator '{operator}'")

        right = self.stack.pop()
        left = self.stack.pop()

        if operator == '+':
            result = left + right
        elif operator == '-':
            result = left - right
        elif operator == '*':
            result = left * right
        elif operator == '/':
            if right == 0:
                raise RuntimeError("Division by zero")
            result = left / right
        elif operator == '^':
            result = left ** right
        else:
            raise RuntimeError(f"Unknown operator '{operator}'")

        self.stack.append(result)

    def execute_compare(self, operator):
        """Executes comparison operation"""
        if len(self.stack) < 2:
            raise RuntimeError(f"Stack underflow for operator '{operator}'")

        right = self.stack.pop()
        left = self.stack.pop()

        if operator == '==':
            result = left == right
        elif operator == '!=':
            result = left != right
        elif operator == '<':
            result = left < right
        elif operator == '<=':
            result = left <= right
        elif operator == '>':
            result = left > right
        elif operator == '>=':
            result = left >= right
        else:
            raise RuntimeError(f"Unknown comparison operator '{operator}'")

        self.stack.append(result)

    def execute_unary(self, operator):
        """Executes unary operation"""
        if len(self.stack) < 1:
            raise RuntimeError(f"Stack underflow for operator '{operator}'")

        operand = self.stack.pop()

        if operator == 'NEG':
            result = -operand
        else:
            raise RuntimeError(f"Unknown unary operator '{operator}'")

        self.stack.append(result)

    def execute_jump(self):
        """Executes unconditional jump"""
        if len(self.stack) < 1:
            raise RuntimeError("Stack underflow in JMP")

        label = self.stack.pop()

        if label not in self.labels:
            raise RuntimeError(f"Undefined label '{label}'")

        self.ip = self.labels[label]
        self._jumped = True

        if self.debug:
            print(f"   Jump to label '{label}' (position {self.ip})")

    def execute_jump_if_false(self):
        """Executes conditional jump (jump if false)"""
        if len(self.stack) < 2:
            raise RuntimeError("Stack underflow in JF")

        label = self.stack.pop()
        condition = self.stack.pop()

        if not condition:
            if label not in self.labels:
                raise RuntimeError(f"Undefined label '{label}'")

            self.ip = self.labels[label]
            self._jumped = True

            if self.debug:
                print(f"   Conditional jump to '{label}' (condition false)")
        else:
            if self.debug:
                print(f"   No jump (condition true)")

    def execute_print(self):
        """Executes print operation"""
        if len(self.stack) < 1:
            raise RuntimeError("Stack underflow in PRINT")

        count = self.stack.pop()

        if not isinstance(count, int):
            count = int(count)

        if len(self.stack) < count:
            raise RuntimeError(f"Stack underflow: need {count} values for PRINT")

        # Pop values in reverse order (they were pushed left-to-right)
        values = []
        for _ in range(count):
            values.append(self.stack.pop())

        values.reverse()

        # Print
        output = ' '.join(str(v) for v in values)
        print(f"OUTPUT: {output}")
        self.output.append(output)

    def execute_input(self):
        """Executes input operation"""
        if len(self.stack) < 1:
            raise RuntimeError("Stack underflow in INPUT")

        var_name = self.stack.pop()

        try:
            value_str = input(f"INPUT {var_name}: ")

            # Try to parse as number
            try:
                if '.' in value_str:
                    value = float(value_str)
                else:
                    value = int(value_str)
            except ValueError:
                # Keep as string
                value = value_str

            self.variables[var_name] = value

        except EOFError:
            print(f"\nEOF reached, setting {var_name} = 0")
            self.variables[var_name] = 0

    def get_output(self):
        """Returns collected output"""
        return self.output

    def get_variables(self):
        """Returns variable state"""
        return self.variables.copy()


def execute_postfix(postfix_code, label_table, debug=False):
    """Executes postfix code"""
    vm = PostfixVM(postfix_code, label_table)
    vm.debug = debug

    success = vm.run()

    if success:
        print("\n" + "=" * 60)
        print("FINAL VARIABLE STATE:")
        print("=" * 60)

        variables = vm.get_variables()
        if variables:
            for name, value in sorted(variables.items()):
                print(f"  {name} = {value}")
        else:
            print("  (no variables)")

        print("\n" + "=" * 60)
        print("PROGRAM OUTPUT:")
        print("=" * 60)

        output = vm.get_output()
        if output:
            for line in output:
                print(f"  {line}")
        else:
            print("  (no output)")

    return success
