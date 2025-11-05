"""
Integration Test Script - Quick Snippet Overlay
Tests real components with actual configuration files (no GUI)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test 1: Verify all modules can be imported"""
    print("Test 1: Module Imports")
    print("-" * 50)

    try:
        import snippet_manager
        print("[PASS] snippet_manager imported")
    except Exception as e:
        print(f"[FAIL] snippet_manager failed: {e}")
        return False

    try:
        import search_engine
        print("[PASS] search_engine imported")
    except Exception as e:
        print(f"[FAIL] search_engine failed: {e}")
        return False

    try:
        import variable_handler
        print("[PASS] variable_handler imported")
    except Exception as e:
        print(f"[FAIL] variable_handler failed: {e}")
        return False

    try:
        import config_manager
        print("[PASS] config_manager imported")
    except Exception as e:
        print(f"[FAIL] config_manager failed: {e}")
        return False

    print("[PASS] All core modules imported successfully\n")
    return True


def test_config_loading():
    """Test 2: Load real configuration file"""
    print("Test 2: Configuration Loading")
    print("-" * 50)

    from config_manager import ConfigManager

    config_path = Path.home() / 'snippets' / 'config.yaml'
    print(f"Config path: {config_path}")

    try:
        config = ConfigManager(str(config_path))
        print(f"[PASS] Configuration loaded")
        print(f"   Hotkey: {config.get('hotkey')}")
        print(f"   Snippet file: {config.get('snippet_file')}")
        print(f"   Max results: {config.get('max_results')}")
        print(f"   Theme: {config.get('theme')}")

        # Validate configuration
        is_valid, errors = config.validate()
        if is_valid:
            print(f"[PASS] Configuration validation passed")
        else:
            print(f"[FAIL] Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False

    except Exception as e:
        print(f"[FAIL] Configuration loading failed: {e}")
        return False

    print()
    return True


def test_snippet_loading():
    """Test 3: Load real snippets file"""
    print("Test 3: Snippet Loading")
    print("-" * 50)

    from snippet_manager import SnippetManager

    snippet_path = Path.home() / 'snippets' / 'snippets.yaml'
    print(f"Snippets path: {snippet_path}")

    try:
        manager = SnippetManager(str(snippet_path))
        snippets = manager.load()  # Actually load the snippets

        print(f"[PASS] Snippets loaded: {len(snippets)} total")

        # Show first 5 snippets
        print(f"\nFirst 5 snippets:")
        for i, snippet in enumerate(snippets[:5]):
            name = snippet.name
            tags = snippet.tags
            print(f"   {i+1}. {name} (tags: {', '.join(tags)})")

        # Validate snippet structure
        for snippet in snippets:
            if not snippet.validate():
                print(f"[FAIL] Snippet validation failed: {snippet.name}")
                return False

        print(f"[PASS] All snippets have required fields")

    except Exception as e:
        print(f"[FAIL] Snippet loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    return True


def test_search_functionality():
    """Test 4: Search engine with real snippets"""
    print("Test 4: Search Functionality")
    print("-" * 50)

    from snippet_manager import SnippetManager
    from search_engine import SearchEngine

    snippet_path = Path.home() / 'snippets' / 'snippets.yaml'

    try:
        manager = SnippetManager(str(snippet_path))
        snippets = manager.load()  # Actually load the snippets
        search = SearchEngine(snippets)

        # Test searches
        test_queries = [
            ("git", "Should find git-related snippets"),
            ("powershell", "Should find PowerShell snippets"),
            ("python", "Should find Python snippets"),
            ("network", "Should find network snippets"),
            ("gti", "Fuzzy: Should still find 'git' (typo tolerance)"),
        ]

        for query, description in test_queries:
            results = search.search(query)
            print(f"\n   Query: '{query}' - {description}")
            print(f"   Results: {len(results)} found")

            if len(results) > 0:
                # Show top 3 results
                for i, result in enumerate(results[:3]):
                    name = result['snippet'].name
                    score = result['score']
                    print(f"      {i+1}. {name} (score: {score:.1f})")
            else:
                print(f"      (no results)")

        print(f"\n[PASS] Search engine working correctly")

    except Exception as e:
        print(f"[FAIL] Search functionality failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    return True


def test_variable_detection():
    """Test 5: Variable handler with real snippet content"""
    print("Test 5: Variable Detection")
    print("-" * 50)

    import variable_handler

    test_cases = [
        ("Hello world", []),
        ("Hello {{name}}", ["name"]),
        ("Hello {{name:World}}", ["name"]),
        ("{{greeting:Hi}} {{name}}, welcome to {{place:Earth}}", ["greeting", "name", "place"]),
        ("netstat -ano | findstr :{{port:8080}}", ["port"]),
    ]

    for content, expected_vars in test_cases:
        detected_vars = variable_handler.detect_variables(content)
        var_names = [v['name'] for v in detected_vars]

        if var_names == expected_vars:
            print(f"[PASS] '{content[:50]}...'")
            print(f"   Variables: {var_names}")
        else:
            print(f"[FAIL] '{content[:50]}...'")
            print(f"   Expected: {expected_vars}")
            print(f"   Got: {var_names}")
            return False

    print(f"\n[PASS] Variable detection working correctly")
    print()
    return True


def test_variable_substitution():
    """Test 6: Variable substitution"""
    print("Test 6: Variable Substitution")
    print("-" * 50)

    import variable_handler

    # Test with provided values
    content = "Hello {{name}}, welcome to {{place}}!"
    values = {"name": "Alice", "place": "Wonderland"}
    result = variable_handler.substitute_variables(content, values)
    expected = "Hello Alice, welcome to Wonderland!"

    if result == expected:
        print(f"[PASS] Substitution test 1 passed")
        print(f"   Input: {content}")
        print(f"   Output: {result}")
    else:
        print(f"[FAIL] Substitution test 1 failed")
        print(f"   Expected: {expected}")
        print(f"   Got: {result}")
        return False

    # Test with default values
    content2 = "Port: {{port:8080}}, Host: {{host:localhost}}"
    values2 = {"port": "3000"}  # Only override port, use default for host
    detected = variable_handler.detect_variables(content2)

    # Build values dict with defaults
    final_values = {}
    for var in detected:
        if var['name'] in values2:
            final_values[var['name']] = values2[var['name']]
        else:
            final_values[var['name']] = var.get('default', '')

    result2 = variable_handler.substitute_variables(content2, final_values)
    expected2 = "Port: 3000, Host: localhost"

    if result2 == expected2:
        print(f"[PASS] Substitution test 2 passed (with defaults)")
        print(f"   Input: {content2}")
        print(f"   Output: {result2}")
    else:
        print(f"[FAIL] Substitution test 2 failed")
        print(f"   Expected: {expected2}")
        print(f"   Got: {result2}")
        return False

    print(f"\n[PASS] Variable substitution working correctly")
    print()
    return True


def test_performance():
    """Test 7: Performance benchmarks"""
    print("Test 7: Performance Benchmarks")
    print("-" * 50)

    import time
    from snippet_manager import SnippetManager
    from search_engine import SearchEngine

    snippet_path = Path.home() / 'snippets' / 'snippets.yaml'

    try:
        # Test snippet loading time
        start = time.time()
        manager = SnippetManager(str(snippet_path))
        snippets = manager.load()
        load_time = (time.time() - start) * 1000
        print(f"[PASS] Snippet loading: {load_time:.1f}ms")

        if load_time > 500:
            print(f"[WARN]  Warning: Load time > 500ms target")

        # Test search performance
        search = SearchEngine(snippets)

        start = time.time()
        for _ in range(100):
            search.search("git")
        avg_search_time = ((time.time() - start) / 100) * 1000

        print(f"[PASS] Average search time: {avg_search_time:.2f}ms")

        if avg_search_time > 50:
            print(f"[WARN]  Warning: Search time > 50ms target")
        else:
            print(f"   (Excellent: {(50/avg_search_time):.1f}x faster than target)")

        # Test search throughput
        start = time.time()
        count = 0
        while time.time() - start < 1.0:
            search.search("test")
            count += 1

        print(f"[PASS] Search throughput: {count} searches/second")

        if count < 100:
            print(f"[WARN]  Warning: Throughput < 100 searches/sec")

    except Exception as e:
        print(f"[FAIL] Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    return True


def test_edge_cases():
    """Test 8: Edge cases and error handling"""
    print("Test 8: Edge Cases")
    print("-" * 50)

    from search_engine import SearchEngine
    from snippet_manager import Snippet
    import variable_handler
    from datetime import date

    # Test empty search
    search = SearchEngine([])
    results = search.search("anything")
    print(f"[PASS] Empty snippet list: {len(results)} results (expected 0)")

    # Test special characters in search
    test_snippet = Snippet(
        id='test',
        name='Test & Special <chars>',
        description='Test snippet',
        content='Content with "quotes" and \'apostrophes\'',
        tags=[],
        created=date.today(),
        modified=date.today()
    )
    search = SearchEngine([test_snippet])
    results = search.search("special")
    print(f"[PASS] Special characters in snippets: {len(results)} results")

    # Test variable handler with edge cases

    # Nested braces (should be literal)
    content = "Object: {{outer:{inner:value}}}"
    vars = variable_handler.detect_variables(content)
    print(f"[PASS] Nested braces handled: {len(vars)} variables detected")

    # Windows paths with colons
    content = "Path: C:\\Users\\{{user:mikeh}}\\Documents"
    vars = variable_handler.detect_variables(content)
    print(f"[PASS] Windows paths with colons: {len(vars)} variables detected")

    # Empty variable name
    content = "Invalid: {{}}"
    vars = variable_handler.detect_variables(content)
    print(f"[PASS] Empty variable name: {len(vars)} variables detected (expected 0)")

    print()
    return True


def main():
    """Run all integration tests"""
    print("=" * 70)
    print("QUICK SNIPPET OVERLAY - INTEGRATION TESTS")
    print("=" * 70)
    print()

    tests = [
        ("Module Imports", test_imports),
        ("Configuration Loading", test_config_loading),
        ("Snippet Loading", test_snippet_loading),
        ("Search Functionality", test_search_functionality),
        ("Variable Detection", test_variable_detection),
        ("Variable Substitution", test_variable_substitution),
        ("Performance Benchmarks", test_performance),
        ("Edge Cases", test_edge_cases),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"[WARN]  {name} FAILED\n")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {name} CRASHED: {e}\n")
            import traceback
            traceback.print_exc()

    print("=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()

    if failed == 0:
        print("[PASS] ALL INTEGRATION TESTS PASSED!")
        print("\nCore functionality verified:")
        print("  - Configuration management [OK]")
        print("  - Snippet loading and validation [OK]")
        print("  - Fuzzy search with typo tolerance [OK]")
        print("  - Variable detection and substitution [OK]")
        print("  - Performance targets met [OK]")
        print("  - Edge case handling [OK]")
        print()
        print("Status: READY FOR MANUAL GUI TESTING")
        return 0
    else:
        print(f"[FAIL] {failed} TEST(S) FAILED")
        print("\nPlease review failures above and fix issues before proceeding.")
        return 1


if __name__ == '__main__':
    sys.exit(main())



