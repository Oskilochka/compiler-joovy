import os
from lexer.lexer import start
from lexer import globals as g

def run_test(test_name, file_path, expect_errors=False):
    print("\n" + "=" * 70)
    print(f"Test: {test_name}")
    print("=" * 70)

    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found")
        return False

    success = start(file_path)

    if expect_errors:
        if g.errorCount > 0:
            print(f"\n✓ Test '{test_name}' Passed (found {g.errorCount} errors)")
            return True
        else:
            print(f"\n✗ Test '{test_name}' Failed")
            return False
    else:
        if success and g.errorCount == 0:
            print(f"\n✓ Test '{test_name}' Passed")
            return True
        else:
            print(f"\n✗ Test '{test_name}' Failed")
            return False

def main():
    tests = [
        ("Base example", "test_programs/test_basic.joovy", False),
        ("Nested example", "test_programs/test_nested.joovy", False),
        ("Errors example", "test_programs/test_errors.joovy", True),
    ]

    results = []

    for test_name, file_path, expect_errors in tests:
        success = run_test(test_name, file_path, expect_errors)
        results.append((test_name, success))

    print("\n" + "=" * 70)
    print("Testing Result")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ Passed" if success else "✗ Failed"
        print(f"{test_name:<40s} {status}")

    print("-" * 70)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print("=" * 70)

if __name__ == "__main__":
    main()
