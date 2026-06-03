#!/usr/bin/env python3
"""
Run all unit tests for fdel
"""

import sys
import os
import unittest

# Add the parent directory to path so Python can find the 'fdel' package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Discover and run all tests"""
    # Point to the tests directory inside fdel package
    test_dir = os.path.join(os.path.dirname(__file__), 'fdel', 'tests')
    
    if not os.path.exists(test_dir):
        print(f"Error: Tests directory not found at {test_dir}")
        print("Creating tests directory...")
        os.makedirs(test_dir, exist_ok=True)
        print("Please create test files in fdel/tests/ directory")
        return False
    
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test module"""
    test_path = os.path.join(os.path.dirname(__file__), 'fdel', 'tests', f'{test_name}.py')
    
    if not os.path.exists(test_path):
        print(f"Test module '{test_name}' not found at {test_path}")
        return False
    
    # Add tests directory to path
    tests_dir = os.path.join(os.path.dirname(__file__), 'fdel', 'tests')
    sys.path.insert(0, tests_dir)
    
    try:
        suite = unittest.defaultTestLoader.loadTestsFromName(f'{test_name}')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"Error importing test: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FDEL UNIT TESTS")
    print("=" * 60 + "\n")
    
    # Check if tests exist
    tests_dir = os.path.join(os.path.dirname(__file__), 'fdel', 'tests')
    
    if not os.path.exists(tests_dir):
        print(f"Creating tests directory at: {tests_dir}")
        os.makedirs(tests_dir, exist_ok=True)
        print("\n⚠️  No test files found!")
        print("Please create test files in: fdel/tests/")
        print("  - test_core.py")
        print("  - test_archive.py")
        print("  - test_stats.py")
        print("  - test_integration.py")
        print("  - __init__.py")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        # Run specific test
        success = run_specific_test(sys.argv[1])
    else:
        # Run all tests
        success = run_all_tests()
    
    print("\n" + "=" * 60)
    print("✅ TESTS PASSED" if success else "❌ TESTS FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
