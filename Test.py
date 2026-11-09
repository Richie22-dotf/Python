def two_fer(name=""):
    # If name is empty, null, or missing, default to 'you'
    if not name:
        name = "you"
    return f"One for {name}, one for me."

# 2. The 4 standard test cases
tests = [
    {"input": "Alice", "expected": "One for Alice, one for me."},
    {"input": "Bob", "expected": "One for Bob, one for me."},
    {"input": "", "expected": "One for you, one for me."},
    {"input": None, "expected": "One for you, one for me."}
]

# 3. Simple Test Runner
passed = 0
for i, test in enumerate(tests, 1):
    actual = two_fer(test["input"])
    if actual == test["expected"]:
        print(f"Test {i}: PASS")
        passed += 1
    else:
        print(f"Test {i}: FAIL (Expected '{test['expected']}', got '{actual}')")

print(f"\n{passed}/4 tests passed.")New-Item app.py; code app.py
touch app.py
ls -la app.py

