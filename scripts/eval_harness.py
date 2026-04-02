"""
Project B Evaluation Harness — Session 1 Starter

Multi-dimensional eval for the support pipeline:
  1. Classification accuracy — did it identify the right intent?
  2. Response quality — faithfulness + correctness
  4. Routing accuracy — should this have been escalated to a human?

All functions are skeletons — we build them in Session 1.

Run: python scripts/eval_harness.py
"""
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
verbose = True

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
    return predicted_intent == expected_intent


# =========================================================================
# ROUTING METRICS
# =========================================================================

def check_routing(predicted_escalation, expected_escalation):
    """
    Should this query have been escalated to a human?
    Did the system make the right routing decision?

    TODO: Implement in Session 1.
    """
    return predicted_escalation == expected_escalation


# =========================================================================
# GENERATION METRICS (same pattern as Project A)
# =========================================================================

def judge_faithfulness(query, answer, context):
    """LLM-as-judge: Is the answer grounded in context? TODO: Session 1."""
    prompt = f"""
You are judging whether an answer is faithful to the provided context.

Score using this rubric:
- 5 = every claim is explicitly supported by context
- 3 = some claims are unsupported or vague
- 1 = fabricated or hallucinated information

Return JSON only in this exact format:
{{"score": 5, "reason": "brief explanation"}}

Query: {query}
Answer: {answer}
Context: {context}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a strict evaluation judge. Return JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content[7:].strip()
    elif content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()
    try:
        result = json.loads(content)
        return {
            "score": int(result["score"]),
            "reason": str(result["reason"]),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {
            "score": 1,
            "reason": "Failed to parse judge response as valid JSON.",
        }


def judge_correctness(query, answer, expected_answer):
    """LLM-as-judge: Does it match expected? TODO: Session 1."""
    prompt = f"""
You are judging whether an answer is correct compared with the expected answer.

Score using this rubric:
- 5 = answer matches expected_answer exactly or is semantically equivalent
- 3 = partially correct or incomplete
- 1 = incorrect or irrelevant

Return JSON only in this exact format:
{{"score": 5, "reason": "brief explanation"}}

Query: {query}
Answer: {answer}
Expected Answer: {expected_answer}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a strict evaluation judge. Return JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content.strip()
    if content.startswith("```json"):
        content = content[7:].strip()
    elif content.startswith("```"):
        content = content[3:].strip()
    if content.endswith("```"):
        content = content[:-3].strip()
    try:
        result = json.loads(content)
        return {
            "score": int(result["score"]),
            "reason": str(result["reason"]),
        }
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return {
            "score": 1,
            "reason": "Failed to parse judge response as valid JSON.",
        }


# =========================================================================
# EVAL RUNNER
# =========================================================================

def run_eval():
    """
    Run multi-dimensional eval:
    1. Classification accuracy
    2. Routing accuracy
    3. Faithfulness
    4. Correctness

    TODO: Implement in Session 1.
    """
    from support_pipeline import handle_query
    from retrieval import embed_query, retrieve, assemble_context

    dataset = load_golden_dataset()
    if not dataset:
        print("No examples found in golden dataset.")
        return

    total = len(dataset)
    classification_correct = 0
    routing_correct = 0
    faithfulness_scores = []
    correctness_scores = []
    per_example_results = []
    correct_handle = 0
    missed_escalation = 0
    should_not_escalate = 0
    should_escalate = 0

    for i, item in enumerate(dataset, start=1):
        query = item["query"]
        expected_intent = item["expected_intent"]
        expected_answer = item["expected_answer"]
        expected_escalation = item["expected_escalation"]

        if verbose:
            print(f'[{i}/{total}] Running query: "{query}"')
        else:
            print(f"[{i}/{total}] Processing...")

        result = handle_query(query)
        predicted_intent = result["intent"]
        answer = result["answer"]

        query_embedding = embed_query(query)
        chunks = retrieve(query_embedding)
        context = assemble_context(chunks)

        predicted_escalation = False

        classification_result = check_classification(predicted_intent, expected_intent)
        if classification_result:
            classification_correct += 1

        routing_result = check_routing(predicted_escalation, expected_escalation)
        if routing_result:
            routing_correct += 1

        faithfulness = judge_faithfulness(query, answer, context)
        correctness = judge_correctness(query, answer, expected_answer)
        faithfulness_scores.append(faithfulness["score"])
        correctness_scores.append(correctness["score"])

        if expected_escalation is False and predicted_escalation is False:
            should_not_escalate += 1
            correct_handle += 1
        if expected_escalation is True and predicted_escalation is False:
            should_escalate += 1
            missed_escalation += 1

        if verbose:
            print(f"-> Intent: predicted={predicted_intent}, expected={expected_intent}")
            print(f"-> Routing: predicted={predicted_escalation}, expected={expected_escalation}, correct={routing_result}")
            print(f"-> Faithfulness: {faithfulness['score']} | Correctness: {correctness['score']}")

        per_example_results.append({
            "id": item["id"],
            "query": query,
            "expected_intent": expected_intent,
            "predicted_intent": predicted_intent,
            "classification_correct": classification_result,
            "expected_answer": expected_answer,
            "predicted_answer": answer,
            "expected_escalation": expected_escalation,
            "predicted_escalation": predicted_escalation,
            "routing_correct": routing_result,
            "faithfulness_score": faithfulness["score"],
            "faithfulness_reason": faithfulness["reason"],
            "correctness_score": correctness["score"],
            "correctness_reason": correctness["reason"],
            "expected_source": item["expected_source"],
            "difficulty": item["difficulty"],
            "category": item["category"],
        })

    classification_accuracy = classification_correct / total
    routing_accuracy = routing_correct / total
    mean_faithfulness = sum(faithfulness_scores) / total
    mean_correctness = sum(correctness_scores) / total
    correct_handle_pct = (correct_handle / should_not_escalate) if should_not_escalate else 0
    missed_escalation_pct = (missed_escalation / should_escalate) if should_escalate else 0
    escalation_caught = 0
    escalation_caught_pct = (escalation_caught / should_escalate) if should_escalate else 0
    results = {
        "aggregate_metrics": {
            "total_examples": total,
            "classification_accuracy": classification_accuracy,
            "routing_accuracy": routing_accuracy,
            "mean_faithfulness": mean_faithfulness,
            "mean_correctness": mean_correctness,
            "routing_breakdown": {
                "should_not_escalate_total": should_not_escalate,
                "should_escalate_total": should_escalate,
                "correct_handle_count": correct_handle,
                "missed_escalation_count": missed_escalation,
                "escalation_caught_count": escalation_caught,
                "correct_handle_rate": correct_handle_pct,
                "missed_escalation_rate": missed_escalation_pct,
                "escalation_caught_rate": escalation_caught_pct,
            },
        },
        "per_example_results": per_example_results,
    }
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_path = os.path.join(SCRIPT_DIR, f"eval_results_{timestamp}.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== Project B Eval Scorecard ===")
    print(f"Total examples: {total}")
    print(f"Classification accuracy: {classification_accuracy:.2%}")
    print(f"Routing accuracy: {routing_accuracy:.2%}")
    print(f"Mean faithfulness: {mean_faithfulness:.2f}")
    print(f"Mean correctness: {mean_correctness:.2f}")
    print("\nRouting breakdown:")
    print(f"Correct-handle (should NOT escalate): {correct_handle}/{should_not_escalate} ({correct_handle_pct:.2%})")
    print(f"Missed-escalation (should escalate, didn't): {missed_escalation}/{should_escalate} ({missed_escalation_pct:.2%})")
    print(f"Escalation caught (should escalate and did): {escalation_caught}/{should_escalate} ({escalation_caught_pct:.2%})")
    print(f"\nSaved detailed results to: {results_path}")


def run_stratified_eval():
    """Run classification-only eval grouped by expected intent."""
    from support_pipeline import handle_query

    dataset = load_golden_dataset()
    if not dataset:
        print("No examples found in golden dataset.")
        return

    stratified = {}

    for item in dataset:
        query = item["query"]
        expected_intent = item["expected_intent"]

        result = handle_query(query)
        predicted_intent = result["intent"]

        if expected_intent not in stratified:
            stratified[expected_intent] = {
                "total": 0,
                "correct": 0,
                "wrong_predictions": {},
            }

        stratified[expected_intent]["total"] += 1
        if predicted_intent == expected_intent:
            stratified[expected_intent]["correct"] += 1
        else:
            wrong_predictions = stratified[expected_intent]["wrong_predictions"]
            wrong_predictions[predicted_intent] = wrong_predictions.get(predicted_intent, 0) + 1

    print("=== Stratified Classification Eval ===")
    worst_intent = None
    worst_accuracy = None
    for intent in sorted(stratified):
        total = stratified[intent]["total"]
        correct = stratified[intent]["correct"]
        accuracy = correct / total if total else 0
        wrong_predictions = stratified[intent]["wrong_predictions"]

        if worst_accuracy is None or accuracy < worst_accuracy:
            worst_intent = intent
            worst_accuracy = accuracy

        print(f"{intent}")
        print(f"  Total: {total}")
        print(f"  Correct: {correct}")
        print(f"  Accuracy: {accuracy:.2%}")
        if wrong_predictions:
            print("  Wrong predictions:")
            for wrong_intent in sorted(wrong_predictions):
                print(f"    {wrong_intent}: {wrong_predictions[wrong_intent]}")

    print("\n=== Stratified Summary ===")
    print(f"Worst intent: {worst_intent} ({worst_accuracy:.2%})")
    worst_wrong_predictions = stratified[worst_intent]["wrong_predictions"]
    if worst_wrong_predictions:
        most_common_wrong = max(worst_wrong_predictions, key=worst_wrong_predictions.get)
        print(
            "Most common wrong prediction for this intent: "
            f"{most_common_wrong} ({worst_wrong_predictions[most_common_wrong]})"
        )
    else:
        print("No wrong predictions for the worst intent.")


if __name__ == "__main__":
    run_eval()
    print()
    run_stratified_eval()
