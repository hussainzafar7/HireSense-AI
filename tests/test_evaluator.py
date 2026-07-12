import subprocess
import sys

from backend.answer_evaluator import AnswerEvaluator


def ensure_models():
    subprocess.run([sys.executable, "training/preprocess.py"], check=True)
    subprocess.run([sys.executable, "training/train_evaluator.py"], check=True)


def test_answer_evaluator_scores_quality_order():
    ensure_models()
    evaluator = AnswerEvaluator()
    q = "What is recursion and why is it important?"
    ref = "Recursion is a technique where a function calls itself to solve smaller subproblems. It requires a base case and recursive case and uses the call stack."
    keywords = ["base case", "recursive case", "stack", "subproblem"]
    excellent = evaluator.evaluate(q, "Recursion is when a function calls itself on smaller subproblems. It must have a base case to stop and a recursive case that moves toward that base case. Each call uses the stack, so depth and complexity matter.", ref, keywords)
    poor = evaluator.evaluate(q, "I don't know", ref, keywords)
    good = evaluator.evaluate(q, "Recursion is when a function calls itself and needs a base case.", ref, keywords)
    assert excellent["score"] >= 0.7
    assert poor["score"] <= 0.2
    assert excellent["score"] > good["score"] > poor["score"]
