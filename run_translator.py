import sys
import argparse
from translator.translator import start as translate_start
from translator.postfix_vm import execute_postfix


def print_postfix_code(postfix_code):
    """Prints postfix code in readable format"""
    print("\n" + "=" * 60)
    print("GENERATED POSTFIX CODE:")
    print("=" * 60)

    if not postfix_code:
        print("  (empty)")
        return

    for i, (lexeme, token) in enumerate(postfix_code):
        print(f"  {i:3d}: ({lexeme:20s}, {token})")


def print_label_table(label_table):
    """Prints label table"""
    print("\n" + "=" * 60)
    print("LABEL TABLE:")
    print("=" * 60)

    if not label_table:
        print("  (no labels)")
        return

    for label, position in sorted(label_table.items(), key=lambda x: x[1]):
        print(f"  {label:15s} -> position {position}")


def save_postfix_to_file(postfix_code, filename):
    """Saves postfix code to file"""
    output_file = filename.replace('.joovy', '.postfix')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Postfix code generated from Joovy\n")
            f.write(f"# Source: {filename}\n\n")

            for i, (lexeme, token) in enumerate(postfix_code):
                f.write(f"{i:3d}: {lexeme:20s} {token}\n")

        print(f"\n✓ Postfix code saved to: {output_file}")
        return True

    except Exception as e:
        print(f"\n✗ Error saving postfix code: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Joovy Compiler and Interpreter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile and execute
  python run_translator.py program.joovy
  
  # Compile only (no execution)
  python run_translator.py program.joovy --no-execute
  
  # Debug mode (verbose output)
  python run_translator.py program.joovy --debug
  
  # Save postfix code to file
  python run_translator.py program.joovy --save-postfix
        """
    )

    parser.add_argument('file', help='Joovy source file (.joovy)')
    parser.add_argument('--no-execute', action='store_true',
                        help='Compile only, do not execute')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output during execution')
    parser.add_argument('--save-postfix', action='store_true',
                        help='Save generated postfix code to file')

    args = parser.parse_args()

    print("=" * 70)
    print("JOOVY COMPILER AND INTERPRETER")
    print("=" * 70)
    print(f"Source file: {args.file}")
    print("=" * 70)

    # Step 1: Lexical analysis and translation
    success, postfix_code, label_table = translate_start(args.file)

    if not success:
        print("\n✗ Compilation failed")
        return 1

    # Display generated code
    print_postfix_code(postfix_code)
    print_label_table(label_table)

    # Save postfix code if requested
    if args.save_postfix:
        save_postfix_to_file(postfix_code, args.file)

    # Step 2: Execute postfix code
    if not args.no_execute:
        if not postfix_code:
            print("\n⚠ No code to execute (empty program)")
            return 0

        print("\n" + "=" * 70)
        print("STARTING EXECUTION")
        print("=" * 70)

        exec_success = execute_postfix(postfix_code, label_table, debug=args.debug)

        if not exec_success:
            print("\n✗ Execution failed")
            return 1

        print("\n" + "=" * 70)
        print("✓ COMPILATION AND EXECUTION COMPLETED SUCCESSFULLY")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✓ COMPILATION COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("(Execution skipped)")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
