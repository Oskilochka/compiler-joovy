import os
import sys
from parser import start

def run_test(test_name, file_path, should_pass=True):
    """Runs one test"""
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print("=" * 70)

    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found")
        return False

    success = start(file_path)

    # Check if result matches expectation
    if should_pass:
        if success:
            print(f"\n✓ Test '{test_name}' PASSED (as expected)")
            return True
        else:
            print(f"\n✗ Test '{test_name}' FAILED (should have passed)")
            return False
    else:
        if not success:
            print(f"\n✓ Test '{test_name}' PASSED (correctly detected errors)")
            return True
        else:
            print(f"\n✗ Test '{test_name}' FAILED (should have detected errors)")
            return False


def main():
    """Main function"""
    tests = [
        # (name, file, should_pass)
        ("Simple correct program", "test_programs/test_correct.joovy", True),
        ("Syntax errors detection", "test_programs/test_syntax_errors.joovy", False),
    ]

    results = []

    for test_name, file_path, should_pass in tests:
        if os.path.exists(file_path):
            success = run_test(test_name, file_path, should_pass)
            results.append((test_name, success))
        else:
            print(f"\nSkipping test '{test_name}' - file not found")

    # Summary
    print("\n" + "=" * 70)
    print("TESTING SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name:<40s} {status}")

    print("-" * 70)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
