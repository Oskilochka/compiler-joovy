import sys
from parser import start

def main():
    if len(sys.argv) < 2:
        print("Using: python run_parser.py <file.joovy>")
        print("\nExamples:")
        print("  python run_parser.py test_programs/test_correct.joovy")
        print("  python run_parser.py test_programs/test_syntax_errors.joovy")
        sys.exit(1)

    file_path = sys.argv[1]

    print(f"\n{'=' * 70}")
    print(f"Analys: {file_path}")
    print(f"{'=' * 70}")

    success = start(file_path)

    if success:
        print("\n✓ The program is syntactically correct.")
        sys.exit(0)
    else:
        print("\n✗ The program contains syntax errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
