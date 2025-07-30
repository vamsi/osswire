from url_validator import validate_oss_url

def test_url_validator():
    """Test the URL validator with various test cases"""
    
    print("🧪 Testing OSSWire URL Validator\n")
    
    # Test cases
    test_cases = [
        # Valid URLs
        ("https://github.com/user/repo", "✅ Should be valid"),
        ("https://gitlab.com/user/repo", "✅ Should be valid"),
        ("https://codeberg.org/user/repo", "✅ Should be valid"),
        ("https://sr.ht/user/repo", "✅ Should be valid"),
        ("https://bitbucket.org/user/repo", "✅ Should be valid"),
        ("https://npmjs.com/package/name", "✅ Should be valid"),
        ("https://crates.io/crates/name", "✅ Should be valid"),
        ("https://pypi.org/project/name", "✅ Should be valid"),
        ("https://custom.gitea.com/user/repo", "✅ Should be valid (wildcard)"),
        ("https://my.gitea.org/user/repo", "✅ Should be valid (wildcard)"),
        ("https://repo.gitea.io/user/repo", "✅ Should be valid (wildcard)"),
        
        # Invalid URLs
        ("https://bit.ly/abc123", "❌ Should be blocked (shortener)"),
        ("https://t.co/abc123", "❌ Should be blocked (shortener)"),
        ("https://gumroad.com/l/product", "❌ Should be blocked (commercial)"),
        ("https://notion.so/page", "❌ Should be blocked (commercial)"),
        ("https://youtube.com/watch?v=123", "❌ Should be blocked (social)"),
        ("https://instagram.com/user", "❌ Should be blocked (social)"),
        ("https://example.com", "❌ Should be blocked (not whitelisted)"),
        ("https://google.com", "❌ Should be blocked (not whitelisted)"),
        
        # Protocol tests
        ("http://github.com/user/repo", "❌ Should be blocked (no HTTPS)"),
        ("github.com/user/repo", "✅ Should be valid (auto-adds HTTPS)"),
        
        # Edge cases
        ("", "❌ Should be blocked (empty)"),
        ("not-a-url", "❌ Should be blocked (invalid format)"),
        ("https://www.github.com/user/repo", "✅ Should be valid (www prefix)"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for url, description in test_cases:
        result = validate_oss_url(url)
        status = "✅ PASS" if result.valid else "❌ FAIL"
        print(f"{status} {description}")
        print(f"   URL: {url}")
        print(f"   Result: {result.reason}")
        if result.normalized_url:
            print(f"   Normalized: {result.normalized_url}")
        print()
        
        # Count expected vs actual results
        expected_valid = "✅" in description
        if result.valid == expected_valid:
            passed += 1
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! URL validator is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    test_url_validator() 