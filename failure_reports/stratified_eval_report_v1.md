# Stratified Evaluation Report — Project B (B2.2)

## Overview

This report presents a stratified evaluation of the intent classification component of the support agent system. The goal is to analyze model performance across different intent categories and identify systematic weaknesses.

---

## Overall Performance

* **Total examples:** 50
* **Classification accuracy:** 70.00%
* **Routing accuracy:** 74.00%
* **Mean faithfulness:** 4.96
* **Mean correctness:** 3.96

### Routing Analysis

* **Correct-handle (should NOT escalate):** 37/37 (100%)
* **Missed escalation (should escalate but didn’t):** 13/13 (100%) ❗
* **Escalation caught:** 0/13 (0%)

**Observation:**
The system completely fails to escalate when required. This is a critical production issue.

---

## Stratified Classification Breakdown

| Intent             | Total | Correct | Accuracy |
| ------------------ | ----- | ------- | -------- |
| billing_or_payment | 8     | 4       | 50.00%   |
| general            | 12    | 6       | 50.00%   |
| membership         | 7     | 6       | 85.71%   |
| order_status       | 6     | 4       | 66.67%   |
| product_info       | 8     | 7       | 87.50%   |
| return_or_refund   | 9     | 8       | 88.89%   |

---

## Key Findings

### 1. Worst Performing Intent

* **Intent:** `billing_or_payment`
* **Accuracy:** 50%

Most frequent misclassification:

* Predicted as `return_or_refund` (3 cases)

**Interpretation:**
The classifier is confusing financial issues (billing/payment) with return/refund scenarios. This suggests overlapping language patterns such as “refund”, “charged”, or “payment issue”.

---

### 2. Weak Performance in "general"

* **Accuracy:** 50%

Misclassifications:

* `membership`: 3
* `product_info`: 3

**Interpretation:**
The model struggles to clearly define the boundary of the `general` category and tends to over-specialize queries into other intents.

---

### 3. Strong Performing Intents

* `return_or_refund`: 88.89%
* `product_info`: 87.50%
* `membership`: 85.71%

**Interpretation:**
These intents likely have clearer semantic signals and better representation in the dataset.

---

### 4. No Evidence of "General" Overuse

Contrary to common failure modes, the classifier is **not defaulting excessively to `general`**.

Instead:

* It tends to misclassify into **specific but incorrect intents**
* Example: billing → return/refund

---

### 5. Confusion Patterns

Key confusion observed:

| True Intent        | Predicted As       |
| ------------------ | ------------------ |
| billing_or_payment | return_or_refund   |
| general            | membership/product |
| order_status       | product_info       |

**Insight:**
Errors are **semantic confusions**, not random guesses.

---

## Critical Issue — Escalation Failure

Despite decent classification performance:

* **0% escalation success**
* All escalation-required cases were missed

This indicates:

* Escalation logic is either:

  * not triggered correctly, or
  * not aligned with dataset expectations

**Impact:**
This is a high-risk failure in production (billing disputes, damaged goods, etc.).

---

## Conclusion

The system shows:

* Moderate classification performance (70%)
* Strong performance on well-defined intents
* Significant confusion in financial and general queries
* Complete failure in escalation handling

---

## Recommended Next Steps

1. Improve intent separation:

   * Add more examples distinguishing billing vs refund

2. Redefine or constrain `general` intent:

   * Reduce ambiguity

3. Fix escalation logic:

   * Align rules with dataset definition
   * Add explicit triggers for high-risk cases

4. Introduce confusion-aware evaluation:

   * Track top-2 predictions or similarity scores

---

## Final Assessment

* Classification: **Acceptable but needs refinement**
* Routing: **Partially correct**
* Escalation: **Critical failure — must be fixed**
