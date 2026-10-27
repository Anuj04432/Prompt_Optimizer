"""
Fast offline test suite for verifying the Prompt Optimizer pipeline.
Runs without requiring external API keys.
"""

from services.preprocess import preprocess
from services.intent import detect_intent
from services.rule_engine import rule_engine
from services.compressor import compress, count_tokens
from services.evaluator import similarity_score
from services.optimization import optimize_prompt


def test_intent_detection():
    # Test code and python detection
    res1 = detect_intent("Write a python function for quicksort")
    assert "code" in res1["intents"]
    assert "python" in res1["intents"]

    # Test SQL detection
    res2 = detect_intent("Optimize this SQL query for postgres")
    assert "sql" in res2["intents"]

    # Test email detection without false substring match
    res3 = detect_intent("Draft an email to my manager")
    assert "email" in res3["intents"]

    # Test false substring prevention: 'blackmail' should not trigger email
    res4 = detect_intent("A story about blackmail in high society")
    assert "email" not in res4["intents"]

    print("[PASS] Intent detection tests passed")


def test_compressor():
    prompt = "Please kindly basically help me write a python script"
    compressed = compress(prompt)
    assert "please" not in compressed.lower()
    assert "basically" not in compressed.lower()
    assert "python script" in compressed.lower()
    print("[PASS] Compressor tests passed")


def test_evaluator():
    orig = "Build a binary search algorithm in Python"
    rewritten = "Implement an optimized binary search algorithm using Python with error handling"
    score = similarity_score(orig, rewritten)
    assert score >= 0.8, f"Expected high retention score, got {score}"

    unrelated = "Make a chocolate cake with vanilla frosting"
    low_score = similarity_score(orig, unrelated)
    assert low_score < 0.2, f"Expected low score for unrelated text, got {low_score}"
    print("[PASS] Evaluator tests passed")


def test_rules_optimization():
    prompt = "write a function to reverse a linked list in python"
    result = optimize_prompt(prompt, mode="rules")

    assert result.original_prompt == prompt
    assert len(result.optimized_prompt) > len(prompt)
    assert "python" in result.intent
    assert "code" in result.intent
    assert result.original_tokens > 0
    assert result.optimized_tokens > result.original_tokens
    assert result.similarity_score > 0.0
    print("[PASS] Rules mode optimization passed")


if __name__ == "__main__":
    print("Running Prompt Optimizer Offline Verification...")
    test_intent_detection()
    test_compressor()
    test_evaluator()
    test_rules_optimization()
    print("=== All Phase 1 offline tests passed successfully! ===")
