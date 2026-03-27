"""
Project B Evaluation Harness — Session 1 Starter

Multi-dimensional eval for the support pipeline:
  1. Classification accuracy — did it identify the right intent?
  2. Retrieval quality — same as Project A
  3. Response quality — faithfulness + correctness
  4. Routing accuracy — should this have been escalated to a human?

All functions are skeletons — we build them in Session 1.

Run: python scripts/eval_harness.py
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

SCRIPT_DIR = os.path.dirname(__file__)


def load_golden_dataset():
    """Load Project B's golden dataset."""
    path = os.path.join(SCRIPT_DIR, "golden_dataset.json")
    if not os.path.exists(path):
        print("No golden_dataset.json found for Project B. Create one first!")
        return []
    with open(path) as f:
        return json.loads(f.read())


# =========================================================================
# CLASSIFICATION METRICS
# =========================================================================

def check_classification(predicted_intent, expected_intent):
    """
    Did the system classify the query correctly?
    Returns True/False.

    TODO: Implement in Session 1.
    """
    pass


# =========================================================================
# ROUTING METRICS
# =========================================================================

def check_routing(predicted_escalation, expected_escalation):
    """
    Should this query have been escalated to a human?
    Did the system make the right routing decision?

    TODO: Implement in Session 1.
    """
    pass


# =========================================================================
# GENERATION METRICS (same pattern as Project A)
# =========================================================================

def judge_faithfulness(query, answer, context):
    """LLM-as-judge: Is the answer grounded in context? TODO: Session 1."""
    pass


def judge_correctness(query, answer, expected_answer):
    """LLM-as-judge: Does it match expected? TODO: Session 1."""
    pass


# =========================================================================
# EVAL RUNNER
# =========================================================================

def run_eval():
    """
    Run multi-dimensional eval:
    1. Classification accuracy
    2. Retrieval quality
    3. Response quality (faithfulness + correctness)
    4. Routing accuracy

    TODO: Implement in Session 1.
    """
    pass


if __name__ == "__main__":
    print("Project B eval harness skeleton loaded.")
    print("Multi-dimensional eval: classification + retrieval + response + routing")
    print("We'll build these together in Session 1.")
