import sys
import os
import argparse
from clr_translator.clr_translator import start


def save_il_file(cil_code, source_file):
    """Saves CIL code to .il file"""
    output_file = source_file.replace('.joovy', '.il')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in cil_code:
                f.write(line + '\n')

        print(f"\n✓ CIL code saved to: {output_file}")
        return output_file

    except Exception as e:
        print(f"\n✗ Error saving CIL code: {e}")
        return None


def compile_with_ilasm(il_file):
    """Compiles .il file with ilasm (if available)"""
    import subprocess

    print("\n" + "=" * 60)
    print("COMPILING WITH ILASM")
    print("=" * 60)

    try:
        # Try to find ilasm
        result = subprocess.run(['ilasm', '/help'],
                                capture_output=True,
                                text=True,
                                timeout=5)

        if result.returncode != 0:
            print("✗ ilasm not found. Install .NET SDK to compile .il files.")
            print("\nTo compile manually:")
            print(f"  ilasm {il_file}")
            return False

        # Compile
        exe_file = il_file.replace('.il', '.exe')
        result = subprocess.run(['ilasm', '/output=' + exe_file, il_file],
                                capture_output=True,
                                text=True)

        if result.returncode == 0:
            print(f"✓ Successfully compiled: {exe_file}")
            print(f"\nTo run:")
            print(f"  {exe_file}")
            return True
        else:
            print(f"✗ Compilation failed:")
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("✗ ilasm not found. Install .NET SDK to compile .il files.")
        print("\nTo compile manually:")
        print(f"  ilasm {il_file}")
        return False

    except Exception as e:
        print(f"✗ Error during compilation: {e}")
        return False


def print_cil_code(cil_code):
    """Prints CIL code"""
    print("\n" + "=" * 60)
    print("GENERATED CIL CODE:")
    print("=" * 60)

    for i, line in enumerate(cil_code, 1):
        print(f"{i:3d}: {line}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Joovy to CLR Compiler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate to CIL
  python run_clr.py program.joovy
  
  # Translate and try to compile with ilasm
  python run_clr.py program.joovy --compile
  
  # Show CIL code on screen
  python run_clr.py program.joovy --show-code
        """
    )

    parser.add_argument('file', help='Joovy source file (.joovy)')
    parser.add_argument('--compile', action='store_true',
                        help='Try to compile with ilasm')
    parser.add_argument('--show-code', action='store_true',
                        help='Display generated CIL code')

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"✗ Error: File '{args.file}' not found")
        return 1

    print("=" * 70)
    print("JOOVY TO CLR COMPILER")
    print("=" * 70)
    print(f"Source file: {args.file}")
    print("=" * 70)

    # Translate
    success, cil_code = start(args.file)

    if not success:
        print("\n✗ Translation failed")
        return 1

    # Show code if requested
    if args.show_code:
        print_cil_code(cil_code)

    # Save to file
    il_file = save_il_file(cil_code, args.file)

    if not il_file:
        return 1

    # Compile if requested
    if args.compile:
        compile_with_ilasm(il_file)
    else:
        print("\nTo compile with .NET SDK:")
        print(f"  ilasm /output={il_file.replace('.il', '.exe')} {il_file}")

    print("\n" + "=" * 70)
    print("✓ CLR COMPILATION COMPLETED")
    print("=" * 70)

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
