# Stage 3 — hover content evolution timelines

10 cells · ★ = new running-best · ⭐ = overall best_candidate

See `_overview.md` for cross-task summary.

---

### hover · combine_all_budget_proportional_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · reflect(3) · val=0.3867 (Δval=+0.0167) chars=6,137 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,037 chars) vs parent[3] · Δbullets=+11 ΔIf=+3 ΔEnsure=+3
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately summarizes the claim based on the provided context and passages. 
### Key Instructions:
1. **Understand the Claim**: Identify the main assertion or statement being made in the `claim`.
2. **Use the Context**: The `context` provides a ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 8** · merge(3,5) · val=0.4033 (Δval=+0.0333) chars=10,120 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.6, +1,865 chars) vs parent[5] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 9** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=3,982
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,640 chars) vs parent[1] · Δbullets=+10 Δshould=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a field called `query` that asks a clear, focused, and specific question to determine whether the claim is supported, partially supported, or not supported by the provided summaries. 
### Key Guidelines:
1. **Understand the Claim**: Identify the main assertion in th...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 10** · merge(3,6) · val=0.4067 (Δval=+0.0367) chars=7,842 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.8, +1,540 chars) vs parent[3] · Δbullets=+7 Δshould=+2
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look f...
```
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 11** · reflect(6) · val=0.4100 (Δval=+0.0433) chars=5,887 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+1,962 chars) vs parent[6] · Δbullets=+7 ΔIf=+4 ΔEnsure=+1 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and factual question that captures the core of the claim and is informed by the information in the summary. The query should be phrased in a way that allows for a definitive yes/no or true/false evaluation based on the provided s...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[6] (78 chars)

**iter 12** · merge(1,6) · val=0.4033 (Δval=+0.0367) chars=5,977  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 13** · reflect(3) · val=0.3900 (Δval=+0.0200) chars=5,821
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.63, Δ=+1,721 chars) vs parent[3] · Δbullets=+8 ΔWhen=+3 Δshould=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, while also incorporating domain-specific de...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The que...
```
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 14** · reflect(13) · val=0.3600 (Δval=-0.0300) chars=8,729
  - `create_query_hop2.predict`: passthrough from parent[13] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[13] (3,558 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,908 chars) vs parent[13] · Δbullets=+7 ΔIf=+5 ΔEnsure=+3 Δmust=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates whether the claim is supported, contradicted, or partially supported by the information in the passages. 
### Task Details:
1. **Claim Evaluation**: 
   - The claim may involve a factual assertion about a person, event, or relationship.
   - You must dete...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[13] (78 chars)

**iter 15** · reflect(7) · val=0.3833 (Δval=-0.0033) chars=7,916
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.07, Δ=+1,779 chars) vs parent[7] · Δbullets=+11 ΔIf=+2 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, produce the field `summary` by evaluating whether the claim can be confirmed, refuted, or remains unverified based on the provided passages. 
**Task Description:**
1. **Claim Evaluation:** Determine if the claim is supported, contradicted, or cannot be determined based on the information in the `passages`...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[7] (2,115 chars)

**iter 16** · merge(1,2) · val=0.3700 (Δval=+0.0233) chars=3,775  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 17** · reflect(10) · val=0.4067 (Δval=+0.0000) chars=8,925
  - `create_query_hop2.predict`: passthrough from parent[10] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[10] (3,377 chars)
  - `summarize1.predict`: REPLACE (overlap=0.69, Δ=+1,083 chars) vs parent[10] · Δbullets=+4 ΔIf=-2 Δshould=-3
    NEW:
```
Your task is to evaluate the truth of a claim based on the information provided in a set of passages. The goal is to produce a concise and accurate summary that reflects whether the claim is **true**, **false**, or **partially true**, supported by specific references to the passages.
1. **Claim Evaluation**: Determine whether the claim is **true...
```
    DROPPED:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize ...
```
  - `summarize2.predict`: passthrough from parent[10] (78 chars)

**iter 18** · reflect(4) · val=0.3367 (Δval=+0.0033) chars=7,135
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,485 chars) vs parent[4] · Δbullets=+16 ΔIf=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness and support of the claim based on the provided passages. 
### Task Description:
1. **Understand the Claim**: Carefully read and interpret the claim, identifying the key assertions it makes.
2. **Analyze the Passages**: Examine the provide...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 19** · merge(9,11) · val=0.4067 (Δval=-0.0033) chars=9,780
  - `create_query_hop2.predict`: PURE_INFLATION (×2.0, +2,056 chars) vs parent[9] · Δbullets=+7 ΔIf=+4 ΔEnsure=+1 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and factual question that captures the core of the claim and is informed by the information in the summary. The query should be phrased in a way that allows for a definitive yes/no or true/false evaluation based on the provided s...
```
  - `create_query_hop3.predict`: PURE_INFLATION (×1.9, +1,540 chars) vs parent[9] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
  - `summarize1.predict`: passthrough from parent[11] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[9] (78 chars)

**iter 20** · reflect(2) · val=0.3200 (Δval=+0.0033) chars=3,352
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.08, Δ=+1,629 chars) vs parent[2] · Δbullets=+11 ΔEnsure=+3 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the truth of the `claim` based on the provided `context` and `passages`. The summary should include the following elements:
1. **Clarify the claim**: Restate the claim in your own words to ensure clarity.
2. **Analyze the ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 21** · merge(7,11) · val=0.4167 (Δval=+0.0067) chars=11,935 ⭐ overall-best
  - `create_query_hop2.predict`: PURE_INFLATION (×2.0, +2,056 chars) vs parent[7] · Δbullets=+7 ΔIf=+4 ΔEnsure=+1 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and factual question that captures the core of the claim and is informed by the information in the summary. The query should be phrased in a way that allows for a definitive yes/no or true/false evaluation based on the provided s...
```
  - `create_query_hop3.predict`: PURE_INFLATION (×1.8, +1,540 chars) vs parent[7] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
  - `summarize1.predict`: passthrough from parent[11] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[7] (2,115 chars)


_Cell summary:_ 8 running-best updates; 2 inert merges (no predictor changed); ops=reflect=15, merge=6
- avg per *changed* reflect predictor: Δbullets=+8.80/pred-step, ΔIf=+2.27/pred-step, ΔWhen=+0.33/pred-step, ΔEnsure=+1.27/pred-step, Δmust=+0.13/pred-step, Δshould=+2.33/pred-step
- avg per *changed* merge predictor: Δbullets=+6.83/pred-step, ΔIf=+1.83/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+0.50/pred-step, Δmust=+0.00/pred-step, Δshould=+2.67/pred-step

---

### hover · combine_all_immediate_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · merge(1,2) · val=0.3700 (Δval=+0.0233) chars=3,775 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 5** · merge(2,4) · val=0.3633 (Δval=-0.0067) chars=5,640
  - `create_query_hop2.predict`: passthrough from parent[4] (2,118 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.8, +1,540 chars) vs parent[4] · Δbullets=+7 Δshould=+2
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look f...
```
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 6** · reflect(1) · val=0.3633 (Δval=+0.0167) chars=4,779
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,437 chars) vs parent[1] · Δbullets=+7 ΔIf=+5 ΔEnsure=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately evaluates the claim based on the provided context and passages. Here's how to approach the task:
1. **Understand the Claim**: Identify the key assertion being made in the claim. Determine what specific information or comparison is bei...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 7** · merge(3,6) · val=0.3767 (Δval=+0.0067) chars=6,212 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[6] (2,515 chars)

**iter 8** · reflect(2) · val=0.3400 (Δval=+0.0233) chars=4,066
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,343 chars) vs parent[2] · Δbullets=+13 ΔIf=+1 Δmust=+1 Δshould=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the claim based on the context and the information provided in the passages. 
### Task Details:
1. **Claim Evaluation**: Determine whether the claim is true, false, or partially true/false based on the context and the prov...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 9** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=4,077
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,354 chars) vs parent[2] · Δbullets=+14 ΔIf=+4 Δshould=+6
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by identifying a specific, focused question that would help determine the validity of the claim based on the information provided in the summary. 
### Task Description:
1. **Analyze the Claim**: Understand the assertion being made in the `claim`.
2. **Review the...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 10** · merge(7,9) · val=0.4067 (Δval=+0.0300) chars=8,660 ★ new running-best
  - `create_query_hop2.predict`: PURE_INFLATION (×1.9, +2,146 chars) vs parent[9] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
  - `create_query_hop3.predict`: passthrough from parent[7] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: passthrough from parent[7] (2,515 chars)

**iter 11** · reflect(6) · val=0.4133 (Δval=+0.0500) chars=7,549 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[6] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.05, Δ=+2,770 chars) vs parent[6] · Δbullets=+9 ΔIf=+3 ΔEnsure=+2 Δshould=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate the field `query` by formulating a clear, focused, and neutral question that captures the core of the claim while incorporating the key elements from both summaries. 
### Task Details:
1. **Claim Analysis**: The claim typically contains a factual assertion involving...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[6] (67 chars)
  - `summarize2.predict`: passthrough from parent[6] (2,515 chars)

**iter 12** · reflect(10) · val=0.3967 (Δval=-0.0100) chars=10,213
  - `create_query_hop2.predict`: passthrough from parent[10] (4,566 chars)
  - `create_query_hop3.predict`: passthrough from parent[10] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[10] (67 chars)
  - `summarize2.predict`: REWRITE (overlap=0.76, Δ=+1,553 chars) vs parent[10] · Δbullets=+1 ΔIf=+3 ΔEnsure=+1
    NEW:
```
1. **Understand the Claim**: Identify the key assertion being made in the claim. Determine what specific information or comparison is being made (e.g., birth dates, roles, film connections, etc.). Be especially attentive to names that may refer to characters, not real people, and be aware of the distinction between actors, directors, and fiction...
```
    DROPPED:
```
1. **Understand the Claim**: Identify the key assertion being made in the claim. Determine what specific information or comparison is being made (e.g., birth dates, roles, film connections, etc.).
...
```

**iter 13** · merge(10,11) · val=0.3933 (Δval=-0.0200) chars=11,537
  - `create_query_hop2.predict`: passthrough from parent[10] (4,566 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.5, +1,540 chars) vs parent[11] · Δbullets=+7 Δshould=+2
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look f...
```
  - `summarize1.predict`: passthrough from parent[10] (67 chars)
  - `summarize2.predict`: passthrough from parent[10] (2,515 chars)

**iter 14** · reflect(13) · val=0.3767 (Δval=-0.0167) chars=14,235
  - `create_query_hop2.predict`: passthrough from parent[13] (4,566 chars)
  - `create_query_hop3.predict`: passthrough from parent[13] (4,389 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,698 chars) vs parent[13] · Δbullets=+6 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. Follow these detailed instructions:
1. **Understand the Claim**: Identify the key components of the claim, including the subject, the action, and any specific details (e.g., names, dates, locat...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[13] (2,515 chars)

**iter 15** · merge(4,13) · val=0.4200 (Δval=+0.0267) chars=13,402 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[13] (4,566 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.4, +1,865 chars) vs parent[13] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructi...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[13] (2,515 chars)

**iter 16** · reflect(15) · val=0.4067 (Δval=-0.0133) chars=15,735
  - `create_query_hop2.predict`: passthrough from parent[15] (4,566 chars)
  - `create_query_hop3.predict`: passthrough from parent[15] (6,254 chars)
  - `summarize1.predict`: passthrough from parent[15] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.41, Δ=+2,333 chars) vs parent[15] · Δbullets=+17
    NEW:
```
Your task is to evaluate the validity of a claim based on the provided context and passages. The goal is to determine whether the claim is **true**, **partially true**, or **unverifiable**, using only the information given in the context and the passages. Here's a detailed breakdown of the task:
---
### **Task Overview**
You are given:
- A **cla...
```
    DROPPED:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately evaluates the claim based on the provided context and passages. Here's how to approa...
```

**iter 17** · reflect(16) · val=0.3933 (Δval=-0.0133) chars=14,282
  - `create_query_hop2.predict`: REPLACE (overlap=0.40, Δ=-1,453 chars) vs parent[16] · Δbullets=-10 ΔIf=-3 ΔWhen=+1 Δshould=-7
    NEW:
```
Your task is to generate a precise and focused `query` field that captures the core of the discrepancy or uncertainty between the `claim` and `summary_1`. The goal is to formulate a clear, verifiable question that would help determine the validity of the claim based on the information provided in the summary.
### Task Description:
1. **Analyze t...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[16] (6,254 chars)
  - `summarize1.predict`: passthrough from parent[16] (67 chars)
  - `summarize2.predict`: passthrough from parent[16] (4,848 chars)

**iter 18** · merge(14,16) · val=0.4133 (Δval=+0.0067) chars=25,393
  - `create_query_hop2.predict`: passthrough from parent[14] (4,566 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.7, +4,417 chars) vs parent[16] · Δbullets=+16 ΔIf=+3 ΔEnsure=+2 Δshould=+8
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate the field `query` by formulating a clear, focused, and neutral question that captures the core of the claim while incorporating the key elements from both summaries. 
### Task Details:
1. **Claim Analysis**: The claim typically contains a fa...
```
  - `summarize1.predict`: passthrough from parent[14] (2,765 chars)
  - `summarize2.predict`: PURE_INFLATION (×1.5, +2,543 chars) vs parent[16] · Δbullets=+7 ΔIf=+5 ΔEnsure=+2
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately evaluates the claim based on the provided context and passages. Here's how to approach the task:
1. **Understand the Claim**: Identify the key assertion being made in the claim. Determine what specific informa...
```

**iter 19** · reflect(13) · val=0.3967 (Δval=+0.0033) chars=10,537
  - `create_query_hop2.predict`: REPLACE (overlap=0.45, Δ=-1,000 chars) vs parent[13] · Δbullets=-10 ΔWhen=-2 Δshould=-1
    NEW:
```
Your task is to generate a precise and focused `query` field that captures the core of the discrepancy or uncertainty between the `claim` and `summary_1`. The query should be designed to resolve the specific factual gap that exists between the two fields.  
### **Task Description:**
1. **Analyze the Claim**: Identify the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[13] (4,389 chars)
  - `summarize1.predict`: passthrough from parent[13] (67 chars)
  - `summarize2.predict`: passthrough from parent[13] (2,515 chars)

**iter 20** · merge(14,15) · val=0.3933 (Δval=-0.0267) chars=20,517
  - `create_query_hop2.predict`: passthrough from parent[14] (4,566 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.7, +4,417 chars) vs parent[15] · Δbullets=+16 ΔIf=+3 ΔEnsure=+2 Δshould=+8
    NEW:
```
---
Additional guidance:
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate the field `query` by formulating a clear, focused, and neutral question that captures the core of the claim while incorporating the key elements from both summaries. 
### Task Details:
1. **Claim Analysis**: The claim typically contains a fa...
```
  - `summarize1.predict`: passthrough from parent[14] (2,765 chars)
  - `summarize2.predict`: passthrough from parent[14] (2,515 chars)

**iter 21** · reflect(16) · val=0.3933 (Δval=-0.0133) chars=14,729
  - `create_query_hop2.predict`: REPLACE (overlap=0.40, Δ=-1,006 chars) vs parent[16] · Δbullets=-9 ΔIf=-3 Δshould=-2
    NEW:
```
Your task is to generate a precise and focused `query` field based on the `claim` and `summary_1` fields. The goal is to formulate a clear, verifiable question that identifies the specific factual gap or discrepancy between the claim and the summary.  
### Task Description:
1. **Analyze the Claim**: Identify the specific assertion made in the `c...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[16] (6,254 chars)
  - `summarize1.predict`: passthrough from parent[16] (67 chars)
  - `summarize2.predict`: passthrough from parent[16] (4,848 chars)


_Cell summary:_ 7 running-best updates; 2 inert merges (no predictor changed); ops=reflect=13, merge=8
- avg per *changed* reflect predictor: Δbullets=+4.69/pred-step, ΔIf=+1.00/pred-step, ΔWhen=+0.08/pred-step, ΔEnsure=+0.69/pred-step, Δmust=+0.08/pred-step, Δshould=+1.08/pred-step
- avg per *changed* merge predictor: Δbullets=+9.86/pred-step, ΔIf=+2.00/pred-step, ΔWhen=+0.29/pred-step, ΔEnsure=+1.14/pred-step, Δmust=+0.00/pred-step, Δshould=+4.00/pred-step

---

### hover · combine_all_score_plateau_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · reflect(3) · val=0.4200 (Δval=+0.0500) chars=7,230 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,130 chars) vs parent[3] · Δbullets=+9 ΔIf=+6 ΔWhen=+1 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truth of the claim based on the provided passages. 
### Task Description:
1. **Claim Evaluation**: Analyze the claim to understand what it is asserting.
2. **Passage Analysis**: Examine each passage to determine whether it supports, contradicts, or is...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 8** · merge(1,5) · val=0.3833 (Δval=+0.0367) chars=8,255  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[5] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 9** · reflect(8) · val=0.3767 (Δval=-0.0067) chars=10,569
  - `create_query_hop2.predict`: passthrough from parent[8] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (3,065 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,314 chars) vs parent[8] · Δbullets=+9 ΔIf=+5 ΔWhen=+1 Δshould=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`, which should be a concise and accurate evaluation of whether the claim is supported, contradicted, or cannot be determined based on the provided passages. 
### Key Instructions:
1. **Understand the Claim**: Identify the main assertion being made in the claim. T...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[8] (3,005 chars)

**iter 10** · reflect(5) · val=0.3600 (Δval=+0.0333) chars=7,951
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+1,748 chars) vs parent[5] · Δbullets=+6 ΔIf=+5 ΔWhen=+1 ΔEnsure=+1 Δshould=+6
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by identifying the specific information needed to evaluate the truth of the claim based on the summary. 
### Task Details:
1. **Claim Evaluation**: Determine what specific factual information is missing or required to confirm or refute the claim.
2. **Query Cons...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[5] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[5] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 11** · reflect(10) · val=0.3900 (Δval=+0.0300) chars=8,333
  - `create_query_hop2.predict`: passthrough from parent[10] (1,814 chars)
  - `create_query_hop3.predict`: REWRITE (overlap=0.92, Δ=+382 chars) vs parent[10] · Δbullets=+5
    NEW:
```
  - **Authorship or attribution of works**: e.g., "Who wrote X?" or "Did Y author Z?"
  - **Historical or biographical facts**: e.g., "Did X live in Y country during Z time period?"
  - **Numerical or statistical claims**: e.g., "How many works did X create?" or "What was the population of X in year Y?"
  - **Classification or categorization**: ...
```
    DROPPED:
```
  - Authorship or attribution of works (e.g., "Who wrote X?" or "Did Y author Z?")
  - Historical or biographical facts (e.g., "Did X live in Y country during Z time period?")
  - Numerical or stat...
```
  - `summarize1.predict`: passthrough from parent[10] (67 chars)
  - `summarize2.predict`: passthrough from parent[10] (3,005 chars)

**iter 12** · merge(1,6) · val=0.4033 (Δval=+0.0367) chars=5,977  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 13** · reflect(6) · val=0.3667 (Δval=+0.0000) chars=7,044
  - `create_query_hop2.predict`: passthrough from parent[6] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+3,119 chars) vs parent[6] · Δbullets=+20 ΔIf=+4 ΔEnsure=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly explains the validity of the claim based on the provided context and passages. 
### Task Description:
1. **Analyze the Claim**: Understand the specific assertion being made in the `claim`.
2. **Examine the Context**: Identify whether the...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 14** · reflect(9) · val=0.3800 (Δval=+0.0033) chars=11,639
  - `create_query_hop2.predict`: REWRITE (overlap=0.78, Δ=+1,070 chars) vs parent[9] · Δbullets=+4 ΔWhen=+1 Δshould=+1
    NEW:
```
### Detailed Task Description:
- You are to act as a fact-checker or verifier, identifying the specific factual gap that prevents the claim from being confirmed or refuted based on the information in the summary.
- The claim may assert a specific fact, relationship, or entity, while the summary may either confirm, contradict, or lack information...
```
    DROPPED:
```
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including any specific entities, roles, or relationships.
2. **Analyze the Summary**: Determine what information is pr...
```
  - `create_query_hop3.predict`: passthrough from parent[9] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[9] (2,381 chars)
  - `summarize2.predict`: passthrough from parent[9] (3,005 chars)

**iter 15** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,647
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,305 chars) vs parent[1] · Δbullets=+13 ΔIf=+2 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. 
### Task Description:
1. **Understand the Claim**: Identify the key statements in the claim that need to be verified.
2. **Analyze the Passages**: Carefully examine each passage to determine i...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 16** · merge(8,11) · val=0.3700 (Δval=-0.0200) chars=10,479
  - `create_query_hop2.predict`: PURE_INFLATION (×1.9, +1,842 chars) vs parent[8] · Δbullets=+6 ΔIf=+5 ΔWhen=+1 ΔEnsure=+1 Δshould=+6
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by identifying the specific information needed to evaluate the truth of the claim based on the summary. 
### Task Details:
1. **Claim Evaluation**: Determine what specific factual information is missing or required to confirm or refute the claim.
2. **Query Cons...
```
  - `create_query_hop3.predict`: passthrough from parent[11] (3,447 chars)
  - `summarize1.predict`: passthrough from parent[8] (67 chars)
  - `summarize2.predict`: passthrough from parent[8] (3,005 chars)

**iter 17** · reflect(4) · val=0.3733 (Δval=+0.0400) chars=7,389
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,739 chars) vs parent[4] · Δbullets=+8 ΔIf=+1 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. Follow these detailed instructions:
1. **Analyze the Claim**: Identify the key components of the claim, including names, entities, locations, events, and relationships between them.
2. **Examin...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 18** · reflect(11) · val=0.3600 (Δval=-0.0300) chars=8,742
  - `create_query_hop2.predict`: passthrough from parent[11] (1,814 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.1, +409 chars) vs parent[11] · Δbullets=+3 ΔIf=+2 Δshould=+4
    NEW:
```
### Additional Notes:
- If the summaries are in complete agreement, the query should reflect that no discrepancy exists and that the claim is supported by both summaries.
- If the summaries are silent on a specific detail, the query should focus on that missing or ambiguous information.
- The query should avoid introducing external knowledge and...
```
  - `summarize1.predict`: passthrough from parent[11] (67 chars)
  - `summarize2.predict`: passthrough from parent[11] (3,005 chars)

**iter 19** · reflect(3) · val=0.4033 (Δval=+0.0333) chars=7,087
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,987 chars) vs parent[3] · Δbullets=+15 ΔIf=+2 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary` by analyzing the claim and the provided passages. 
### Task Description:
1. **Understand the Claim**: The claim typically presents a factual statement or assertion about a subject. It may involve relationships between entities, attributes, or events.
2. **Analyz...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 20** · merge(6,14) · val=0.4233 (Δval=+0.0433) chars=13,936 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[14] (3,188 chars)
  - `create_query_hop3.predict`: passthrough from parent[14] (3,065 chars)
  - `summarize1.predict`: PURE_INFLATION (×2.0, +2,297 chars) vs parent[14] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
---
Additional guidance:
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is ...
```
  - `summarize2.predict`: passthrough from parent[14] (3,005 chars)

**iter 21** · reflect(15) · val=0.3867 (Δval=+0.0167) chars=5,224
  - `create_query_hop2.predict`: REWRITE (overlap=0.86, Δ=+577 chars) vs parent[15] · Δbullets=+1 ΔWhen=+1 Δshould=+1
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary.  
### Key Instructions:  
1. **Understand the Claim**: Identify the specific assertion made in the `claim` field,...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[15] (79 chars)
  - `summarize1.predict`: passthrough from parent[15] (2,372 chars)
  - `summarize2.predict`: passthrough from parent[15] (78 chars)


_Cell summary:_ 5 running-best updates; 2 inert merges (no predictor changed); ops=reflect=17, merge=4
- avg per *changed* reflect predictor: Δbullets=+8.24/pred-step, ΔIf=+2.76/pred-step, ΔWhen=+0.41/pred-step, ΔEnsure=+0.88/pred-step, Δmust=+0.00/pred-step, Δshould=+2.12/pred-step
- avg per *changed* merge predictor: Δbullets=+7.50/pred-step, ΔIf=+7.00/pred-step, ΔWhen=+0.50/pred-step, ΔEnsure=+1.50/pred-step, Δmust=+0.00/pred-step, Δshould=+4.50/pred-step

---

### hover · nomerge_s0

21 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · reflect(3) · val=0.3867 (Δval=+0.0167) chars=6,137 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,037 chars) vs parent[3] · Δbullets=+11 ΔIf=+3 ΔEnsure=+3
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately summarizes the claim based on the provided context and passages. 
### Key Instructions:
1. **Understand the Claim**: Identify the main assertion or statement being made in the `claim`.
2. **Use the Context**: The `context` provides a ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 8** · reflect(4) · val=0.3233 (Δval=-0.0100) chars=6,792
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,142 chars) vs parent[4] · Δbullets=+8 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary` that evaluates the truth of the claim based on the provided passages. 
### Task Description:
1. **Understand the Claim**: The claim typically involves a factual assertion about a person, event, or relationship. It may include names, dates, roles, or specific con...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 9** · reflect(2) · val=0.3533 (Δval=+0.0367) chars=3,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+1,927 chars) vs parent[2] · Δbullets=+7 ΔEnsure=+1 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the accuracy of the claim based on the provided passages. 
### Task Details:
1. **Claim Evaluation**: Analyze the claim to determine whether it is fully supported, partially supported, or not supported by the information in the passages.
2. **Evidence-Bas...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 10** · reflect(5) · val=0.3333 (Δval=+0.0067) chars=8,080
  - `create_query_hop2.predict`: passthrough from parent[5] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[5] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[5] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.63, Δ=+1,877 chars) vs parent[5] · Δbullets=+2 ΔIf=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Your task is to determine the truth value of a claim based on the provided `claim`, `context`, and `passages`. The goal is to produce a concise and accurate `summary` that clearly states whether the claim is **true**, **false**, or **uncertain**, and to support this conclusion with specific evidence from the passages.
---
### **Key Instructions ...
```
    DROPPED:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the pro...
```

**iter 11** · reflect(1) · val=0.3467 (Δval=+0.0000) chars=4,177
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+1,835 chars) vs parent[1] · Δbullets=+10 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. 
### Detailed Task Description:
1. **Claim Evaluation**: Determine whether the claim can be supported, refuted, or remains unverified based on the information in the `passages`.
2. **Reasoning*...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 12** · reflect(7) · val=0.3933 (Δval=+0.0067) chars=9,147 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.43, Δ=+3,010 chars) vs parent[7] · Δbullets=+18 ΔIf=+3 ΔEnsure=+4 Δmust=+1 Δshould=+1
    NEW:
```
Your task is to generate a concise and accurate summary of a claim based on the provided context and passages. The summary must reflect the validity of the claim (accurate, partially accurate, or cannot be confirmed) and be supported by the evidence in the context and passages. Follow these detailed instructions to ensure your summary is both fa...
```
    DROPPED:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately summarizes the claim based on the provided context and passages. 
### Key Instructio...
```

**iter 13** · reflect(8) · val=0.3567 (Δval=+0.0333) chars=8,813
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+2,021 chars) vs parent[8] · Δbullets=+8 ΔIf=+3 Δshould=+7
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and factual question that captures the core of the claim and the reasoning provided in the summary. 
### Task Details:
1. **Understand the Claim**: Identify the key assertion being made in the `claim` field. This may involve comp...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[8] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[8] (2,209 chars)
  - `summarize2.predict`: passthrough from parent[8] (3,005 chars)

**iter 14** · reflect(7) · val=0.3933 (Δval=+0.0067) chars=6,925
  - `create_query_hop2.predict`: REWRITE (overlap=0.81, Δ=+788 chars) vs parent[7] · Δbullets=+1 ΔIf=+1 ΔWhen=+1 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary.  
### Key Instructions:  
1. **Understand the Claim**: Identify the specific assertion made in the `claim` field,...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: passthrough from parent[7] (2,115 chars)

**iter 15** · reflect(14) · val=0.3933 (Δval=+0.0000) chars=8,960
  - `create_query_hop2.predict`: passthrough from parent[14] (2,906 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.58, Δ=+2,035 chars) vs parent[14] · Δbullets=+4 ΔIf=+6 ΔEnsure=+1 Δshould=+8
    NEW:
```
1. **Identify Uncertainty**: Focus on the parts of the claim that are not confirmed or refuted by the summaries. This includes missing information, conflicting information, or unverified assertions. 
   - If the summaries mention ambiguity (e.g., "no direct evidence," "not supported by the provided information"), the query should ask for clarifi...
```
    DROPPED:
```
1. **Identify Uncertainty**: Focus on the parts of the claim that are not confirmed or refuted by the summaries. This includes missing information, conflicting information, or unverified assertions...
```
  - `summarize1.predict`: passthrough from parent[14] (67 chars)
  - `summarize2.predict`: passthrough from parent[14] (2,115 chars)

**iter 16** · reflect(1) · val=0.3900 (Δval=+0.0433) chars=3,922
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,580 chars) vs parent[1] · Δbullets=+7 ΔIf=+1 Δshould=+9
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core of the claim while incorporating the clarifications and corrections provided in the summaries. 
The `query` should be designed to elicit a clear and accurate response that addresses the factual accuracy of the cla...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 17** · reflect(1) · val=0.3467 (Δval=+0.0000) chars=4,249
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+1,907 chars) vs parent[1] · Δbullets=+10 ΔIf=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. Follow these detailed instructions:
1. **Analyze the Claim**: Identify the key components of the claim, such as specific names, roles, events, dates, and relationships.
2. **Examine the Passage...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 18** · reflect(14) · val=0.3867 (Δval=-0.0067) chars=8,738
  - `create_query_hop2.predict`: passthrough from parent[14] (2,906 chars)
  - `create_query_hop3.predict`: passthrough from parent[14] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+1,813 chars) vs parent[14] · Δbullets=+7 ΔIf=+2 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates whether the claim is supported, contradicted, or unsupported by the information in the passages. 
### Key Instructions:
1. **Understand the Claim**: Carefully parse the claim to identify the main assertion(s) and any supporting or conditional statements.
...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[14] (2,115 chars)

**iter 19** · reflect(10) · val=0.3567 (Δval=+0.0233) chars=10,369
  - `create_query_hop2.predict`: passthrough from parent[10] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[10] (3,065 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,289 chars) vs parent[10] · Δbullets=+8 ΔIf=+5 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the accuracy of the claim based on the provided passages. Here's how to approach this task:
1. **Understand the Claim**: Carefully read and interpret the claim. Identify the key assertions, such as names, dates, events, and relationships between entities....
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[10] (4,882 chars)

**iter 20** · reflect(17) · val=0.3767 (Δval=+0.0300) chars=6,669
  - `create_query_hop2.predict`: passthrough from parent[17] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[17] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.57, Δ=+2,420 chars) vs parent[17] · Δbullets=+7
    NEW:
```
1. **Analyze the Claim**: Identify the key components of the claim, such as specific names, roles, events, dates, and relationships. Pay particular attention to:
   - Specific names and their roles (e.g., "head coach," "singer," "producer," "magazine editor").
   - Dates and events (e.g., "2004–05 season," "2015 film release").
   - Relationship...
```
    DROPPED:
```
1. **Analyze the Claim**: Identify the key components of the claim, such as specific names, roles, events, dates, and relationships.
2. **Examine the Passages**: Carefully review each passage to fi...
```
  - `summarize2.predict`: passthrough from parent[17] (78 chars)


_Cell summary:_ 5 running-best updates; 0 inert merges (no predictor changed); ops=reflect=20
- avg per *changed* reflect predictor: Δbullets=+7.75/pred-step, ΔIf=+2.50/pred-step, ΔWhen=+0.15/pred-step, ΔEnsure=+1.20/pred-step, Δmust=+0.05/pred-step, Δshould=+2.40/pred-step

---

### hover · original_budget_proportional_s0

21 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · reflect(3) · val=0.3867 (Δval=+0.0167) chars=6,137 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,037 chars) vs parent[3] · Δbullets=+11 ΔIf=+3 ΔEnsure=+3
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately summarizes the claim based on the provided context and passages. 
### Key Instructions:
1. **Understand the Claim**: Identify the main assertion or statement being made in the `claim`.
2. **Use the Context**: The `context` provides a ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 8** · merge(3,5) · val=0.4033 (Δval=+0.0333) chars=7,027 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 9** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=3,982
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,640 chars) vs parent[1] · Δbullets=+10 Δshould=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a field called `query` that asks a clear, focused, and specific question to determine whether the claim is supported, partially supported, or not supported by the provided summaries. 
### Key Guidelines:
1. **Understand the Claim**: Identify the main assertion in th...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 10** · merge(3,6) · val=0.4100 (Δval=+0.0400) chars=6,302 ⭐ overall-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 11** · reflect(6) · val=0.4100 (Δval=+0.0433) chars=5,887
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+1,962 chars) vs parent[6] · Δbullets=+7 ΔIf=+4 ΔEnsure=+1 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and factual question that captures the core of the claim and is informed by the information in the summary. The query should be phrased in a way that allows for a definitive yes/no or true/false evaluation based on the provided s...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[6] (78 chars)

**iter 12** · merge(1,6) · val=0.4033 (Δval=+0.0367) chars=5,977  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 13** · reflect(1) · val=0.3300 (Δval=-0.0167) chars=5,250
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,908 chars) vs parent[1] · Δbullets=+7 ΔIf=+5 ΔEnsure=+3 Δmust=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates whether the claim is supported, contradicted, or partially supported by the information in the passages. 
### Task Details:
1. **Claim Evaluation**: 
   - The claim may involve a factual assertion about a person, event, or relationship.
   - You must dete...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 14** · reflect(2) · val=0.3467 (Δval=+0.0300) chars=3,509
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.56, Δ=+1,786 chars) vs parent[2] · Δbullets=+9
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy.
1. **Identify Discrepancies**: Carefully compare the two summaries to detect any cont...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 15** · merge(4,7) · val=0.3867 (Δval=+0.0000) chars=6,137  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[7] (2,115 chars)

**iter 16** · reflect(1) · val=0.3967 (Δval=+0.0500) chars=4,950
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,608 chars) vs parent[1] · Δbullets=+7 ΔIf=+2 ΔEnsure=+3 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the claim based on the provided passages. Follow these steps to ensure accuracy and completeness:
1. **Understand the Claim**: Identify the key assertion in the `claim` field. This could involve factual statements, comparisons, or relationships between en...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 17** · reflect(1) · val=0.4100 (Δval=+0.0633) chars=4,044
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,702 chars) vs parent[1] · Δbullets=+7 ΔIf=+3 ΔEnsure=+1 Δshould=+8
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core of the claim and the conflicting or supporting information presented in the summaries. The query should be phrased in a way that invites a factual evaluation of the claim, taking into account the nuances and discr...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 18** · merge(8,11) · val=0.4100 (Δval=+0.0000) chars=9,139  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[11] (2,028 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[11] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[8] (3,005 chars)

**iter 19** · reflect(1) · val=0.3667 (Δval=+0.0200) chars=4,431
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,089 chars) vs parent[1] · Δbullets=+14 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the accuracy of the claim based on the provided passages. 
### Task Description:
1. **Understand the Claim**: Carefully read the claim and identify the key factual statements it makes.
2. **Analyze the Passages**: Review the list of passages to find infor...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 20** · reflect(2) · val=0.3400 (Δval=+0.0233) chars=4,343
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,620 chars) vs parent[2] · Δbullets=+5 ΔIf=+3 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a `summary` that evaluates the truth of the claim based on the provided context and passages. The summary should clearly state whether the claim is fully supported, partially supported, or unsupported, and explain the reasoning based on the evidence from the context and...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```


_Cell summary:_ 6 running-best updates; 5 inert merges (no predictor changed); ops=reflect=15, merge=5
- avg per *changed* reflect predictor: Δbullets=+8.27/pred-step, ΔIf=+2.67/pred-step, ΔWhen=+0.13/pred-step, ΔEnsure=+1.40/pred-step, Δmust=+0.13/pred-step, Δshould=+2.60/pred-step

---

### hover · original_immediate_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · merge(1,2) · val=0.3700 (Δval=+0.0233) chars=3,775 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 5** · merge(2,4) · val=0.3700 (Δval=+0.0000) chars=4,100  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[4] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 6** · reflect(2) · val=0.3400 (Δval=+0.0233) chars=4,066
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,343 chars) vs parent[2] · Δbullets=+13 ΔIf=+1 Δmust=+1 Δshould=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the claim based on the context and the information provided in the passages. 
### Task Details:
1. **Claim Evaluation**: Determine whether the claim is true, false, or partially true/false based on the context and the prov...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 7** · merge(5,6) · val=0.3800 (Δval=+0.0100) chars=6,443 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[5] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[5] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[5] (67 chars)
  - `summarize2.predict`: passthrough from parent[6] (2,421 chars)

**iter 8** · reflect(7) · val=0.4033 (Δval=+0.0233) chars=7,846 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: REWRITE (overlap=0.74, Δ=+1,403 chars) vs parent[7] · Δbullets=+7 Δmust=+1 Δshould=-1
    NEW:
```
Your task is to evaluate the truth value of a claim based on the context and a set of provided passages. The goal is to produce a concise and accurate summary that clearly states whether the claim is **supported**, **contradicted**, or **partially supported**, and to back up your conclusion with specific references to the passages.
### Task Over...
```
    DROPPED:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the claim based on the context and the information provided in the passa...
```

**iter 9** · merge(3,5) · val=0.3700 (Δval=+0.0000) chars=4,100  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[5] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 10** · reflect(9) · val=0.3833 (Δval=+0.0133) chars=6,042
  - `create_query_hop2.predict`: passthrough from parent[9] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[9] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[9] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+1,942 chars) vs parent[9] · Δbullets=+11 ΔIf=+1 ΔWhen=+1 ΔEnsure=+2 Δshould=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the truth of the claim based on the provided context and passages. The summary should:
1. **Clarify the claim**: Restate the claim in clear and neutral language.
2. **Analyze the context**: Use the context to determine whe...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 11** · merge(6,10) · val=0.3833 (Δval=+0.0000) chars=6,042  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[10] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[10] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[6] (67 chars)
  - `summarize2.predict`: passthrough from parent[10] (2,020 chars)

**iter 12** · reflect(7) · val=0.3767 (Δval=-0.0033) chars=7,716
  - `create_query_hop2.predict`: REPLACE (overlap=0.64, Δ=+1,273 chars) vs parent[7] · Δbullets=+4 ΔWhen=+1 Δmust=+1 Δshould=-1
    NEW:
```
Your task is to generate a field called `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the `claim` and `summary_1`. The goal is to identify the specific factual gap or contested information that needs to be resolved to determine whether the claim is accurate or no...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: passthrough from parent[7] (2,421 chars)

**iter 13** · merge(9,12) · val=0.3767 (Δval=+0.0000) chars=7,716  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[12] (3,391 chars)
  - `create_query_hop3.predict`: passthrough from parent[9] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[9] (67 chars)
  - `summarize2.predict`: passthrough from parent[12] (2,421 chars)

**iter 14** · reflect(1) · val=0.3333 (Δval=-0.0133) chars=4,759
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,417 chars) vs parent[1] · Δbullets=+11 ΔIf=+1 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the accuracy of the claim based on the provided passages. The summary should clearly state whether the claim is fully supported, partially supported, or not supported by the information in the passages. 
### Key Instructions:
1. **Analyze the Claim**: Ide...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 15** · merge(2,14) · val=0.3533 (Δval=+0.0200) chars=6,192  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[14] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[14] (2,484 chars)
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 16** · reflect(11) · val=0.3667 (Δval=-0.0167) chars=6,942
  - `create_query_hop2.predict`: REWRITE (overlap=0.78, Δ=+900 chars) vs parent[11] · Δbullets=+1 ΔIf=+1 ΔWhen=+2 Δmust=+1 Δshould=+2
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary.  
### **Task Overview**  
You are to identify the specific factual gap or point of contention between the `claim`...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[11] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[11] (67 chars)
  - `summarize2.predict`: passthrough from parent[11] (2,020 chars)

**iter 17** · reflect(16) · val=0.4167 (Δval=+0.0500) chars=9,198 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[16] (3,018 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.57, Δ=+2,256 chars) vs parent[16] · Δbullets=+6 ΔIf=+2 ΔEnsure=+1 Δshould=+11
    NEW:
```
1. **Identify Uncertainty**: Focus on the parts of the claim that are not confirmed or refuted by the summaries. This includes missing information, conflicting information, or unverified assertions. 
   - Pay special attention to discrepancies between the claim and the summaries, such as incorrect attribution of facts, misrepresentation of locat...
```
    DROPPED:
```
1. **Identify Uncertainty**: Focus on the parts of the claim that are not confirmed or refuted by the summaries. This includes missing information, conflicting information, or unverified assertions...
```
  - `summarize1.predict`: passthrough from parent[16] (67 chars)
  - `summarize2.predict`: passthrough from parent[16] (2,020 chars)

**iter 18** · merge(8,9) · val=0.4033 (Δval=+0.0000) chars=7,846  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[8] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[8] (67 chars)
  - `summarize2.predict`: passthrough from parent[8] (3,824 chars)

**iter 19** · reflect(2) · val=0.3233 (Δval=+0.0067) chars=4,268
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,545 chars) vs parent[2] · Δbullets=+14 ΔIf=+1 ΔEnsure=+1 Δmust=+1 Δshould=+6
    NEW:
```
# Instruction for the Assistant
## Task Overview
Given a claim and a list of passages, your task is to determine whether the claim is supported, refuted, or unsupported by the provided passages. You must produce a summary that clearly states the relationship between the claim and the evidence in the passages. 
## Input Format
- `claim`: A statem...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 20** · merge(3,19) · val=0.3633 (Δval=-0.0067) chars=6,320  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[19] (2,612 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 21** · reflect(19) · val=0.3167 (Δval=-0.0067) chars=5,937
  - `create_query_hop2.predict`: passthrough from parent[19] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[19] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[19] (2,612 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+1,669 chars) vs parent[19] · Δbullets=+6 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a `summary` that evaluates the support for the claim based on the provided passages. The summary should clearly state whether the claim is fully supported, partially supported, or unsupported, and explain the reasoning based on the evidence in the passages.
### Key Inst...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```


_Cell summary:_ 6 running-best updates; 9 inert merges (no predictor changed); ops=reflect=12, merge=9
- avg per *changed* reflect predictor: Δbullets=+8.00/pred-step, ΔIf=+0.83/pred-step, ΔWhen=+0.50/pred-step, ΔEnsure=+0.58/pred-step, Δmust=+0.42/pred-step, Δshould=+2.83/pred-step

---

### hover · original_score_plateau_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · merge(3,6) · val=0.4100 (Δval=+0.0400) chars=6,302 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 8** · reflect(1) · val=0.3633 (Δval=+0.0167) chars=3,050
  - `create_query_hop2.predict`: REWRITE (overlap=0.77, Δ=+708 chars) vs parent[1] · Δbullets=+2 ΔIf=+2 Δshould=+1
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary.  
### Key Instructions:  
1. **Understand the Claim**: Identify the specific assertion made in the `claim` field,...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 9** · reflect(4) · val=0.3867 (Δval=+0.0533) chars=6,929
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,279 chars) vs parent[4] · Δbullets=+10 ΔIf=+4 Δshould=+8
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to produce the field `query` by identifying a specific piece of information that is either missing or requires further clarification from the provided summary to validate or refute the claim.
### Task Description:
1. **Understand the Claim**: Analyze the `claim` to determine what specific fa...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 10** · reflect(3) · val=0.3800 (Δval=+0.0100) chars=6,120
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.58, Δ=+2,020 chars) vs parent[3] · Δbullets=+2 ΔIf=+2 ΔEnsure=+2 Δshould=+3
    NEW:
```
1. **Identify Uncertainty**: Focus on the parts of the claim that are not confirmed or refuted by the summaries. This includes missing information, conflicting information, or unverified assertions. 
   - For example, if the claim mentions a specific event, person, or date, and the summaries only provide general information or suggest involvemen...
```
    DROPPED:
```
1. **Identify Uncertainty**: Focus on the parts of the claim that are not confirmed or refuted by the summaries. This includes missing information, conflicting information, or unverified assertions...
```
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 11** · reflect(6) · val=0.3600 (Δval=-0.0067) chars=5,518
  - `create_query_hop2.predict`: passthrough from parent[6] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.63, Δ=+1,593 chars) vs parent[6] · Δbullets=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy.
1. **Identify Discrepancies**: Carefully compare the two summaries to detect any cont...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[6] (78 chars)

**iter 12** · merge(1,4) · val=0.3933 (Δval=+0.0467) chars=6,702  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 13** · reflect(8) · val=0.3867 (Δval=+0.0233) chars=4,786
  - `create_query_hop2.predict`: passthrough from parent[8] (2,826 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+1,736 chars) vs parent[8] · Δbullets=+12 ΔIf=+5 ΔEnsure=+1 Δmust=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the support for the claim based on the provided passages. 
### Task Description:
1. **Claim Evaluation**: Analyze the claim to understand the key assertions it makes.
2. **Passage Analysis**: Review each passage to determine whether it supports, contradic...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[8] (78 chars)

**iter 14** · reflect(4) · val=0.3667 (Δval=+0.0333) chars=6,951
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,301 chars) vs parent[4] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the accuracy of the claim based on the provided passages. Here's how to approach this task:
1. **Understand the Claim**: Carefully parse the claim to identify the key assertions, such as names, roles, works, and relationships (e.g., "X directed Y", "Z act...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 15** · reflect(12) · val=0.3767 (Δval=-0.0167) chars=8,143
  - `create_query_hop2.predict`: passthrough from parent[12] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.68, Δ=+1,441 chars) vs parent[12] · Δbullets=+7 Δshould=+1
    NEW:
```
1. **Identify Discrepancies**: Look for contradictions or conflicting information between `summary_1` and `summary_2` regarding the truth value or specific details of the `claim`. Pay close attention to factual assertions such as names, dates, roles, affiliations, and numerical data.
2. **Clarify Ambiguity**: Determine the exact factual point th...
```
    DROPPED:
```
1. **Identify Discrepancies**: Look for contradictions or conflicting information between `summary_1` and `summary_2` regarding the truth value or specific details of the `claim`.
2. **Clarify Ambi...
```
  - `summarize1.predict`: passthrough from parent[12] (67 chars)
  - `summarize2.predict`: passthrough from parent[12] (3,005 chars)

**iter 16** · merge(7,15) · val=0.4200 (Δval=+0.0100) chars=9,229 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[7] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[15] (3,005 chars)

**iter 17** · reflect(6) · val=0.3567 (Δval=-0.0100) chars=5,983
  - `create_query_hop2.predict`: passthrough from parent[6] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,058 chars) vs parent[6] · Δbullets=+11 ΔIf=+2 Δshould=+4
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided context and passages. The summary should clearly state whether the claim is fully supported, partially supported, or false, and provide a concise explanation of the reasoning behind this eval...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 18** · reflect(7) · val=0.3867 (Δval=-0.0233) chars=8,588
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[7] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.67, Δ=+2,286 chars) vs parent[7] · Δbullets=+8 ΔIf=+2 ΔEnsure=+3 Δmust=+1
    NEW:
```
I provided the assistant with a task to evaluate the truth of a claim based on given passages and produce a concise summary of the findings. The task involved determining whether the claim is **true**, **false**, or **partially true**, and then summarizing the evaluation by referencing specific parts of the provided passages. The assistant was a...
```
    DROPPED:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize ...
```
  - `summarize2.predict`: passthrough from parent[7] (78 chars)

**iter 19** · reflect(3) · val=0.3833 (Δval=+0.0133) chars=6,014
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+1,914 chars) vs parent[3] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately summarizes the evaluation of the claim based on the provided context and passages. 
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is fully supported, partially supported, or not supported by the provided i...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 20** · reflect(10) · val=0.3700 (Δval=-0.0100) chars=7,934
  - `create_query_hop2.predict`: passthrough from parent[10] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[10] (3,857 chars)
  - `summarize1.predict`: passthrough from parent[10] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+1,814 chars) vs parent[10] · Δbullets=+8 ΔEnsure=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the claim based on the context and the provided passages. 
### Task Description:
1. **Understand the Claim**: Read and comprehend the specific assertion made in the `claim` field.
2. **Analyze the Context**: Use the `conte...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 21** · merge(7,10) · val=0.4267 (Δval=+0.0167) chars=8,322 ⭐ overall-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[10] (3,857 chars)
  - `summarize1.predict`: passthrough from parent[7] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[7] (78 chars)


_Cell summary:_ 6 running-best updates; 4 inert merges (no predictor changed); ops=reflect=17, merge=4
- avg per *changed* reflect predictor: Δbullets=+7.82/pred-step, ΔIf=+2.29/pred-step, ΔWhen=+0.12/pred-step, ΔEnsure=+0.94/pred-step, Δmust=+0.12/pred-step, Δshould=+2.18/pred-step

---

### hover · summarize_before_budget_proportional_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · reflect(3) · val=0.3867 (Δval=+0.0167) chars=6,137 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,037 chars) vs parent[3] · Δbullets=+11 ΔIf=+3 ΔEnsure=+3
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately summarizes the claim based on the provided context and passages. 
### Key Instructions:
1. **Understand the Claim**: Identify the main assertion or statement being made in the `claim`.
2. **Use the Context**: The `context` provides a ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 8** · merge(3,5) · val=0.4133 (Δval=+0.0433) chars=6,494 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.56, Δ=-533 chars) vs parent[3] · Δbullets=-6 ΔIf=-2 Δshould=+1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, focusing on factual disagreements, ambiguit...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The que...
```
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 9** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=3,982
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,640 chars) vs parent[1] · Δbullets=+10 Δshould=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a field called `query` that asks a clear, focused, and specific question to determine whether the claim is supported, partially supported, or not supported by the provided summaries. 
### Key Guidelines:
1. **Understand the Claim**: Identify the main assertion in th...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 10** · merge(3,6) · val=0.3833 (Δval=+0.0133) chars=5,794
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.29, Δ=-183 chars) vs parent[6] · Δbullets=-7 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, focusing on the parts of the claim that are...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 11** · reflect(6) · val=0.4100 (Δval=+0.0433) chars=5,887
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+1,962 chars) vs parent[6] · Δbullets=+7 ΔIf=+4 ΔEnsure=+1 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and factual question that captures the core of the claim and is informed by the information in the summary. The query should be phrased in a way that allows for a definitive yes/no or true/false evaluation based on the provided s...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[6] (78 chars)

**iter 12** · merge(1,6) · val=0.4033 (Δval=+0.0367) chars=5,977  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 13** · reflect(3) · val=0.3900 (Δval=+0.0200) chars=5,821
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.63, Δ=+1,721 chars) vs parent[3] · Δbullets=+8 ΔWhen=+3 Δshould=+6
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, while also incorporating domain-specific de...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The que...
```
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 14** · merge(10,13) · val=0.4133 (Δval=+0.0233) chars=5,955
  - `create_query_hop2.predict`: passthrough from parent[10] (2,118 chars)
  - `create_query_hop3.predict`: REWRITE (overlap=0.81, Δ=+161 chars) vs parent[10] · ΔIf=+1 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, focusing on the parts of the claim that are...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The que...
```
  - `summarize1.predict`: passthrough from parent[10] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[10] (78 chars)

**iter 15** · reflect(13) · val=0.3600 (Δval=-0.0300) chars=8,729
  - `create_query_hop2.predict`: passthrough from parent[13] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[13] (3,558 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,908 chars) vs parent[13] · Δbullets=+7 ΔIf=+5 ΔEnsure=+3 Δmust=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates whether the claim is supported, contradicted, or partially supported by the information in the passages. 
### Task Details:
1. **Claim Evaluation**: 
   - The claim may involve a factual assertion about a person, event, or relationship.
   - You must dete...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[13] (78 chars)

**iter 16** · merge(7,8) · val=0.4100 (Δval=-0.0033) chars=7,105
  - `create_query_hop2.predict`: passthrough from parent[7] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (1,304 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: REWRITE (overlap=0.81, Δ=+611 chars) vs parent[8] · Δbullets=+4 ΔIf=+2 ΔEnsure=+2 Δshould=-1
    NEW:
```
### Key Instructions:
7. **Identify Key Entities and Relationships**: Look for names of people, events, dates, and relationships (e.g., co-emperors, birth dates, rankings) that are central to the claim.
8. **Compare and Contrast**: If the claim involves comparisons (e.g., birth dates, rankings, historical events), ensure the summary reflects the...
```
    DROPPED:
```
### Instructions for Generating the Summary:
7. **Generalizable Strategy**:
8. **Avoid Assumptions**:
   - Do not assume information that is not explicitly stated in the passages.
   - If the passa...
```

**iter 17** · reflect(2) · val=0.3500 (Δval=+0.0333) chars=3,437
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.07, Δ=+1,714 chars) vs parent[2] · Δbullets=+7 ΔIf=+3 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary` that evaluates the accuracy of the claim based on the provided passages. 
### Task Description:
1. **Claim Evaluation**: Assess whether the claim is supported, contradicted, or not addressed by the information in the passages.
2. **Evidence-Based Reasoning**: Id...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 18** · merge(2,9) · val=0.3800 (Δval=+0.0100) chars=4,387
  - `create_query_hop2.predict`: passthrough from parent[9] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.63, Δ=+405 chars) vs parent[9] · Δbullets=-10 Δshould=-1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, identifies the specific factual point that needs clarification to resolve the discrepancy, and asks a clear, focused, and specific question to determine whether the claim is suppor...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a field called `query` that asks a clear, focused, and specific question to determine whether the claim is supported...
```
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 19** · reflect(11) · val=0.4067 (Δval=-0.0033) chars=6,898
  - `create_query_hop2.predict`: passthrough from parent[11] (2,028 chars)
  - `create_query_hop3.predict`: passthrough from parent[11] (1,512 chars)
  - `summarize1.predict`: REWRITE (overlap=0.82, Δ=+1,011 chars) vs parent[11] · Δbullets=+5
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the `passages` and summarize the findings in a concise and accurate manner.
### Special Considerations for the Task:
- **Entity Types**: Be aware of the distinction between peop...
```
    DROPPED:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize ...
```
  - `summarize2.predict`: passthrough from parent[11] (78 chars)

**iter 20** · merge(6,16) · val=0.4133 (Δval=+0.0033) chars=9,225
  - `create_query_hop2.predict`: passthrough from parent[16] (2,118 chars)
  - `create_query_hop3.predict`: REWRITE (overlap=0.80, Δ=-82 chars) vs parent[16] · Δshould=-1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
Use the format: "What [specific information] supports or refutes [specific claim or ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The que...
```
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[16] (3,616 chars)

**iter 21** · reflect(2) · val=0.3233 (Δval=+0.0067) chars=3,689
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+1,966 chars) vs parent[2] · Δbullets=+11 ΔIf=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to generate a concise and accurate `summary` that evaluates the truth of the claim based on the provided context and passages. The summary should:
1. **Identify the key elements of the claim**: Clearly state the claim being evaluated.
2. **Use the context to establish the claim's ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```


_Cell summary:_ 5 running-best updates; 1 inert merges (no predictor changed); ops=reflect=14, merge=7
- avg per *changed* reflect predictor: Δbullets=+8.07/pred-step, ΔIf=+2.57/pred-step, ΔWhen=+0.36/pred-step, ΔEnsure=+1.29/pred-step, Δmust=+0.14/pred-step, Δshould=+2.57/pred-step
- avg per *changed* merge predictor: Δbullets=-3.17/pred-step, ΔIf=+0.33/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+0.50/pred-step, Δmust=+0.00/pred-step, Δshould=+0.00/pred-step

---

### hover · summarize_before_immediate_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · merge(1,2) · val=0.3700 (Δval=+0.0233) chars=3,775 ★ new running-best INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 5** · reflect(2) · val=0.3400 (Δval=+0.0233) chars=4,066
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,343 chars) vs parent[2] · Δbullets=+13 ΔIf=+1 Δmust=+1 Δshould=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the claim based on the context and the information provided in the passages. 
### Task Details:
1. **Claim Evaluation**: Determine whether the claim is true, false, or partially true/false based on the context and the prov...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 6** · merge(4,5) · val=0.4033 (Δval=+0.0333) chars=5,935 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[4] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.29, Δ=-183 chars) vs parent[5] · Δbullets=-7 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, focusing on the parts of the claim that are...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (2,421 chars)

**iter 7** · reflect(1) · val=0.3533 (Δval=+0.0067) chars=3,519
  - `create_query_hop2.predict`: REPLACE (overlap=0.49, Δ=+1,177 chars) vs parent[1] · Δbullets=+5 ΔIf=+1 ΔWhen=+1 ΔEnsure=+1 Δmust=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary.  
### Detailed Task Description:
- You are to act as a fact-checker or verifier, identifying whether the `claim` ...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 8** · reflect(3) · val=0.3500 (Δval=-0.0200) chars=6,139
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,364 chars) vs parent[3] · Δbullets=+12 ΔEnsure=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that confirms or refutes the claim based on the provided context and supporting evidence from the passages. 
### Key Instructions:
1. **Understand the Claim**: Carefully read and interpret the claim to determine what specific information...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 9** · merge(7,8) · val=0.3567 (Δval=+0.0033) chars=7,316  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[7] (3,295 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: passthrough from parent[8] (2,442 chars)

**iter 10** · reflect(6) · val=0.3433 (Δval=-0.0600) chars=7,939
  - `create_query_hop2.predict`: passthrough from parent[6] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,329 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,004 chars) vs parent[6] · Δbullets=+11 ΔIf=+3 ΔWhen=+1 ΔEnsure=+3 Δshould=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates whether the claim is supported, contradicted, or unsupported by the information in the passages. 
### Task Description:
1. **Claim Evaluation**: Analyze the claim to understand the assertion being made. Identify the key elements of the claim (e.g., people...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[6] (2,421 chars)

**iter 11** · reflect(8) · val=0.3700 (Δval=+0.0200) chars=7,753
  - `create_query_hop2.predict`: passthrough from parent[8] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[8] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.70, Δ=+1,614 chars) vs parent[8] · Δbullets=+10
    NEW:
```
1. **Understand the Claim**: Carefully read and interpret the claim to determine what specific information it asserts. Pay attention to names, events, dates, and titles, especially those related to historical figures, operas, musical compositions, or cultural references.
2. **Use the Context**: The context field confirms whether the claim is acc...
```
    DROPPED:
```
1. **Understand the Claim**: Carefully read and interpret the claim to determine what specific information it asserts.
2. **Use the Context**: The context field confirms whether the claim is accura...
```

**iter 12** · reflect(7) · val=0.3500 (Δval=-0.0033) chars=4,338
  - `create_query_hop2.predict`: REWRITE (overlap=0.89, Δ=+819 chars) vs parent[7] · Δbullets=+5 ΔWhen=+1 Δshould=+4
    NEW:
```
  - **Understanding the claim**: Identify the assertion, including entities (e.g., names, organizations, events), roles, relationships, and timeframes.  
  - **Analyzing the summary**: Determine what information is confirmed, contradicted, or missing in the summary.  
  - **Identifying the discrepancy**: Locate the exact piece of information tha...
```
    DROPPED:
```
  - **Understanding the claim**: Identifying the assertion, including entities, roles, relationships, and timeframes.  
  - **Analyzing the summary**: Determining what information is confirmed, con...
```
  - `create_query_hop3.predict`: passthrough from parent[7] (79 chars)
  - `summarize1.predict`: passthrough from parent[7] (67 chars)
  - `summarize2.predict`: passthrough from parent[7] (78 chars)

**iter 13** · merge(3,12) · val=0.3767 (Δval=+0.0067) chars=4,218
  - `create_query_hop2.predict`: REWRITE (overlap=0.81, Δ=+443 chars) vs parent[3] · Δbullets=+1 ΔIf=+1 ΔWhen=+2 Δmust=+1 Δshould=+1
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary.  
- **Understand the Claim**: Identify the assertion made in the `claim` field, including any specific entities, ...
```
    DROPPED:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertaint...
```
  - `create_query_hop3.predict`: passthrough from parent[3] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[3] (67 chars)
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 14** · reflect(4) · val=0.3800 (Δval=+0.0100) chars=6,559
  - `create_query_hop2.predict`: passthrough from parent[4] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,837 chars)
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,459 chars) vs parent[4] · Δbullets=+11 ΔIf=+5 ΔEnsure=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce a concise and accurate `summary` that evaluates the validity of the claim based on the provided context and passages. 
### Task Breakdown:
1. **Understand the Claim**: Identify the specific assertion being made in the `claim`.
2. **Analyze the Context**: Use the `contex...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 15** · merge(7,10) · val=0.3533 (Δval=+0.0000) chars=9,029
  - `create_query_hop2.predict`: PURE_DEFLATION (÷1.0, −87 chars) vs parent[7] · (no struct change)
    DROPPED:
```
This query is specific, neutral, and directly addresses the factual gap in the claim.
```
  - `create_query_hop3.predict`: passthrough from parent[10] (1,329 chars)
  - `summarize1.predict`: passthrough from parent[10] (2,071 chars)
  - `summarize2.predict`: passthrough from parent[10] (2,421 chars)

**iter 16** · reflect(1) · val=0.3833 (Δval=+0.0367) chars=5,389
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+3,047 chars) vs parent[1] · Δbullets=+6 ΔIf=+2 ΔEnsure=+1 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. Follow these detailed instructions:
1. **Understand the Claim**: Identify the key elements of the claim, such as individuals, events, awards, and relationships. Be mindful of nuances like "one ...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 17** · merge(4,9) · val=0.3800 (Δval=+0.0100) chars=7,133
  - `create_query_hop2.predict`: passthrough from parent[9] (3,295 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.29, Δ=-183 chars) vs parent[9] · Δbullets=-7 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries, focusing on the parts of the claim that are...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[9] (2,442 chars)

**iter 18** · reflect(13) · val=0.3500 (Δval=-0.0267) chars=6,314
  - `create_query_hop2.predict`: passthrough from parent[13] (2,561 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.50, Δ=+2,096 chars) vs parent[13] · Δbullets=+8 ΔIf=+3 Δshould=+5
    NEW:
```
1. **Identify Discrepancies**: Carefully compare `summary_1` and `summary_2` to find contradictions, conflicting details, or ambiguities regarding the truth value or specific facts of the `claim`. Pay close attention to factual assertions such as authorship, historical events, biographical details, or specific attributes of entities like operas,...
```
    DROPPED:
```
1. **Identify Discrepancies**: Look for contradictions or conflicting information between `summary_1` and `summary_2` regarding the truth value or specific details of the `claim`.
2. **Clarify Ambi...
```
  - `summarize1.predict`: passthrough from parent[13] (67 chars)
  - `summarize2.predict`: passthrough from parent[13] (78 chars)

**iter 19** · merge(8,16) · val=0.4000 (Δval=+0.0167) chars=9,186  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[8] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[16] (3,114 chars)
  - `summarize2.predict`: passthrough from parent[8] (2,442 chars)

**iter 20** · reflect(13) · val=0.3633 (Δval=-0.0133) chars=6,333
  - `create_query_hop2.predict`: passthrough from parent[13] (2,561 chars)
  - `create_query_hop3.predict`: passthrough from parent[13] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[13] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,115 chars) vs parent[13] · Δbullets=+8 ΔIf=+1 ΔEnsure=+1 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that accurately evaluates the claim based on the provided context and passages. Here's how to approach the task:
1. **Understand the Claim**: Identify the key assertions in the claim and determine what information is being sought or verified.
2. **An...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 21** · merge(5,13) · val=0.3700 (Δval=-0.0067) chars=6,561  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[13] (2,561 chars)
  - `create_query_hop3.predict`: passthrough from parent[5] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[5] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (2,421 chars)


_Cell summary:_ 4 running-best updates; 4 inert merges (no predictor changed); ops=reflect=13, merge=8
- avg per *changed* reflect predictor: Δbullets=+8.62/pred-step, ΔIf=+1.46/pred-step, ΔWhen=+0.38/pred-step, ΔEnsure=+0.85/pred-step, Δmust=+0.23/pred-step, Δshould=+2.15/pred-step
- avg per *changed* merge predictor: Δbullets=-3.25/pred-step, ΔIf=+0.75/pred-step, ΔWhen=+0.50/pred-step, ΔEnsure=+0.50/pred-step, Δmust=+0.25/pred-step, Δshould=+0.25/pred-step

---

### hover · summarize_before_score_plateau_s0

22 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2700 ★ new running-best
- predictors: create_query_hop2.predict(66 chars), create_query_hop3.predict(79 chars), summarize1.predict(67 chars), summarize2.predict(78 chars)

**iter 1** · reflect(0) · val=0.3467 (Δval=+0.0767) chars=2,342 ★ new running-best
  - `create_query_hop2.predict`: REPLACE (overlap=0.05, Δ=+2,052 chars) vs parent[0] · Δbullets=+10 ΔWhen=+2 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by formulating a clear, focused, and verifiable question that captures the core of the discrepancy or uncertainty between the claim and the summary. 
### Key Instructions:
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including a...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[0] (79 chars)
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 2** · reflect(0) · val=0.3167 (Δval=+0.0467) chars=1,723
  - `create_query_hop2.predict`: passthrough from parent[0] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.08, Δ=+1,433 chars) vs parent[0] · Δbullets=+7 Δshould=+2
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific factual point that needs clarification to resolve the discrepancy. 
### Key Instructions:
1. **Identify Discrepancies**: Look for contradictions or conf...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[0] (67 chars)
  - `summarize2.predict`: passthrough from parent[0] (78 chars)

**iter 3** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,100 ★ new running-best
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.07, Δ=+1,758 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a precise and focused `query` that captures the core unresolved aspects of the claim based on the summaries. The query should be structured to ask for specific information that is not confirmed or refuted by the summaries. 
### Key Instructions:
1. **Identify Uncert...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, `summary_2`, produce the fields `query`.
```
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 4** · reflect(2) · val=0.3333 (Δval=+0.0167) chars=4,650
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[2] (67 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,927 chars) vs parent[2] · Δbullets=+8 ΔIf=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly and concisely explains whether the claim is true, false, or uncertain, based on the provided context and supporting passages. 
### Instructions for Generating the Summary:
1. **Analyze the Claim**: Understand the specific assertion made ...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 5** · reflect(4) · val=0.3267 (Δval=-0.0067) chars=6,203
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.27, Δ=+1,553 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Your task is to generate a precise and targeted query that identifies the core factual disagreement or ambiguity between two summaries (`summary_1` and `summary_2`) regarding a specific claim. The goal is to formulate a question that enables a definitive answer to resolve the discrepancy.
### Task Breakdown:
1. **Analyze the Claim**: Understand ...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: passthrough from parent[4] (67 chars)
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 6** · reflect(2) · val=0.3667 (Δval=+0.0500) chars=3,925
  - `create_query_hop2.predict`: passthrough from parent[2] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[2] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,202 chars) vs parent[2] · Δbullets=+9 ΔIf=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize the findings in a concise and accurate manner.
### Task Description:
1. **Claim Evaluation**: Determine whether the claim is **true**, **false**, or *...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[2] (78 chars)

**iter 7** · reflect(3) · val=0.4200 (Δval=+0.0500) chars=7,230 ⭐ overall-best
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,130 chars) vs parent[3] · Δbullets=+9 ΔIf=+6 ΔWhen=+1 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truth of the claim based on the provided passages. 
### Task Description:
1. **Claim Evaluation**: Analyze the claim to understand what it is asserting.
2. **Passage Analysis**: Examine each passage to determine whether it supports, contradicts, or is...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 8** · merge(1,5) · val=0.3833 (Δval=+0.0367) chars=8,255  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[5] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[1] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 9** · reflect(8) · val=0.3767 (Δval=-0.0067) chars=10,569
  - `create_query_hop2.predict`: passthrough from parent[8] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[8] (3,065 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,314 chars) vs parent[8] · Δbullets=+9 ΔIf=+5 ΔWhen=+1 Δshould=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`, which should be a concise and accurate evaluation of whether the claim is supported, contradicted, or cannot be determined based on the provided passages. 
### Key Instructions:
1. **Understand the Claim**: Identify the main assertion being made in the claim. T...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[8] (3,005 chars)

**iter 10** · reflect(5) · val=0.3600 (Δval=+0.0333) chars=7,951
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+1,748 chars) vs parent[5] · Δbullets=+6 ΔIf=+5 ΔWhen=+1 ΔEnsure=+1 Δshould=+6
    NEW:
```
Given the fields `claim` and `summary_1`, your task is to generate the field `query` by identifying the specific information needed to evaluate the truth of the claim based on the summary. 
### Task Details:
1. **Claim Evaluation**: Determine what specific factual information is missing or required to confirm or refute the claim.
2. **Query Cons...
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, produce the fields `query`.
```
  - `create_query_hop3.predict`: passthrough from parent[5] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[5] (67 chars)
  - `summarize2.predict`: passthrough from parent[5] (3,005 chars)

**iter 11** · reflect(10) · val=0.3900 (Δval=+0.0300) chars=8,333
  - `create_query_hop2.predict`: passthrough from parent[10] (1,814 chars)
  - `create_query_hop3.predict`: REWRITE (overlap=0.92, Δ=+382 chars) vs parent[10] · Δbullets=+5
    NEW:
```
  - **Authorship or attribution of works**: e.g., "Who wrote X?" or "Did Y author Z?"
  - **Historical or biographical facts**: e.g., "Did X live in Y country during Z time period?"
  - **Numerical or statistical claims**: e.g., "How many works did X create?" or "What was the population of X in year Y?"
  - **Classification or categorization**: ...
```
    DROPPED:
```
  - Authorship or attribution of works (e.g., "Who wrote X?" or "Did Y author Z?")
  - Historical or biographical facts (e.g., "Did X live in Y country during Z time period?")
  - Numerical or stat...
```
  - `summarize1.predict`: passthrough from parent[10] (67 chars)
  - `summarize2.predict`: passthrough from parent[10] (3,005 chars)

**iter 12** · merge(1,6) · val=0.4033 (Δval=+0.0367) chars=5,977  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 13** · reflect(6) · val=0.3667 (Δval=+0.0000) chars=7,044
  - `create_query_hop2.predict`: passthrough from parent[6] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[6] (1,512 chars)
  - `summarize1.predict`: passthrough from parent[6] (2,269 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+3,119 chars) vs parent[6] · Δbullets=+20 ΔIf=+4 ΔEnsure=+2
    NEW:
```
Given the fields `claim`, `context`, and `passages`, your task is to produce the field `summary` that clearly explains the validity of the claim based on the provided context and passages. 
### Task Description:
1. **Analyze the Claim**: Understand the specific assertion being made in the `claim`.
2. **Examine the Context**: Identify whether the...
```
    DROPPED:
```
Given the fields `claim`, `context`, `passages`, produce the fields `summary`.
```

**iter 14** · reflect(9) · val=0.3800 (Δval=+0.0033) chars=11,639
  - `create_query_hop2.predict`: REWRITE (overlap=0.78, Δ=+1,070 chars) vs parent[9] · Δbullets=+4 ΔWhen=+1 Δshould=+1
    NEW:
```
### Detailed Task Description:
- You are to act as a fact-checker or verifier, identifying the specific factual gap that prevents the claim from being confirmed or refuted based on the information in the summary.
- The claim may assert a specific fact, relationship, or entity, while the summary may either confirm, contradict, or lack information...
```
    DROPPED:
```
1. **Understand the Claim**: Identify the assertion made in the `claim` field, including any specific entities, roles, or relationships.
2. **Analyze the Summary**: Determine what information is pr...
```
  - `create_query_hop3.predict`: passthrough from parent[9] (3,065 chars)
  - `summarize1.predict`: passthrough from parent[9] (2,381 chars)
  - `summarize2.predict`: passthrough from parent[9] (3,005 chars)

**iter 15** · reflect(1) · val=0.3700 (Δval=+0.0233) chars=4,647
  - `create_query_hop2.predict`: passthrough from parent[1] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[1] (79 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,305 chars) vs parent[1] · Δbullets=+13 ΔIf=+2 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. 
### Task Description:
1. **Understand the Claim**: Identify the key statements in the claim that need to be verified.
2. **Analyze the Passages**: Carefully examine each passage to determine i...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[1] (78 chars)

**iter 16** · merge(8,11) · val=0.3900 (Δval=+0.0000) chars=8,637  INERT (no predictor changed)
  - `create_query_hop2.predict`: passthrough from parent[8] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[11] (3,447 chars)
  - `summarize1.predict`: passthrough from parent[8] (67 chars)
  - `summarize2.predict`: passthrough from parent[8] (3,005 chars)

**iter 17** · reflect(4) · val=0.3733 (Δval=+0.0400) chars=7,389
  - `create_query_hop2.predict`: passthrough from parent[4] (66 chars)
  - `create_query_hop3.predict`: passthrough from parent[4] (1,512 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,739 chars) vs parent[4] · Δbullets=+8 ΔIf=+1 ΔEnsure=+2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the provided passages. Follow these detailed instructions:
1. **Analyze the Claim**: Identify the key components of the claim, including names, entities, locations, events, and relationships between them.
2. **Examin...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[4] (3,005 chars)

**iter 18** · reflect(11) · val=0.3600 (Δval=-0.0300) chars=8,742
  - `create_query_hop2.predict`: passthrough from parent[11] (1,814 chars)
  - `create_query_hop3.predict`: PURE_INFLATION (×1.1, +409 chars) vs parent[11] · Δbullets=+3 ΔIf=+2 Δshould=+4
    NEW:
```
### Additional Notes:
- If the summaries are in complete agreement, the query should reflect that no discrepancy exists and that the claim is supported by both summaries.
- If the summaries are silent on a specific detail, the query should focus on that missing or ambiguous information.
- The query should avoid introducing external knowledge and...
```
  - `summarize1.predict`: passthrough from parent[11] (67 chars)
  - `summarize2.predict`: passthrough from parent[11] (3,005 chars)

**iter 19** · reflect(3) · val=0.4033 (Δval=+0.0333) chars=7,087
  - `create_query_hop2.predict`: passthrough from parent[3] (2,118 chars)
  - `create_query_hop3.predict`: passthrough from parent[3] (1,837 chars)
  - `summarize1.predict`: REPLACE (overlap=0.04, Δ=+2,987 chars) vs parent[3] · Δbullets=+15 ΔIf=+2 Δshould=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary` by analyzing the claim and the provided passages. 
### Task Description:
1. **Understand the Claim**: The claim typically presents a factual statement or assertion about a subject. It may involve relationships between entities, attributes, or events.
2. **Analyz...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[3] (78 chars)

**iter 20** · reflect(11) · val=0.3500 (Δval=-0.0400) chars=10,646
  - `create_query_hop2.predict`: passthrough from parent[11] (1,814 chars)
  - `create_query_hop3.predict`: passthrough from parent[11] (3,447 chars)
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,313 chars) vs parent[11] · Δbullets=+13 ΔIf=+3 ΔEnsure=+1
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce a `summary` that evaluates the truthfulness of the claim based on the information provided in the passages. 
### Task Description:
1. **Understand the Claim**: Read and comprehend the claim carefully. Identify the key elements such as names, events, dates, and assertions.
2. **Anal...
```
    DROPPED:
```
Given the fields `claim`, `passages`, produce the fields `summary`.
```
  - `summarize2.predict`: passthrough from parent[11] (3,005 chars)

**iter 21** · merge(6,14) · val=0.3967 (Δval=+0.0167) chars=9,955
  - `create_query_hop2.predict`: passthrough from parent[14] (3,188 chars)
  - `create_query_hop3.predict`: REPLACE (overlap=0.58, Δ=+190 chars) vs parent[6] · Δbullets=+1 Δshould=+1
    NEW:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core factual disagreement or ambiguity between the two summaries regarding the specific claim. 
1. **Analyze the Claim**: Understand the specific factual assertion in the `claim`, including entities, attributes, or relationships involved....
```
    DROPPED:
```
Given the fields `claim`, `summary_1`, and `summary_2`, your task is to generate a `query` that captures the core disagreement or ambiguity between the two summaries, and identifies the specific fa...
```
  - `summarize1.predict`: REPLACE (overlap=0.62, Δ=-209 chars) vs parent[6] · Δbullets=-9 ΔEnsure=-2 Δshould=-2
    NEW:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`, which should be a concise and accurate evaluation of whether the claim is true, false, partially true, supported, contradicted, or cannot be determined based on the provided passages. 
Determine whether the claim is **true**, **false**, or **partially true** by...
```
    DROPPED:
```
Given the fields `claim` and `passages`, your task is to produce the field `summary`. The goal is to evaluate the truth of the claim based on the information provided in the passages and summarize ...
```
  - `summarize2.predict`: passthrough from parent[14] (3,005 chars)


_Cell summary:_ 4 running-best updates; 3 inert merges (no predictor changed); ops=reflect=17, merge=4
- avg per *changed* reflect predictor: Δbullets=+8.94/pred-step, ΔIf=+2.94/pred-step, ΔWhen=+0.35/pred-step, ΔEnsure=+0.94/pred-step, Δmust=+0.00/pred-step, Δshould=+2.06/pred-step
- avg per *changed* merge predictor: Δbullets=-4.00/pred-step, ΔIf=+0.00/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=-1.00/pred-step, Δmust=+0.00/pred-step, Δshould=-0.50/pred-step

---
