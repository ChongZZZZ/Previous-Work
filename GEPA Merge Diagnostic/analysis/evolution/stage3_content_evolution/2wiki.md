# Stage 3 — 2wiki content evolution timelines

10 cells · ★ = new running-best · ⭐ = overall best_candidate

See `_overview.md` for cross-task summary.

---

### 2wiki · combine_all_budget_proportional_s0

20 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2667 (Δval=+0.0167) chars=2,185 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.7500 (Δval=+0.4833) chars=4,091 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.7567 (Δval=+0.0067) chars=5,628 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[0] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(2) · val=0.7500 (Δval=+0.0000) chars=5,867
  - `summarize1.predict`: REWRITE (overlap=0.70, Δ=+996 chars) vs parent[2] · Δbullets=+1 ΔIf=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question.
   - Look for domain-specific terms and names (e.g., "Small Dark Spot," "First French Republic," ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
3. **Extract and Synthesize Information**: Pull out the relevant ...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(3) · val=0.7433 (Δval=-0.0067) chars=8,690
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,992 chars) vs parent[3] · Δbullets=+5 ΔIf=+7 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the two summaries to directly answer the question.  
### Task Details:
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's conte...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · reflect(3) · val=0.7700 (Δval=+0.0200) chars=5,855 ★ new running-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.09, Δ=+1,657 chars) vs parent[3] · Δbullets=+13 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and supporting evidence from the paragraphs. 
The task involves identifying the key information from the `context` and cross-referencing it with the relevant details in the `paragraphs` to form a concise a...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 7** · reflect(1,5) · val=0.7533 (Δval=-0.0167) chars=7,681
  - `summarize1.predict`: PURE_INFLATION (×1.6, +2,472 chars) vs parent[1] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 8** · reflect(2) · val=0.7267 (Δval=-0.0300) chars=6,766
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+2,053 chars) vs parent[2] · Δbullets=+12 ΔEnsure=+3 Δshould=+3
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query` by reformulating the original question into a more direct and focused query based on the information provided in the summary. 
### Key Guidelines:
1. **Identify the core question**: Extract the main subject and the specific information being sought from the or...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 9** · reflect(4,7) · val=0.7567 (Δval=+0.0067) chars=6,462
  - `summarize1.predict`: PURE_INFLATION (×1.5, +3,383 chars) vs parent[7] · Δbullets=+9 ΔIf=+5 ΔEnsure=+2
    NEW:
```
---
Additional guidance:
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any ...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,075 chars)

**iter 10** · reflect(5) · val=0.7467 (Δval=-0.0100) chars=7,196
  - `summarize1.predict`: REPLACE (overlap=0.51, Δ=+1,248 chars) vs parent[5] · Δbullets=+4 Δmust=+1 Δshould=+1
    NEW:
```
**Task Description:**  
The task involves answering a complex question that requires identifying a specific piece of information by analyzing multiple paragraphs. The question typically asks for a term, entity, or concept that connects two or more distinct pieces of information, often involving geographical, historical, or institutional knowledg...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typicall...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 11** · reflect(4,5) · val=0.7600 (Δval=+0.0033) chars=6,288
  - `summarize1.predict`: PURE_INFLATION (×1.7, +2,472 chars) vs parent[4] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 12** · reflect(5) · val=0.7633 (Δval=-0.0067) chars=6,994
  - `summarize1.predict`: passthrough from parent[5] (2,444 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.09, Δ=+1,359 chars) vs parent[5] · Δbullets=+6 Δshould=+2
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query`. 
The task involves transforming the original `question` into a more precise or focused `query` based on the information provided in `summary_1`. The `query` should directly reflect the key information or answer derived from the `summary_1`, and it should be phrased in a way ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 13** · reflect(2,7) · val=0.7533 (Δval=-0.0033) chars=7,569
  - `summarize1.predict`: PURE_INFLATION (×1.4, +2,387 chars) vs parent[7] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
---
Additional guidance:
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Info...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,075 chars)

**iter 14** · merge(11) · val=0.7533 (Δval=-0.0167) chars=11,311
  - `summarize1.predict`: REPLACE (overlap=0.53, Δ=-1,142 chars) vs parent[11] · Δbullets=-9 ΔIf=-1 ΔEnsure=-1 Δmust=+1 Δshould=-2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
### **Task Description**  
The task involves answering a question by extracting specific factual information from a set of provided paragraphs. The question typically requires identify...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typicall...
```
  - `create_query_hop2.predict`: passthrough from parent[11] (69 chars)
  - `summarize2.predict`: passthrough from parent[11] (83 chars)
  - `final_answer.predict`: passthrough from parent[11] (2,075 chars)

**iter 15** · reflect(2,5) · val=0.7300 (Δval=-0.0400) chars=7,745
  - `summarize1.predict`: PURE_INFLATION (×2.0, +2,387 chars) vs parent[5] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
---
Additional guidance:
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Info...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 16** · merge(2) · val=0.7367 (Δval=-0.0167) chars=16,943
  - `summarize1.predict`: REPLACE (overlap=0.60, Δ=+2,561 chars) vs parent[2] · Δbullets=+7 ΔIf=+6 ΔEnsure=+4
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay attention to any specific names, titles, or terms that may refer to particular individuals, organizations, or historical events.
2. **Identify Relevant Information**: Carefully scan through the provided paragrap...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through the provided p...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)


_Cell summary:_ 5 running-best updates; 0 inert merges (no predictor changed); ops=reflect=14, merge=2
- avg per *changed* reflect predictor: Δbullets=+8.79/pred-step, ΔIf=+2.14/pred-step, ΔWhen=+0.07/pred-step, ΔEnsure=+1.21/pred-step, Δmust=+0.07/pred-step, Δshould=+1.71/pred-step
- avg per *changed* merge predictor: Δbullets=-1.00/pred-step, ΔIf=+2.50/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+1.50/pred-step, Δmust=+0.50/pred-step, Δshould=-1.00/pred-step

---

### 2wiki · combine_all_immediate_s0

19 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.4433 (Δval=+0.1933) chars=2,145 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,204 chars) vs parent[0] · Δbullets=+9 ΔIf=+5
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Key Instructions:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, events, dates, locations, etc.) that need to be addressed.
2. **Analyze the Paragraphs...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.4500 (Δval=+0.0067) chars=3,701 ★ new running-best
  - `summarize1.predict`: passthrough from parent[0] (72 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,743 chars) vs parent[0] · Δbullets=+10 ΔIf=+2 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by formulating a clear, concise, and focused question that extracts the specific factual information required to answer the original `question`. 
### Key Instructions:
- **Identify the core factual information** needed to answer the original question. This may involve:
  - Re...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(1,2) · val=0.7367 (Δval=+0.2933) chars=2,604 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[1] (2,276 chars)
  - `create_query_hop2.predict`: passthrough from parent[2] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[1] (83 chars)

**iter 4** · merge(2) · val=0.7267 (Δval=-0.0100) chars=4,160
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[2] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[2] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(4) · val=0.5167 (Δval=+0.0667) chars=5,478
  - `summarize1.predict`: passthrough from parent[4] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.10, Δ=+1,519 chars) vs parent[4] · Δbullets=+5 ΔIf=+2 ΔEnsure=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the correct and consistent information from the summaries to directly answer the question. 
### Key Instructions:
1. **Identify the core question**: Understand what specific piece of information the question is asking for (e.g., a ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · merge(3,5) · val=0.7267 (Δval=-0.0100) chars=6,109
  - `summarize1.predict`: PURE_INFLATION (×1.9, +2,304 chars) vs parent[5] · Δbullets=+9 ΔIf=+5
    NEW:
```
---
Additional guidance:
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Key Instructions:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, events, dates, locations, etc.) that need to be addressed.
2....
```
  - `create_query_hop2.predict`: passthrough from parent[3] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,602 chars)

**iter 7** · reflect(2) · val=0.7867 (Δval=+0.0600) chars=5,159 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,825 chars) vs parent[2] · Δbullets=+8 ΔIf=+1 ΔWhen=+1 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Carefully parse the question to identify key elements such as the subject, the required information, and any contextual clues. Look for embedded questio...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[2] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 8** · merge(6,7) · val=0.7900 (Δval=+0.0033) chars=8,885 ★ new running-best
  - `summarize1.predict`: PURE_INFLATION (×1.6, +2,925 chars) vs parent[6] · Δbullets=+8 ΔIf=+1 ΔWhen=+1 ΔEnsure=+2
    NEW:
```
---
Additional guidance:
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Carefully parse the question to identify key elements such as the subject, the required information, and any contextual clues. ...
```
  - `create_query_hop2.predict`: passthrough from parent[6] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[6] (83 chars)
  - `final_answer.predict`: passthrough from parent[6] (1,602 chars)

**iter 9** · reflect(4) · val=0.7833 (Δval=-0.0033) chars=7,623
  - `summarize1.predict`: passthrough from parent[4] (2,444 chars)
  - `create_query_hop2.predict`: REWRITE (overlap=0.75, Δ=+1,146 chars) vs parent[4] · Δbullets=+3 ΔIf=+3 ΔEnsure=+1 Δshould=+2
    NEW:
```
  - Recognizing the entity or location mentioned in the question (e.g., a person, organization, country, event, or location).
  - Determining the specific attribute or detail being asked (e.g., date, number, name, location, or role).
- **Use the summary to guide the query**: If the summary contains the answer, the query should be phrased to extr...
```
    DROPPED:
```
  - Recognizing the entity or location mentioned in the question (e.g., a person, organization, country, or event).
  - Determining the specific attribute or detail being asked (e.g., date, number,...
```
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 10** · reflect(5,7) · val=0.7933 (Δval=+0.0100) chars=9,017 ★ new running-best
  - `summarize1.predict`: PURE_INFLATION (×1.9, +2,472 chars) vs parent[7] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,602 chars)

**iter 11** · merge(7) · val=0.7933 (Δval=+0.0000) chars=12,843
  - `summarize1.predict`: REWRITE (overlap=0.74, Δ=+1,609 chars) vs parent[7] · ΔIf=+1
    NEW:
```
1. **Understand the Question**: Carefully parse the question to identify key elements such as the subject, the required information, and any contextual clues. Look for embedded questions or multi-part queries. Pay special attention to identifying the relationships between entities (e.g., people, places, organizations) and the specific context re...
```
    DROPPED:
```
1. **Understand the Question**: Carefully parse the question to identify key elements such as the subject, the required information, and any contextual clues. Look for embedded questions or multi-p...
```
  - `create_query_hop2.predict`: passthrough from parent[7] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[7] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (83 chars)

**iter 12** · reflect(3) · val=0.7867 (Δval=-0.0033) chars=10,631
  - `summarize1.predict`: REPLACE (overlap=0.66, Δ=+2,278 chars) vs parent[3] · Δbullets=+8 ΔIf=+7 Δshould=+4
    NEW:
```
### Instruction for the Assistant
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, events, dates, locations, etc.) that need to be addressed. Pay special attention to any ambiguous or potentially conflated references (e.g., names that appear in multiple contexts such as books, people, places...
```
    DROPPED:
```
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, events, dates, locations, etc.) that need to be addressed.
3. **Identify Ambiguity or Confusi...
```
  - `create_query_hop2.predict`: passthrough from parent[3] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 13** · reflect(10,12) · val=0.7700 (Δval=-0.0167) chars=5,203
  - `summarize1.predict`: PURE_INFLATION (×1.9, +4,582 chars) vs parent[10] · Δbullets=+17 ΔIf=+12 Δshould=+4
    NEW:
```
---
Additional guidance:
### Instruction for the Assistant
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Key Instructions:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, events, dates, locations, e...
```
  - `create_query_hop2.predict`: passthrough from parent[10] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[10] (83 chars)
  - `final_answer.predict`: passthrough from parent[10] (1,602 chars)

**iter 14** · reflect(12) · val=0.7733 (Δval=-0.0133) chars=7,080
  - `summarize1.predict`: passthrough from parent[12] (4,554 chars)
  - `create_query_hop2.predict`: passthrough from parent[12] (1,812 chars)
  - `summarize2.predict`: REPLACE (overlap=0.11, Δ=+1,332 chars) vs parent[12] · Δbullets=+6 Δmust=+2 Δshould=+6
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the context and supporting evidence from the paragraphs. 
The task involves identifying the key factual information required to answer the question, using the context as a guide, and then locating and synthesizing the relevant...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[12] (83 chars)


_Cell summary:_ 7 running-best updates; 1 inert merges (no predictor changed); ops=reflect=10, merge=4
- avg per *changed* reflect predictor: Δbullets=+8.44/pred-step, ΔIf=+3.67/pred-step, ΔWhen=+0.11/pred-step, ΔEnsure=+0.67/pred-step, Δmust=+0.22/pred-step, Δshould=+2.44/pred-step
- avg per *changed* merge predictor: Δbullets=+6.75/pred-step, ΔIf=+2.00/pred-step, ΔWhen=+0.25/pred-step, ΔEnsure=+0.75/pred-step, Δmust=+0.00/pred-step, Δshould=+1.00/pred-step

---

### 2wiki · combine_all_score_plateau_s0

20 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2433 (Δval=-0.0067) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2633 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.1933 (Δval=-0.0567) chars=2,091
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[0] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(2) · val=0.4000 (Δval=+0.1500) chars=2,358 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.70, Δ=+996 chars) vs parent[2] · Δbullets=+1 ΔIf=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question.
   - Look for domain-specific terms and names (e.g., "Small Dark Spot," "First French Republic," ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
3. **Extract and Synthesize Information**: Pull out the relevant ...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(3) · val=0.6067 (Δval=+0.2067) chars=2,741 ★ new running-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.09, Δ=+1,629 chars) vs parent[3] · Δbullets=+6 ΔIf=+1 ΔEnsure=+1 Δmust=+1 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the specific factual information required to answer the question. The question typically involves identifying a particular piece of information (e.g., a person, a year, a position, a location, or a type of heritage site) based on c...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · reflect(5) · val=0.5400 (Δval=-0.0667) chars=4,725
  - `summarize1.predict`: REWRITE (overlap=0.79, Δ=+1,077 chars) vs parent[5] · Δbullets=+6 ΔEnsure=+1 Δshould=+6
    NEW:
```
**Task Description:**  
**Key Instructions:**  
1. **Understand the Question:** Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, location, event, or relationship between entities.  
2. **Analyze the Paragraphs:** Review the provided paragraphs to l...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
**Key Instructions:**
1. **Understand the Question:** Carefully read and interpret the question to ...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,712 chars)

**iter 7** · reflect(6) · val=0.7933 (Δval=+0.5300) chars=5,444 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.89, Δ=+833 chars) vs parent[6] · Δbullets=+4 ΔEnsure=+1 Δshould=+3
    NEW:
```
- The task may involve identifying a state's secession date, the number of death row inmates, or the formation of a band or organization, which requires careful cross-referencing of information.  
- The assistant should be able to infer missing information when it is not explicitly stated, such as the capital of a county, the country where a fil...
```
  - `create_query_hop2.predict`: passthrough from parent[6] (69 chars)
  - `summarize2.predict`: passthrough from parent[6] (83 chars)
  - `final_answer.predict`: passthrough from parent[6] (1,712 chars)

**iter 8** · reflect(5) · val=0.3800 (Δval=-0.0200) chars=4,762
  - `summarize1.predict`: REWRITE (overlap=0.80, Δ=+767 chars) vs parent[5] · Δbullets=+4 ΔWhen=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
**Task Description:**  
The task involves answering a complex question by synthesizing information from multiple paragraphs. The question typically requires identifying a specific piece of information, such as a date, entity, or relationship, by analyzing the content of the paragraphs. The answer should be concise, directly address the question,...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typicall...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,712 chars)

**iter 9** · reflect(4) · val=0.4033 (Δval=+0.0033) chars=4,830
  - `summarize1.predict`: REWRITE (overlap=0.86, Δ=+1,128 chars) vs parent[4] · Δbullets=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question. For example, if the question refers to a specific event, person, or place, extract those details....
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural ...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 10** · reflect(8) · val=0.3833 (Δval=-0.0200) chars=7,537
  - `summarize1.predict`: REWRITE (overlap=0.95, Δ=+33 chars) vs parent[8] · (no struct change)
    NEW:
```
- The assistant should be able to recognize and interpret terms related to specific domains, such as "area code," "mountain range," "birthplace," "mayoral election," "school year," "historical events," "geopolitical contexts," or "celestial bodies."  
- The assistant should be able to interpret geographical, historical, and administrative contex...
```
    DROPPED:
```
- The assistant should be able to recognize and interpret terms related to specific domains, such as "prime minister," "French Revolution," "occupation," "planet naming," "synthesis of elements," o...
```
  - `create_query_hop2.predict`: passthrough from parent[8] (69 chars)
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (1,712 chars)

**iter 11** · merge(4,10) · val=0.5233 (Δval=-0.0167) chars=7,197
  - `summarize1.predict`: PURE_INFLATION (×2.0, +3,272 chars) vs parent[4] · Δbullets=+14 ΔIf=+1 ΔWhen=+1 ΔEnsure=+2 Δshould=+8
    NEW:
```
**Task Description:**  
The task involves answering a complex question by synthesizing information from multiple paragraphs. The question typically requires identifying a specific piece of information, such as a date, entity, or relationship, by analyzing the content of the paragraphs. The answer should be concise, directly address the question,...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[10] (1,712 chars)

**iter 12** · reflect(6) · val=0.5300 (Δval=-0.0100) chars=5,030
  - `summarize1.predict`: passthrough from parent[6] (3,521 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.08, Δ=+1,524 chars) vs parent[6] · Δbullets=+5
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by:
1. **Analyzing the question** to identify the key facts, entities, and the specific information being requested.
2. **Using the summary_1** to extract the relevant factual information that directly answers the question. Be mindful of any potential misstatements, ambiguiti...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[6] (83 chars)
  - `final_answer.predict`: passthrough from parent[6] (1,712 chars)

**iter 13** · reflect(11) · val=0.5267 (Δval=-0.0133) chars=6,470
  - `summarize1.predict`: passthrough from parent[11] (6,627 chars)
  - `create_query_hop2.predict`: passthrough from parent[11] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,393 chars) vs parent[11] · Δbullets=+7 ΔIf=+1 ΔEnsure=+2
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and paragraphs. 
### Detailed Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements such as the subject, the action, and the specific details required ...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[11] (1,712 chars)

**iter 14** · reflect(4) · val=0.5433 (Δval=+0.0167) chars=8,246
  - `summarize1.predict`: passthrough from parent[4] (3,355 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.08, Δ=+1,803 chars) vs parent[4] · Δbullets=+9 ΔEnsure=+2
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and supporting information from the paragraphs. 
The task involves identifying key entities and relationships from the question, using the context to guide the interpretation, and then locating relevant fa...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 15** · merge(4) · val=0.5500 (Δval=+0.0067) chars=10,718
  - `summarize1.predict`: REWRITE (overlap=0.88, Δ=+932 chars) vs parent[4] · Δshould=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question. Look for clues about the location, time period, or specific entities involved.
   - Be careful to...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural ...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 16** · reflect(8) · val=0.4833 (Δval=-0.0567) chars=6,691
  - `summarize1.predict`: passthrough from parent[8] (3,211 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,763 chars) vs parent[8] · Δbullets=+8 ΔIf=+5 Δshould=+3
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query`. 
The task involves extracting a specific factual question from a complex or ambiguous original question, using the information provided in the summary. The summary may contain partial or indirect clues, such as references to historical events, geographical locations, politic...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (1,712 chars)

**iter 17** · reflect(7,13) · val=0.7467 (Δval=+0.2067) chars=5,137 ⭐ overall-best
  - `summarize1.predict`: PURE_INFLATION (×1.7, +4,382 chars) vs parent[13] · Δbullets=+20 ΔIf=+1 ΔEnsure=+3 Δshould=+13
    NEW:
```
---
Additional guidance:
**Task Description:**  
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answer should be concise and directly address the ques...
```
  - `create_query_hop2.predict`: passthrough from parent[7] (69 chars)
  - `summarize2.predict`: passthrough from parent[13] (2,476 chars)
  - `final_answer.predict`: passthrough from parent[7] (1,712 chars)

**iter 18** · reflect(8) · val=0.7467 (Δval=+0.0000) chars=7,307
  - `summarize1.predict`: passthrough from parent[8] (3,211 chars)
  - `create_query_hop2.predict`: passthrough from parent[8] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,344 chars) vs parent[8] · Δbullets=+10 ΔIf=+7 Δshould=+1
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and paragraphs. 
### Detailed Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements it is asking about (e.g., names, locations, dates, relationships, e...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[8] (1,712 chars)


_Cell summary:_ 5 running-best updates; 0 inert merges (no predictor changed); ops=reflect=16, merge=2
- avg per *changed* reflect predictor: Δbullets=+7.38/pred-step, ΔIf=+1.56/pred-step, ΔWhen=+0.12/pred-step, ΔEnsure=+1.00/pred-step, Δmust=+0.06/pred-step, Δshould=+2.25/pred-step
- avg per *changed* merge predictor: Δbullets=+7.00/pred-step, ΔIf=+0.50/pred-step, ΔWhen=+0.50/pred-step, ΔEnsure=+1.00/pred-step, Δmust=+0.00/pred-step, Δshould=+4.50/pred-step

---

### 2wiki · nomerge_s0

17 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2433 (Δval=-0.0067) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,639 chars) vs parent[0] · Δbullets=+10 ΔIf=+2 ΔWhen=+2 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the information provided in the paragraphs. Follow these detailed instructions to ensure accuracy and completeness:
1. **Understand the Question**: Carefully read and interpret the question to determine what specific information is being ...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2633 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,204 chars) vs parent[0] · Δbullets=+9 ΔIf=+5
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Key Instructions:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, events, dates, locations, etc.) that need to be addressed.
2. **Analyze the Paragraphs...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.1933 (Δval=-0.0567) chars=2,091
  - `summarize1.predict`: passthrough from parent[0] (72 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,743 chars) vs parent[0] · Δbullets=+10 ΔIf=+2 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by formulating a clear, concise, and focused question that extracts the specific factual information required to answer the original `question`. 
### Key Instructions:
- **Identify the core factual information** needed to answer the original question. This may involve:
  - Re...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(1) · val=0.4000 (Δval=+0.1500) chars=2,358 ★ new running-best
  - `summarize1.predict`: PURE_INFLATION (×1.8, +2,064 chars) vs parent[1] · Δbullets=+7 ΔIf=+6 ΔWhen=+1
    NEW:
```
**Additional Considerations Based on Examples:**
- **Geographical and Historical Context**: When the question involves a location or a historical event, use the provided paragraphs to determine the relevant country, region, or time period. If the information is not explicitly stated, consider the broader historical context (e.g., the Great Ameri...
```
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[1] (83 chars)

**iter 5** · reflect(0) · val=0.6233 (Δval=+0.2233) chars=2,741 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,652 chars) vs parent[0] · Δbullets=+12 ΔIf=+3 ΔEnsure=+2 Δshould=+2
    NEW:
```
Given the fields `question` and `paragraphs`, your task is to produce the field `summary`. The summary should be a concise and accurate answer to the question, derived from the information in the provided paragraphs. 
### Key Instructions:
1. **Identify the question's core components**: Determine the key elements of the question, such as the sub...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 6** · reflect(1) · val=0.5567 (Δval=-0.0667) chars=4,725
  - `summarize1.predict`: REPLACE (overlap=0.68, Δ=+2,069 chars) vs parent[1] · Δbullets=+2 ΔIf=+1 ΔEnsure=+3
    NEW:
```
1. **Understand the Question**: Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, place, event, or relationship based on contextual clues. Pay attention to any references to historical events, geographical locations, or domain-specific terminology.
...
```
    DROPPED:
```
1. **Understand the Question**: Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, place, event, or ...
```
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[1] (83 chars)

**iter 7** · reflect(5) · val=0.7933 (Δval=+0.5300) chars=5,444 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.76, Δ=+1,762 chars) vs parent[5] · Δbullets=+9 ΔIf=+1 ΔEnsure=+2
    NEW:
```
### Niche and Domain-Specific Knowledge to Consider:
- **Coffee Production**: Brazil is the world's largest coffee producer, as shown in the list of countries by coffee production.
- **Supreme Courts and Legal Systems**: Understand the structure of judicial systems in different countries, including the distinction between constitutional courts, ...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (83 chars)

**iter 8** · reflect(5) · val=0.3800 (Δval=-0.0200) chars=4,762
  - `summarize1.predict`: passthrough from parent[5] (2,724 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,730 chars) vs parent[5] · Δbullets=+10 ΔIf=+4 ΔEnsure=+2 Δshould=+4
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query`. 
The task involves transforming a complex or ambiguous question into a more focused, answerable query based on the information provided in the summary. The summary may contain partial or contextual information that helps clarify the original question. 
### Key Instructions:
...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (83 chars)

**iter 9** · reflect(3) · val=0.4033 (Δval=+0.0033) chars=4,830 ⭐ overall-best
  - `summarize1.predict`: passthrough from parent[3] (72 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (1,812 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.06, Δ=+2,609 chars) vs parent[3] · Δbullets=+12 ΔIf=+1 ΔWhen=+1 ΔEnsure=+1 Δmust=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the specific factual information required to answer the question. 
### Task Description:
1. **Understand the Question**: Identify the key elements of the question, including the subject, the context, and the specific information be...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 10** · reflect(5) · val=0.3833 (Δval=-0.0200) chars=7,537
  - `summarize1.predict`: passthrough from parent[5] (2,724 chars)
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.08, Δ=+1,896 chars) vs parent[5] · Δbullets=+11 ΔIf=+3
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and paragraphs. 
### Detailed Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., specific names, locations, dates, or relationships).
2. **Us...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[5] (83 chars)

**iter 11** · reflect(5) · val=0.7000 (Δval=+0.1433) chars=4,929
  - `summarize1.predict`: passthrough from parent[5] (2,724 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,733 chars) vs parent[5] · Δbullets=+8 ΔIf=+4 ΔEnsure=+2 Δshould=+4
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query`. 
The task involves transforming a complex question into a more focused and precise query based on the information provided in the summary. The goal is to extract the essential elements of the question and rephrase it in a way that can be used to retrieve specific factual inf...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (83 chars)

**iter 12** · reflect(1) · val=0.7933 (Δval=+0.0000) chars=7,128
  - `summarize1.predict`: PURE_INFLATION (×1.5, +1,336 chars) vs parent[1] · Δbullets=+9 ΔWhen=+9
    NEW:
```
**Additional Domain-Specific Guidance:**
- When identifying the state where a candidate was a senator, look for direct mentions of the candidate's state of residence or senatorial district in the paragraphs.
- When determining the year a president lost a state, refer to historical election data, especially presidential election years (e.g., 1992...
```
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[1] (83 chars)

**iter 13** · reflect(4) · val=0.4000 (Δval=-0.0033) chars=5,695
  - `summarize1.predict`: PURE_INFLATION (×1.4, +2,018 chars) vs parent[4] · Δbullets=+8 ΔIf=+3
    NEW:
```
**Niche and Domain-Specific Knowledge to Incorporate:**
- **Historical Regimes**: Recognize that the execution of Louis XVI led to the establishment of the First French Republic, and that the First French Republic was a revolutionary regime that replaced the monarchy in France.
- **Planetary Naming Conventions**: Understand that the naming of pl...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 14** · reflect(10) · val=0.6800 (Δval=-0.0200) chars=6,977
  - `summarize1.predict`: REWRITE (overlap=0.76, Δ=+1,439 chars) vs parent[10] · Δbullets=+7
    NEW:
```
- **Colonial History**: Recognize the colonial holdings of European powers in Africa, such as German South West Africa, French Togoland, and British colonies in East Africa.
- **Geographical Knowledge**: Be familiar with regions like Champagne-Ardenne in France, the Ardennes, and their neighboring countries (e.g., Germany).
- **Explorers and Dis...
```
    DROPPED:
```
- **Military Terminology**: Recognize terms like "Reichswehr," "Kriegsmarine," "battleships," and "aircraft carriers" and their historical significance.
```
  - `create_query_hop2.predict`: passthrough from parent[10] (69 chars)
  - `summarize2.predict`: passthrough from parent[10] (1,979 chars)
  - `final_answer.predict`: passthrough from parent[10] (83 chars)

**iter 15** · reflect(4) · val=0.6833 (Δval=+0.0033) chars=8,364
  - `summarize1.predict`: REPLACE (overlap=0.70, Δ=+482 chars) vs parent[4] · Δbullets=-1
    NEW:
```
1. **Understand the Question**: Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, place, event, or relationship based on contextual clues. Pay close attention to terms like "last," "most," or "spouse" to guide your interpretation.
2. **Analyze the P...
```
    DROPPED:
```
1. **Understand the Question**: Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, place, event, or ...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 16** · reflect(5) · val=0.7067 (Δval=+0.0067) chars=7,556
  - `summarize1.predict`: passthrough from parent[5] (2,724 chars)
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,109 chars) vs parent[5] · Δbullets=+9 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the context and supporting information from the paragraphs. 
The task involves the following steps:
1. **Understand the question**: Identify the key elements of the question, such as the subject, the action, and the desired ou...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[5] (83 chars)


_Cell summary:_ 5 running-best updates; 0 inert merges (no predictor changed); ops=reflect=16
- avg per *changed* reflect predictor: Δbullets=+8.25/pred-step, ΔIf=+2.19/pred-step, ΔWhen=+0.81/pred-step, ΔEnsure=+1.06/pred-step, Δmust=+0.06/pred-step, Δshould=+0.94/pred-step

---

### 2wiki · original_budget_proportional_s0

20 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2667 (Δval=+0.0167) chars=2,871 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2500 (Δval=-0.0167) chars=4,229
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.4367 (Δval=+0.1867) chars=2,000 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[0] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(2) · val=0.2567 (Δval=+0.0067) chars=3,176
  - `summarize1.predict`: REWRITE (overlap=0.70, Δ=+996 chars) vs parent[2] · Δbullets=+1 ΔIf=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question.
   - Look for domain-specific terms and names (e.g., "Small Dark Spot," "First French Republic," ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
3. **Extract and Synthesize Information**: Pull out the relevant ...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(3) · val=0.4667 (Δval=+0.2000) chars=4,451 ⭐ overall-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,992 chars) vs parent[3] · Δbullets=+5 ΔIf=+7 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the two summaries to directly answer the question.  
### Task Details:
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's conte...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · reflect(3) · val=0.4967 (Δval=+0.0600) chars=3,050 ★ new running-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.09, Δ=+1,657 chars) vs parent[3] · Δbullets=+13 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and supporting evidence from the paragraphs. 
The task involves identifying the key information from the `context` and cross-referencing it with the relevant details in the `paragraphs` to form a concise a...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 7** · merge(1,5) · val=0.5067 (Δval=+0.0100) chars=5,919 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[5] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 8** · reflect(3) · val=0.3533 (Δval=+0.1033) chars=1,972
  - `summarize1.predict`: REWRITE (overlap=0.76, Δ=+1,242 chars) vs parent[3] · Δbullets=+8 ΔEnsure=+1 Δshould=+8
    NEW:
```
**Task Description:**  
**Key Instructions:**  
1. **Understand the Question:** Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, location, event, or relationship between entities.  
2. **Analyze the Paragraphs:** Review the provided paragraphs to l...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
**Key Instructions:**
1. **Understand the Question:** Carefully read and interpret the question to ...
```
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 9** · merge(2,7) · val=0.5000 (Δval=+0.0033) chars=5,614  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[7] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,075 chars)

**iter 10** · reflect(2) · val=0.4933 (Δval=-0.0033) chars=5,397
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+2,053 chars) vs parent[2] · Δbullets=+12 ΔEnsure=+3 Δshould=+3
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query` by reformulating the original question into a more direct and focused query based on the information provided in the summary. 
### Key Guidelines:
1. **Identify the core question**: Extract the main subject and the specific information being sought from the or...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 11** · merge(7,8) · val=0.4667 (Δval=+0.0000) chars=4,451  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[7] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[7] (69 chars)
  - `summarize2.predict`: passthrough from parent[7] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,075 chars)

**iter 12** · reflect(1) · val=0.2367 (Δval=-0.0133) chars=2,473
  - `summarize1.predict`: passthrough from parent[1] (3,993 chars)
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.10, Δ=+1,533 chars) vs parent[1] · Δbullets=+8 ΔIf=+1 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the most accurate and concise answer to the question based on the provided summaries. 
### Key Instructions:
1. **Understand the Question**: Carefully analyze the question to identify what specific information is being requested (e...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 13** · merge(4,11) · val=0.5067 (Δval=+0.0000) chars=5,919  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[11] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[11] (2,075 chars)

**iter 14** · reflect(8) · val=0.2500 (Δval=+0.0000) chars=2,511
  - `summarize1.predict`: REWRITE (overlap=0.95, Δ=+371 chars) vs parent[8] · Δbullets=+2 Δshould=+2
    NEW:
```
- The assistant should be able to identify locations and states from fictional or animated content (e.g., "Finding Dory") and relate them to real-world geography.  
- The assistant should be able to interpret the political and historical context of fictional or animated settings, such as identifying the real-world country associated with a ficti...
```
  - `create_query_hop2.predict`: passthrough from parent[8] (69 chars)
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (83 chars)

**iter 15** · merge(13,14) · val=0.5067 (Δval=+0.0000) chars=5,919  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[13] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[13] (69 chars)
  - `summarize2.predict`: passthrough from parent[13] (83 chars)
  - `final_answer.predict`: passthrough from parent[13] (2,075 chars)

**iter 16** · reflect(15) · val=0.2333 (Δval=-0.0167) chars=2,306
  - `summarize1.predict`: passthrough from parent[15] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[15] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.07, Δ=+2,327 chars) vs parent[15] · Δbullets=+13 ΔIf=+5 ΔEnsure=+4 Δshould=+1
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and paragraphs. 
### Detailed Task Description:
1. **Identify the key elements of the question**: Determine the main subject, the specific information required, and any contextual clues that may help locat...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[15] (2,075 chars)

**iter 17** · merge(2) · val=0.5000 (Δval=-0.0067) chars=5,614
  - `summarize1.predict`: REPLACE (overlap=0.59, Δ=+1,011 chars) vs parent[2] · Δbullets=+1 ΔIf=+1 Δshould=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay attention to any specific names, events, or locations mentioned in the question.
4. **Handle Ambiguity and Inference**: If the question involves inference or requires understanding of historical, cultural, or li...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
4. **Handle Ambiguity and Inference**: If the question involves i...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 18** · reflect(15,17) · val=0.5000 (Δval=+0.0033) chars=5,363  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[15] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[15] (69 chars)
  - `summarize2.predict`: passthrough from parent[15] (83 chars)
  - `final_answer.predict`: passthrough from parent[15] (2,075 chars)


_Cell summary:_ 6 running-best updates; 6 inert merges (no predictor changed); ops=reflect=12, merge=6
- avg per *changed* reflect predictor: Δbullets=+9.00/pred-step, ΔIf=+2.09/pred-step, ΔWhen=+0.09/pred-step, ΔEnsure=+1.36/pred-step, Δmust=+0.00/pred-step, Δshould=+2.36/pred-step
- avg per *changed* merge predictor: Δbullets=+1.00/pred-step, ΔIf=+1.00/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+0.00/pred-step, Δmust=+0.00/pred-step, Δshould=+1.00/pred-step

---

### 2wiki · original_immediate_s0

20 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2400 (Δval=-0.0100) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2600 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(2) · val=0.2533 (Δval=+0.0133) chars=3,788
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.09, Δ=+1,660 chars) vs parent[2] · Δbullets=+13 ΔIf=+6 ΔEnsure=+1 Δmust=+1 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the most accurate and concise information that directly addresses the question. 
### Task Details:
- The question typically involves a multi-step inference or a specific factual connection between entities, locations, or events.
- ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 4** · merge(1,3) · val=0.2667 (Δval=+0.0067) chars=5,040 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[3] (2,359 chars)
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[3] (1,743 chars)

**iter 5** · reflect(4) · val=0.7400 (Δval=+0.4900) chars=2,557 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.74, Δ=+793 chars) vs parent[4] · Δbullets=+1 ΔIf=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay special attention to any references to specific people, places, events, or terms that may require domain-specific knowledge.
   - Be aware of domain-specific terms like "Fachhochschule" (German for a university ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
4. **Handle Ambiguity and Inference**: If the question involves i...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (1,743 chars)

**iter 6** · merge(5) · val=0.7300 (Δval=-0.0100) chars=5,756
  - `summarize1.predict`: REWRITE (overlap=0.86, Δ=+1,021 chars) vs parent[5] · Δbullets=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay special attention to any references to specific people, places, events, or terms that may require domain-specific knowledge. Look for clues that indicate the need to identify a location, a historical event, a pe...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay special attention to any references to specific people, place...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,743 chars)

**iter 7** · reflect(1) · val=0.2667 (Δval=+0.0133) chars=5,517
  - `summarize1.predict`: passthrough from parent[1] (3,993 chars)
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.07, Δ=+2,087 chars) vs parent[1] · Δbullets=+6 ΔIf=+5 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by identifying the specific factual information that directly answers the question. 
### Key Instructions:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the time period, the location, or the rela...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 8** · merge(4,7) · val=0.2667 (Δval=+0.0000) chars=5,517 ⭐ overall-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[4] (2,359 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,170 chars)

**iter 9** · reflect(8) · val=0.7400 (Δval=+0.0100) chars=7,348
  - `summarize1.predict`: passthrough from parent[8] (2,359 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,792 chars) vs parent[8] · Δbullets=+8 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query` by extracting the core factual claim or answer from the `summary_1` and rephrasing it as a direct, concise statement that answers the `question`.  
### Key Guidelines:
1. **Identify the core factual claim** in `summary_1` that directly answers the `question`. ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (2,170 chars)

**iter 10** · merge(5,7) · val=0.7433 (Δval=+0.0033) chars=8,882 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[5] (3,152 chars)
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,170 chars)

**iter 11** · reflect(7) · val=0.7400 (Δval=+0.0000) chars=4,961
  - `summarize1.predict`: passthrough from parent[7] (3,993 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,657 chars) vs parent[7] · Δbullets=+11 ΔIf=+2 ΔEnsure=+1
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by reformulating the question into a more direct and focused form based on the information provided in the summary. Follow these guidelines:
1. **Identify the core subject and key information** from the question.
2. **Extract relevant details** from the summary that directly ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[7] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,170 chars)

**iter 12** · merge(6,8) · val=0.7400 (Δval=+0.0000) chars=7,348  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[6] (4,173 chars)
  - `create_query_hop2.predict`: passthrough from parent[6] (69 chars)
  - `summarize2.predict`: passthrough from parent[6] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (2,170 chars)

**iter 13** · reflect(0) · val=0.3167 (Δval=+0.0500) chars=7,220
  - `summarize1.predict`: passthrough from parent[0] (72 chars)
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.10, Δ=+1,451 chars) vs parent[0] · Δbullets=+7 Δshould=+7
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by identifying the key factual information required to answer the question. 
The task involves analyzing the question to determine what specific information is needed, using the context to guide the interpretation, and then locating the relevant details in the ...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 14** · merge(8,11) · val=0.7467 (Δval=+0.0067) chars=7,767 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[8] (2,359 chars)
  - `create_query_hop2.predict`: passthrough from parent[11] (1,726 chars)
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (2,170 chars)

**iter 15** · reflect(12) · val=0.7500 (Δval=+0.0033) chars=8,755 ★ new running-best
  - `summarize1.predict`: PURE_INFLATION (×1.3, +1,169 chars) vs parent[12] · Δbullets=+4 ΔIf=+2 ΔEnsure=+2
    NEW:
```
11. **Identify the Subject and Context**: If the question involves a person, locate their birthplace or citizenship from the paragraphs. If it involves a historical event, identify the country or region associated with it.
12. **Map Information to the Question**: Ensure that all information extracted is directly relevant to the question and that...
```
  - `create_query_hop2.predict`: passthrough from parent[12] (69 chars)
  - `summarize2.predict`: passthrough from parent[12] (83 chars)
  - `final_answer.predict`: passthrough from parent[12] (2,170 chars)

**iter 16** · merge(11,15) · val=0.7433 (Δval=+0.0000) chars=8,882  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[15] (5,342 chars)
  - `create_query_hop2.predict`: passthrough from parent[11] (1,726 chars)
  - `summarize2.predict`: passthrough from parent[11] (83 chars)
  - `final_answer.predict`: passthrough from parent[11] (2,170 chars)

**iter 17** · reflect(8) · val=0.7333 (Δval=-0.0100) chars=10,052
  - `summarize1.predict`: REPLACE (overlap=0.60, Δ=+1,288 chars) vs parent[8] · ΔIf=+1 Δshould=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay attention to any specific references to historical events, people, places, or domain-specific terms.
   - Use domain-specific knowledge such as:
     - Recognizing that "Milton's divorce tracts" refer to works b...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
4. **Handle Ambiguity and Inference**: If the question involves i...
```
  - `create_query_hop2.predict`: passthrough from parent[8] (69 chars)
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (2,170 chars)

**iter 18** · merge(10,11) · val=0.7633 (Δval=+0.0133) chars=10,347 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[10] (3,152 chars)
  - `create_query_hop2.predict`: passthrough from parent[11] (1,726 chars)
  - `summarize2.predict`: passthrough from parent[10] (83 chars)
  - `final_answer.predict`: passthrough from parent[10] (2,170 chars)


_Cell summary:_ 8 running-best updates; 7 inert merges (no predictor changed); ops=reflect=10, merge=8
- avg per *changed* reflect predictor: Δbullets=+7.70/pred-step, ΔIf=+2.40/pred-step, ΔWhen=+0.10/pred-step, ΔEnsure=+1.10/pred-step, Δmust=+0.10/pred-step, Δshould=+1.30/pred-step
- avg per *changed* merge predictor: Δbullets=+1.00/pred-step, ΔIf=+0.00/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+0.00/pred-step, Δmust=+0.00/pred-step, Δshould=+0.00/pred-step

---

### 2wiki · original_score_plateau_s0

20 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2433 (Δval=-0.0067) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2633 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.1933 (Δval=-0.0567) chars=2,091
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[0] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(2) · val=0.4000 (Δval=+0.1500) chars=2,358 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.70, Δ=+996 chars) vs parent[2] · Δbullets=+1 ΔIf=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question.
   - Look for domain-specific terms and names (e.g., "Small Dark Spot," "First French Republic," ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
3. **Extract and Synthesize Information**: Pull out the relevant ...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(3) · val=0.6133 (Δval=+0.2133) chars=2,741 ⭐ overall-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,992 chars) vs parent[3] · Δbullets=+5 ΔIf=+7 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the two summaries to directly answer the question.  
### Task Details:
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's conte...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · reflect(3) · val=0.5567 (Δval=-0.0567) chars=4,725
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.09, Δ=+1,657 chars) vs parent[3] · Δbullets=+13 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and supporting evidence from the paragraphs. 
The task involves identifying the key information from the `context` and cross-referencing it with the relevant details in the `paragraphs` to form a concise a...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 7** · reflect(3) · val=0.2400 (Δval=-0.0233) chars=4,263
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.07, Δ=+2,272 chars) vs parent[3] · Δbullets=+12 ΔIf=+2 ΔEnsure=+2 Δmust=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the correct and concise answer to the question based on the information provided in the summaries. 
### Task Description:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the context, ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 8** · reflect(2) · val=0.2667 (Δval=+0.0033) chars=4,479
  - `summarize1.predict`: REPLACE (overlap=0.67, Δ=+2,032 chars) vs parent[2] · Δbullets=+7 ΔIf=+5 ΔEnsure=+4
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Look for specific terms, entities, or relationships that are central to the question.
   - The question may refer to specific historical events, people, places, or organizations.
4. **Handle Ambiguity and Inference*...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
   - The question may refer to specific historical events, people...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 9** · merge(2,7) · val=0.5500 (Δval=-0.0633) chars=6,913  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[7] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,355 chars)

**iter 10** · reflect(7) · val=0.5400 (Δval=-0.0167) chars=6,973
  - `summarize1.predict`: REWRITE (overlap=0.75, Δ=+1,646 chars) vs parent[7] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2 Δshould=+6
    NEW:
```
**Task Description:**  
**Key Instructions:**  
1. **Understand the Question:** Carefully read and interpret the question to determine what specific information is being requested. The question may involve identifying a person, location, event, or relationship between entities.  
2. **Analyze the Paragraphs:** Review the provided paragraphs to l...
```
    DROPPED:
```
**Task Description:**
**Key Instructions:**
1. **Understand the Question:** Carefully read and interpret the question to determine what specific information is being requested. The question may inv...
```
  - `create_query_hop2.predict`: passthrough from parent[7] (69 chars)
  - `summarize2.predict`: passthrough from parent[7] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,355 chars)

**iter 11** · reflect(5) · val=0.5567 (Δval=+0.0000) chars=6,141
  - `summarize1.predict`: passthrough from parent[5] (2,444 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.08, Δ=+1,645 chars) vs parent[5] · Δbullets=+8 ΔEnsure=+2 Δshould=+3
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query` by reformulating the `question` into a more concise and focused version that retains all the key elements necessary to retrieve the correct answer from the provided `summary_1`.  
### Key Guidelines:
1. **Identify the core components** of the question: the sub...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 12** · reflect(8) · val=0.5600 (Δval=+0.0100) chars=8,857
  - `summarize1.predict`: PURE_INFLATION (×1.2, +976 chars) vs parent[8] · Δbullets=+4 ΔIf=+2
    NEW:
```
16. **Understand County and Regional Boundaries**: Be aware that in some contexts, such as in the United States, counties may share borders with other counties, and that these boundaries may be described in the text through geographical features or administrative descriptions.
17. **Identify Cities and Their Counties**: Recognize that cities are...
```
  - `create_query_hop2.predict`: passthrough from parent[8] (69 chars)
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (83 chars)

**iter 13** · reflect(11,12) · val=0.5433 (Δval=-0.0067) chars=7,787  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[11] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[11] (1,714 chars)
  - `summarize2.predict`: passthrough from parent[11] (83 chars)
  - `final_answer.predict`: passthrough from parent[11] (2,075 chars)

**iter 14** · reflect(12) · val=0.5500 (Δval=-0.0067) chars=8,067
  - `summarize1.predict`: passthrough from parent[12] (5,367 chars)
  - `create_query_hop2.predict`: passthrough from parent[12] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.08, Δ=+1,793 chars) vs parent[12] · Δbullets=+6 ΔIf=+1 ΔEnsure=+2
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by identifying the key factual information required to answer the question. The task involves:
1. **Understanding the Question**: Identify the core information being asked, such as a specific event, person, place, or date.
2. **Using the Context**: Leverage the...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[12] (83 chars)

**iter 15** · reflect(12) · val=0.5600 (Δval=-0.0533) chars=4,496
  - `summarize1.predict`: PURE_INFLATION (×1.2, +1,005 chars) vs parent[12] · Δbullets=+2
    NEW:
```
20. **Be Aware of Specific Historical and Cultural Contexts**: Recognize specific historical and cultural references, such as:
   - The "yellow bell" plant being native to South America and mentioned in paragraph [3].
   - The connection between Tito's visits and the U.S. state, as well as the organization employing Sinha Basnayake.
   - The dat...
```
  - `create_query_hop2.predict`: passthrough from parent[12] (69 chars)
  - `summarize2.predict`: passthrough from parent[12] (83 chars)
  - `final_answer.predict`: passthrough from parent[12] (83 chars)

**iter 16** · merge(15) · val=0.5367 (Δval=-0.0233) chars=9,731
  - `summarize1.predict`: PURE_INFLATION (×1.1, +953 chars) vs parent[15] · Δbullets=+4 ΔIf=+1 ΔWhen=+3 ΔEnsure=+2
    NEW:
```
22. **Identify the U.S. State Visited by Tito**: When the question refers to a U.S. state visited by Tito, refer to specific mentions of his visits, such as his visit to New York in the late 1970s, as described in paragraph [11].
23. **Identify the Organization Employing Sinha Basnayake**: When the question refers to an organization employing Si...
```
  - `create_query_hop2.predict`: passthrough from parent[15] (69 chars)
  - `summarize2.predict`: passthrough from parent[15] (83 chars)
  - `final_answer.predict`: passthrough from parent[15] (83 chars)

**iter 17** · reflect(4,10) · val=0.7367 (Δval=+0.1233) chars=3,319 ★ new running-best INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[10] (4,090 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[10] (2,355 chars)

**iter 18** · merge(2) · val=0.5600 (Δval=+0.0000) chars=8,857
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,783 chars) vs parent[2] · Δbullets=+9 ΔEnsure=+1
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query` by rephrasing the original question in a clearer, more direct form, while preserving the essential factual elements and context provided in the summary. The goal is to create a query that is easier to understand and more likely to yield a precise answer from a...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 19** · reflect(4) · val=0.6833 (Δval=+0.1333) chars=8,308
  - `summarize1.predict`: passthrough from parent[4] (3,355 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.10, Δ=+1,539 chars) vs parent[4] · Δbullets=+7 ΔEnsure=+1 Δshould=+2
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the question and the two summaries.  
### Key Instructions:
1. **Understand the question**: Identify the specific information being asked, which may involve factual knowledge about geography, history, culture...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```


_Cell summary:_ 5 running-best updates; 3 inert merges (no predictor changed); ops=reflect=16, merge=3
- avg per *changed* reflect predictor: Δbullets=+7.86/pred-step, ΔIf=+2.14/pred-step, ΔWhen=+0.07/pred-step, ΔEnsure=+1.36/pred-step, Δmust=+0.07/pred-step, Δshould=+1.50/pred-step
- avg per *changed* merge predictor: Δbullets=+6.50/pred-step, ΔIf=+0.50/pred-step, ΔWhen=+1.50/pred-step, ΔEnsure=+1.50/pred-step, Δmust=+0.00/pred-step, Δshould=+0.00/pred-step

---

### 2wiki · summarize_before_budget_proportional_s0

21 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2433 (Δval=-0.0067) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2633 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.1933 (Δval=-0.0567) chars=2,091
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[0] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(2) · val=0.4000 (Δval=+0.1500) chars=2,358 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.70, Δ=+996 chars) vs parent[2] · Δbullets=+1 ΔIf=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question.
   - Look for domain-specific terms and names (e.g., "Small Dark Spot," "First French Republic," ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
3. **Extract and Synthesize Information**: Pull out the relevant ...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(3) · val=0.6067 (Δval=+0.2067) chars=2,741 ★ new running-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,992 chars) vs parent[3] · Δbullets=+5 ΔIf=+7 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the two summaries to directly answer the question.  
### Task Details:
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's conte...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · merge(3) · val=0.4033 (Δval=+0.0033) chars=5,557
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.09, Δ=+1,657 chars) vs parent[3] · Δbullets=+13 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and supporting evidence from the paragraphs. 
The task involves identifying the key information from the `context` and cross-referencing it with the relevant details in the `paragraphs` to form a concise a...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 7** · reflect(1,5) · val=0.5400 (Δval=-0.0667) chars=4,725
  - `summarize1.predict`: REPLACE (overlap=0.37, Δ=-823 chars) vs parent[1] · Δbullets=-4 ΔIf=-2 ΔWhen=-1 ΔEnsure=-1 Δshould=+3
    NEW:
```
**Task Description:**  
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answer should be concise and directly address the question, drawing on the rele...
```
    DROPPED:
```
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred....
```
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 8** · merge(3) · val=0.5367 (Δval=-0.0700) chars=5,940
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,850 chars) vs parent[3] · Δbullets=+11 ΔEnsure=+1 Δmust=+1 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by identifying the specific factual information required to answer the question. 
### Task Details:
- The question typically involves a multi-step reasoning process, often requiring the identification of a country, person, or entity based on a c...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 9** · reflect(2,7) · val=0.5367 (Δval=+0.0000) chars=7,471
  - `summarize1.predict`: REPLACE (overlap=0.33, Δ=-1,484 chars) vs parent[2] · Δbullets=-8 ΔIf=-3 ΔEnsure=-1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to determine the specific information requested, and analyze the paragraphs to locate relevant information. Identify key entities and their relationships, and draw logical connections acros...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Id...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[7] (2,075 chars)

**iter 10** · merge(9) · val=0.5367 (Δval=-0.0700) chars=5,940
  - `summarize1.predict`: REPLACE (overlap=0.52, Δ=+1,361 chars) vs parent[9] · Δbullets=+10 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to determine the specific information requested, and analyze the paragraphs to locate relevant information. Identify key entities and their relationships, and draw logical connections acros...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to determine the specific information r...
```
  - `create_query_hop2.predict`: passthrough from parent[9] (69 chars)
  - `summarize2.predict`: passthrough from parent[9] (83 chars)
  - `final_answer.predict`: passthrough from parent[9] (2,075 chars)

**iter 11** · reflect(7,8) · val=0.7500 (Δval=+0.2133) chars=7,802 ★ new running-best
  - `summarize1.predict`: passthrough from parent[7] (3,170 chars)
  - `create_query_hop2.predict`: passthrough from parent[7] (69 chars)
  - `summarize2.predict`: passthrough from parent[7] (83 chars)
  - `final_answer.predict`: PURE_INFLATION (×1.4, +919 chars) vs parent[7] · Δbullets=+1 Δmust=+1 Δshould=+1
    NEW:
```
- **Additional Guidance**:
  - The question typically involves a multi-step reasoning process, often requiring the identification of a country, person, or entity based on a chain of contextual clues.
  - The summaries provide direct or indirect information that can be used to infer the correct answer. These summaries may contain the same or slig...
```

**iter 12** · merge(2) · val=0.7400 (Δval=-0.0100) chars=9,270
  - `summarize1.predict`: REPLACE (overlap=0.67, Δ=+2,032 chars) vs parent[2] · Δbullets=+7 ΔIf=+5 ΔEnsure=+4
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Look for specific terms, entities, or relationships that are central to the question.
   - The question may refer to specific historical events, people, places, or organizations.
4. **Handle Ambiguity and Inference*...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
   - The question may refer to specific historical events, people...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 13** · reflect(4,8) · val=0.5267 (Δval=-0.0133) chars=6,379
  - `summarize1.predict`: REPLACE (overlap=0.13, Δ=-1,353 chars) vs parent[8] · Δbullets=-10 ΔIf=-1 Δshould=-4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to identify the key elements, such as the subject, required data, and context. Analyze the paragraphs to locate relevant information, being mindful of specific historical, geographical, or ...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typicall...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (1,933 chars)

**iter 14** · merge(10) · val=0.5533 (Δval=+0.0133) chars=7,673
  - `summarize1.predict`: PURE_INFLATION (×1.9, +1,954 chars) vs parent[10] · Δbullets=+11 ΔWhen=+5 ΔEnsure=+1
    NEW:
```
**Additional Domain-Specific Guidelines:**
- When dealing with historical events, ensure you distinguish between the actual events and any claims or interpretations that may be present in the text.
- When identifying the country where a person was educated, look for direct mentions of the educational institution and its location.
- When determin...
```
  - `create_query_hop2.predict`: passthrough from parent[10] (69 chars)
  - `summarize2.predict`: passthrough from parent[10] (83 chars)
  - `final_answer.predict`: passthrough from parent[10] (2,075 chars)

**iter 15** · reflect(8,10) · val=0.6000 (Δval=-0.0067) chars=4,268
  - `summarize1.predict`: passthrough from parent[10] (2,236 chars)
  - `create_query_hop2.predict`: passthrough from parent[8] (69 chars)
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: REWRITE (overlap=0.75, Δ=+1,378 chars) vs parent[10] · Δbullets=+10 Δmust=+1 Δshould=+1
    NEW:
```
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's context and relevant facts.  
- **Goal**: Extract the most accurate and complete answer to the question by combining the information from both summaries.  
- **Strategy**:  
  - Identify the key elements of the ques...
```
    DROPPED:
```
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's context and relevant facts.
- **Goal**: Extract the most accurate...
```

**iter 16** · merge(8) · val=0.5500 (Δval=-0.0500) chars=7,467
  - `summarize1.predict`: passthrough from parent[8] (2,444 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.08, Δ=+1,575 chars) vs parent[8] · Δbullets=+11 ΔEnsure=+1 Δshould=+5
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query`.  
### Task Description:
The goal is to reformulate the original `question` into a more direct and focused `query` that can be used to retrieve factual information from a database or knowledge source. The `query` should capture the core intent of the `question...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[8] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (1,933 chars)

**iter 17** · reflect(2,8) · val=0.7067 (Δval=+0.1533) chars=8,207
  - `summarize1.predict`: REPLACE (overlap=0.52, Δ=-706 chars) vs parent[2] · Δbullets=-8 ΔIf=-3 ΔEnsure=-2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to identify the key elements, required data, and context. Analyze the paragraphs to locate relevant information, being mindful of specific historical events, people, places, and the need to...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Id...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[8] (1,933 chars)

**iter 18** · merge(4) · val=0.5500 (Δval=-0.0500) chars=7,467
  - `summarize1.predict`: passthrough from parent[4] (3,355 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+2,086 chars) vs parent[4] · Δbullets=+9 ΔIf=+2 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `summary_1`, your task is to produce the field `query` by reformulating the original question into a more precise, focused, and answerable form based on the information provided in the summary. 
### Key Guidelines:
1. **Understand the Question's Core**: Identify the main subject, the key relationship, and the desi...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 19** · reflect(15,17) · val=0.6967 (Δval=-0.0100) chars=8,919 ⭐ overall-best
  - `summarize1.predict`: REWRITE (overlap=0.75, Δ=+325 chars) vs parent[15] · Δbullets=-10
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to determine the specific information requested, and analyze the paragraphs to locate relevant information. Identify key entities and their relationships, and draw logical connections acros...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Understand the question to determine the specific information r...
```
  - `create_query_hop2.predict`: passthrough from parent[15] (69 chars)
  - `summarize2.predict`: passthrough from parent[15] (83 chars)
  - `final_answer.predict`: passthrough from parent[15] (3,453 chars)

**iter 20** · merge(2) · val=0.7167 (Δval=-0.0333) chars=9,738
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+1,972 chars) vs parent[2] · Δbullets=+10 ΔIf=+3 Δshould=+9
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by extracting the core factual question that can be directly answered using the information in `summary_1`. 
### Task Description:
1. **Identify the core factual question**: Extract the specific factual question that is being asked in the `question` field, which can be answer...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)


_Cell summary:_ 5 running-best updates; 0 inert merges (no predictor changed); ops=reflect=12, merge=8
- avg per *changed* reflect predictor: Δbullets=+1.17/pred-step, ΔIf=+0.67/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+0.08/pred-step, Δmust=+0.17/pred-step, Δshould=+0.58/pred-step
- avg per *changed* merge predictor: Δbullets=+10.25/pred-step, ΔIf=+1.25/pred-step, ΔWhen=+0.62/pred-step, ΔEnsure=+1.50/pred-step, Δmust=+0.12/pred-step, Δshould=+2.38/pred-step

---

### 2wiki · summarize_before_immediate_s0

20 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2433 (Δval=-0.0067) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2633 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(2) · val=0.2467 (Δval=-0.0167) chars=4,581
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.09, Δ=+1,660 chars) vs parent[2] · Δbullets=+13 ΔIf=+6 ΔEnsure=+1 Δmust=+1 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the most accurate and concise information that directly addresses the question. 
### Task Details:
- The question typically involves a multi-step inference or a specific factual connection between entities, locations, or events.
- ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 4** · reflect(1,3) · val=0.4100 (Δval=+0.1600) chars=1,559 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.77, Δ=-139 chars) vs parent[1] · Δbullets=-3 ΔEnsure=-1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine what needs to be determined or inferred.
2. **Extract Relevant Information**: Scan through the provided paragraphs to find information that directly or indirectly relates to...
```
    DROPPED:
```
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract Relevant...
```
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[3] (1,743 chars)

**iter 5** · merge(4) · val=0.4000 (Δval=-0.0100) chars=4,758
  - `summarize1.predict`: REWRITE (overlap=0.82, Δ=+1,714 chars) vs parent[4] · Δbullets=+8 ΔIf=+2 ΔEnsure=+1 Δshould=+3
    NEW:
```
### Instruction for the Assistant
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine what needs to be determined or inferred. Pay attention to whether the question involves a direct fact, a logical inference, or a comparison...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine what needs to be determ...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (1,743 chars)

**iter 6** · reflect(1) · val=0.2533 (Δval=-0.0100) chars=5,872
  - `summarize1.predict`: passthrough from parent[1] (3,993 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.09, Δ=+1,403 chars) vs parent[1] · Δbullets=+3 ΔIf=+3 ΔEnsure=+1 Δshould=+3
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by transforming the question into a more precise or focused query based on the information provided in the summary. 
### Task Details:
- **Goal:** Generate a concise and accurate query that extracts or clarifies the specific information needed to answer the original question,...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: passthrough from parent[1] (83 chars)

**iter 7** · reflect(0) · val=0.2633 (Δval=+0.0000) chars=5,543
  - `summarize1.predict`: REPLACE (overlap=0.05, Δ=+2,678 chars) vs parent[0] · Δbullets=+9 ΔIf=+3 ΔEnsure=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
To solve this task, follow these steps:
1. **Identify Key Entities and Relationships**: Parse the question to identify key entities (e.g., people, organizations, locations, events) and relationships (e.g., "found...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 8** · merge(4,7) · val=0.4133 (Δval=+0.0033) chars=6,795 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.79, Δ=-72 chars) vs parent[4] · Δbullets=-5 ΔIf=-1
    NEW:
```
To solve this task, follow these steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine what needs to be determined or inferred. Identify key entities and relationships (e.g., people, organizations, locations, events) and...
```
    DROPPED:
```
### Task Description:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine w...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (1,743 chars)

**iter 9** · reflect(0) · val=0.7767 (Δval=+0.3667) chars=3,144 ★ new running-best
  - `summarize1.predict`: passthrough from parent[0] (72 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.06, Δ=+2,093 chars) vs parent[0] · Δbullets=+4 Δshould=+1
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by reformulating the original question into a more focused and direct query that extracts the core factual information implied by the summary.  
### Task Details:
- **Goal**: Transform the original question into a more precise query that can be used to retrieve specific factu...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 10** · merge(3,7) · val=0.7633 (Δval=-0.0133) chars=8,380
  - `summarize1.predict`: REPLACE (overlap=0.53, Δ=+1,044 chars) vs parent[7] · Δbullets=-1 ΔIf=+3 ΔEnsure=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Parse the question to identify key entities (e.g., people, or...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
To solve this task, follow these steps:
1. **Identify Key Enti...
```
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: passthrough from parent[3] (1,743 chars)

**iter 11** · reflect(1) · val=0.7667 (Δval=+0.0033) chars=9,578 ⭐ overall-best
  - `summarize1.predict`: passthrough from parent[1] (3,993 chars)
  - `create_query_hop2.predict`: passthrough from parent[1] (69 chars)
  - `summarize2.predict`: passthrough from parent[1] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.07, Δ=+2,025 chars) vs parent[1] · Δbullets=+6 ΔIf=+3 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the two summaries to directly answer the question.  
### Task Details:
- **Input Format**: Each example contains a `question`, a `summary_1`, and a `summary_2`. These summaries are concise statements that pro...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 12** · reflect(5,7) · val=0.7633 (Δval=-0.0033) chars=10,675
  - `summarize1.predict`: REPLACE (overlap=0.65, Δ=-487 chars) vs parent[5] · Δbullets=-7 ΔIf=-1 ΔEnsure=-1
    NEW:
```
To solve this task, follow these steps:
1. **Identify Key Entities and Relationships**: Parse the question to identify key entities (e.g., people, organizations, locations, events) and relationships (e.g., "founder of Redpath Sugar," "country where... lived," "largest river in..."). This helps determine what specific information is needed from t...
```
    DROPPED:
```
### Instruction for the Assistant
### Task Description:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,743 chars)

**iter 13** · reflect(4) · val=0.7667 (Δval=+0.0033) chars=9,680
  - `summarize1.predict`: passthrough from parent[4] (3,854 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.09, Δ=+1,625 chars) vs parent[4] · Δbullets=+5 ΔIf=+1 ΔEnsure=+2
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by identifying the key information needed to answer the question. The task involves:
1. **Understanding the question**: Carefully parse the question to identify the main subject, the specific information required, and any contextual clues or constraints.
2. **U...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[4] (1,743 chars)

**iter 14** · reflect(13) · val=0.7633 (Δval=-0.0133) chars=4,774
  - `summarize1.predict`: passthrough from parent[13] (3,854 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.07, Δ=+1,880 chars) vs parent[13] · Δbullets=+7 ΔIf=+4 ΔEnsure=+2 Δshould=+4
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by reformulating the question into a clear and precise query that captures the essential information needed to answer the question.  
### Key Guidelines:
1. **If the summary_1 directly provides the answer** to the question, then the `query` should be the exact answer provided...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[13] (1,708 chars)
  - `final_answer.predict`: passthrough from parent[13] (1,743 chars)

**iter 15** · reflect(12,13) · val=0.7633 (Δval=-0.0033) chars=11,209
  - `summarize1.predict`: REWRITE (overlap=0.92, Δ=+244 chars) vs parent[13] · ΔEnsure=-1
    NEW:
```
To solve this task, follow these steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine what needs to be determined or inferred. Identify key entities and relationships, such as people, organizations, locations, events, a...
```
    DROPPED:
```
### Task Description:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Carefully parse the question to determine w...
```
  - `create_query_hop2.predict`: passthrough from parent[12] (69 chars)
  - `summarize2.predict`: passthrough from parent[13] (1,708 chars)
  - `final_answer.predict`: passthrough from parent[12] (1,743 chars)

**iter 16** · reflect(12) · val=0.7600 (Δval=-0.0167) chars=5,522
  - `summarize1.predict`: PURE_INFLATION (×1.2, +976 chars) vs parent[12] · Δbullets=+3 Δshould=+3
    NEW:
```
- The assistant should be able to recognize specific cultural and historical references such as:
  - **Books and Authors**: The *Man with the Golden Gun* by Ian Fleming, the *Mighty Joe Moon* by Grant Lee Buffalo.
  - **Historical Figures**: Adolf Hitler, Ian Fleming, Francisco Scaramanga, and Ilídio Vale.
  - **Geographical Discoveries**: Portu...
```
  - `create_query_hop2.predict`: passthrough from parent[12] (69 chars)
  - `summarize2.predict`: passthrough from parent[12] (83 chars)
  - `final_answer.predict`: passthrough from parent[12] (1,743 chars)

**iter 17** · merge(14,15) · val=0.7633 (Δval=-0.0033) chars=10,081  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[15] (4,098 chars)
  - `create_query_hop2.predict`: passthrough from parent[14] (1,949 chars)
  - `summarize2.predict`: passthrough from parent[14] (1,708 chars)
  - `final_answer.predict`: passthrough from parent[14] (1,743 chars)

**iter 18** · reflect(5) · val=0.7733 (Δval=-0.0033) chars=3,922
  - `summarize1.predict`: REWRITE (overlap=0.91, Δ=+157 chars) vs parent[5] · Δbullets=-1 ΔIf=-1
    NEW:
```
### Examples and Domain-Specific Knowledge:
- **Historical Context**: Know that the Ottoman Empire declined after the Crimean War, and that the Italian invasion of Libya occurred in 1911.
- **Geographical Knowledge**: Understand that the Appalachian Mountains are in eastern North America, and that the Ozark and Ouachita Mountains are the only ma...
```
    DROPPED:
```
### Example:
If the question is: "From which country is the president of the country that in 1911 seized Al-Berka's country from the empire that declined after the Crimean War?"  
- Identify that A...
```
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (1,743 chars)


_Cell summary:_ 5 running-best updates; 1 inert merges (no predictor changed); ops=reflect=14, merge=4
- avg per *changed* reflect predictor: Δbullets=+4.71/pred-step, ΔIf=+1.79/pred-step, ΔWhen=+0.07/pred-step, ΔEnsure=+0.64/pred-step, Δmust=+0.07/pred-step, Δshould=+1.21/pred-step
- avg per *changed* merge predictor: Δbullets=+0.67/pred-step, ΔIf=+1.33/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+0.67/pred-step, Δmust=+0.00/pred-step, Δshould=+1.00/pred-step

---

### 2wiki · summarize_before_score_plateau_s0

19 candidates total. ⭐ = overall best_candidate. ★ = new running-best.

**iter 0** · seed · val=0.2500 ★ new running-best
- predictors: summarize1.predict(72 chars), create_query_hop2.predict(69 chars), summarize2.predict(83 chars), final_answer.predict(83 chars)

**iter 1** · reflect(0) · val=0.2433 (Δval=-0.0067) chars=2,254
  - `summarize1.predict`: REPLACE (overlap=0.03, Δ=+3,921 chars) vs parent[0] · Δbullets=+19 ΔIf=+4 ΔWhen=+1 ΔEnsure=+2 Δshould=+1
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., people, places, events, relationships) that need to be determined or inferred.
2. **Extract R...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 2** · reflect(0) · val=0.2633 (Δval=+0.0200) chars=3,506 ★ new running-best
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,287 chars) vs parent[0] · Δbullets=+8 ΔIf=+3 ΔEnsure=+2
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. Follow these detailed steps:
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
2. **Identify Relevant Information**: Scan through t...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 3** · reflect(0) · val=0.1933 (Δval=-0.0567) chars=2,091
  - `summarize1.predict`: REPLACE (overlap=0.06, Δ=+2,372 chars) vs parent[0] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1 Δshould=+4
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typically requires identifying a specific piece of information, such as a person, place, event, or fact, by analyzing the content of the paragraphs. The answe...
```
    DROPPED:
```
Given the fields `question`, `paragraphs`, produce the fields `summary`.
```
  - `create_query_hop2.predict`: passthrough from parent[0] (69 chars)
  - `summarize2.predict`: passthrough from parent[0] (83 chars)
  - `final_answer.predict`: passthrough from parent[0] (83 chars)

**iter 4** · reflect(2) · val=0.4000 (Δval=+0.1500) chars=2,358 ★ new running-best
  - `summarize1.predict`: REWRITE (overlap=0.70, Δ=+996 chars) vs parent[2] · Δbullets=+1 ΔIf=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question.
   - Look for domain-specific terms and names (e.g., "Small Dark Spot," "First French Republic," ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context.
3. **Extract and Synthesize Information**: Pull out the relevant ...
```
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: passthrough from parent[2] (83 chars)

**iter 5** · reflect(3) · val=0.6067 (Δval=+0.2067) chars=2,741 ★ new running-best
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[3] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,992 chars) vs parent[3] · Δbullets=+5 ΔIf=+7 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the two summaries to directly answer the question.  
### Task Details:
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's conte...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 6** · reflect(4) · val=0.5400 (Δval=-0.0667) chars=4,725
  - `summarize1.predict`: REWRITE (overlap=0.86, Δ=+1,094 chars) vs parent[4] · Δbullets=+1 ΔIf=+1 ΔWhen=+1 ΔEnsure=+2
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question. For example, if the question refers to a specific historical event, a geographical feature, or a ...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural ...
```
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 7** · reflect(5) · val=0.7933 (Δval=+0.5300) chars=5,444 ★ new running-best
  - `summarize1.predict`: passthrough from parent[5] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.53, Δ=+1,998 chars) vs parent[5] · Δbullets=+10 ΔIf=+6 ΔEnsure=+2 Δmust=+1
    NEW:
```
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's context and relevant facts. These summaries may include indirect references, such as locations, political figures, historical events, cultural references, or indirect identifications of people, places, or events.  
...
```
    DROPPED:
```
- **Input Format**: Each example contains a `question`, `summary_1`, and `summary_2`, which are concise summaries of the question's context and relevant facts.
- **Goal**: Extract the most accurate...
```

**iter 8** · reflect(5) · val=0.3800 (Δval=-0.0200) chars=4,762
  - `summarize1.predict`: passthrough from parent[5] (2,444 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.09, Δ=+1,286 chars) vs parent[5] · Δbullets=+6 ΔEnsure=+1 Δshould=+5
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by extracting the answer to the question from the summary. The answer should be a concise, direct statement that explicitly states the factual information provided in the summary. 
The task involves identifying the key factual information from the summary that directly answer...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[5] (83 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 9** · reflect(3) · val=0.4033 (Δval=+0.0033) chars=4,830
  - `summarize1.predict`: passthrough from parent[3] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.05, Δ=+2,951 chars) vs parent[3] · Δbullets=+14 ΔEnsure=+2
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the context and the provided paragraphs. 
### Task Details:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., entities, relationships, specific facts).
2. **Use Context**: The `co...
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[3] (83 chars)

**iter 10** · reflect(5,9) · val=0.3833 (Δval=-0.0200) chars=7,537  INERT (no predictor changed)
  - `summarize1.predict`: passthrough from parent[5] (2,444 chars)
  - `create_query_hop2.predict`: passthrough from parent[5] (69 chars)
  - `summarize2.predict`: passthrough from parent[9] (3,034 chars)
  - `final_answer.predict`: passthrough from parent[5] (2,075 chars)

**iter 11** · merge(4) · val=0.5233 (Δval=-0.0167) chars=7,197
  - `summarize1.predict`: passthrough from parent[4] (3,355 chars)
  - `create_query_hop2.predict`: passthrough from parent[4] (69 chars)
  - `summarize2.predict`: REPLACE (overlap=0.06, Δ=+2,379 chars) vs parent[4] · Δbullets=+13 ΔIf=+2 ΔEnsure=+1 Δshould=+5
    NEW:
```
Given the fields `question`, `context`, and `paragraphs`, produce the field `summary` by answering the question based on the provided context and supporting information from the paragraphs. 
### Task Description:
1. **Understand the Question**: Carefully parse the question to identify the key elements (e.g., names, locations, events, years, etc....
```
    DROPPED:
```
Given the fields `question`, `context`, `paragraphs`, produce the fields `summary`.
```
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 12** · reflect(11) · val=0.5300 (Δval=-0.0100) chars=5,030 ⭐ overall-best
  - `summarize1.predict`: passthrough from parent[11] (3,355 chars)
  - `create_query_hop2.predict`: passthrough from parent[11] (69 chars)
  - `summarize2.predict`: passthrough from parent[11] (2,462 chars)
  - `final_answer.predict`: REPLACE (overlap=0.09, Δ=+1,688 chars) vs parent[11] · Δbullets=+8 ΔIf=+3 ΔEnsure=+1 Δshould=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by synthesizing the information from the summaries to directly answer the question. 
### Key Instructions:
1. **Understand the Question**: Identify the core request of the question, which often involves connecting pieces of information from diff...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 13** · reflect(12) · val=0.5267 (Δval=-0.0133) chars=6,470
  - `summarize1.predict`: REWRITE (overlap=0.73, Δ=+989 chars) vs parent[12] · Δbullets=+1 ΔEnsure=+1
    NEW:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural references that may be embedded within the question. For example, if the question refers to a specific empire, a historical event, or a geographical f...
```
    DROPPED:
```
1. **Understand the Question**: Identify the key elements of the question, such as the subject, the required data, and the context. Pay close attention to any historical, geographical, or cultural ...
```
  - `create_query_hop2.predict`: passthrough from parent[12] (69 chars)
  - `summarize2.predict`: passthrough from parent[12] (2,462 chars)
  - `final_answer.predict`: passthrough from parent[12] (1,771 chars)

**iter 14** · reflect(2) · val=0.5433 (Δval=+0.0167) chars=8,246
  - `summarize1.predict`: passthrough from parent[2] (2,359 chars)
  - `create_query_hop2.predict`: passthrough from parent[2] (69 chars)
  - `summarize2.predict`: passthrough from parent[2] (83 chars)
  - `final_answer.predict`: REPLACE (overlap=0.08, Δ=+1,848 chars) vs parent[2] · Δbullets=+12 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `question`, `summary_1`, and `summary_2`, your task is to produce the field `answer` by extracting the correct and consistent information that directly answers the question. 
### Key Instructions:
1. **Identify the core question**: Understand what the question is asking for (e.g., a date, a number, a name, a location, etc.).
2. ...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, `summary_2`, produce the fields `answer`.
```

**iter 15** · merge(10) · val=0.5500 (Δval=+0.0067) chars=10,718
  - `summarize1.predict`: REWRITE (overlap=0.84, Δ=+908 chars) vs parent[10] · Δbullets=+3 ΔEnsure=+1 Δshould=+3
    NEW:
```
- The assistant should also be able to recognize and process information about:
  - **World Heritage Sites** (e.g., UNESCO-listed locations, number of sites in a country or territory)
  - **Music and Bands** (e.g., identifying the origin of a band, the release date of a song, the artist who performed it)
  - **Historical Events** (e.g., secessio...
```
  - `create_query_hop2.predict`: passthrough from parent[10] (69 chars)
  - `summarize2.predict`: passthrough from parent[10] (3,034 chars)
  - `final_answer.predict`: passthrough from parent[10] (2,075 chars)

**iter 16** · reflect(3,13) · val=0.4833 (Δval=-0.0567) chars=6,691
  - `summarize1.predict`: REPLACE (overlap=0.34, Δ=+614 chars) vs parent[3] · ΔIf=+1 ΔEnsure=+1 Δshould=-3
    NEW:
```
Given the fields `question` and `paragraphs`, produce the field `summary` by answering the question based on the provided paragraphs. 
**Task Description:**  
The task involves answering a question by identifying specific factual information, such as a person, place, event, or relationship, through analysis of the provided paragraphs. The answer...
```
    DROPPED:
```
Given the fields `question` and `paragraphs`, produce the field `summary`. 
**Task Description:**
The task involves answering a question based on a set of provided paragraphs. The question typicall...
```
  - `create_query_hop2.predict`: passthrough from parent[3] (69 chars)
  - `summarize2.predict`: passthrough from parent[13] (2,462 chars)
  - `final_answer.predict`: passthrough from parent[13] (1,771 chars)

**iter 17** · reflect(4) · val=0.7467 (Δval=+0.2067) chars=5,137
  - `summarize1.predict`: passthrough from parent[4] (3,355 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.10, Δ=+1,255 chars) vs parent[4] · Δbullets=+10 ΔIf=+1 ΔEnsure=+1
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query` by transforming the original question into a clear, direct question that can be answered using the information provided in `summary_1`. 
### Key Instructions:
- **Identify the core information** in the `question` that needs to be answered.
- **Extract the relevant facts** fro...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[4] (83 chars)
  - `final_answer.predict`: passthrough from parent[4] (83 chars)

**iter 18** · reflect(12) · val=0.7467 (Δval=+0.0000) chars=7,307
  - `summarize1.predict`: passthrough from parent[12] (3,355 chars)
  - `create_query_hop2.predict`: REPLACE (overlap=0.09, Δ=+1,357 chars) vs parent[12] · Δbullets=+8 ΔEnsure=+1 Δshould=+1
    NEW:
```
Given the fields `question` and `summary_1`, produce the field `query`. 
The task involves transforming the original `question` into a more precise and focused `query` by incorporating key factual information from the `summary_1`. The goal is to create a clear, concise, and factually grounded query that retains the core intent of the original qu...
```
    DROPPED:
```
Given the fields `question`, `summary_1`, produce the fields `query`.
```
  - `summarize2.predict`: passthrough from parent[12] (2,462 chars)
  - `final_answer.predict`: passthrough from parent[12] (1,771 chars)


_Cell summary:_ 5 running-best updates; 1 inert merges (no predictor changed); ops=reflect=16, merge=2
- avg per *changed* reflect predictor: Δbullets=+7.53/pred-step, ΔIf=+2.00/pred-step, ΔWhen=+0.13/pred-step, ΔEnsure=+1.20/pred-step, Δmust=+0.07/pred-step, Δshould=+0.67/pred-step
- avg per *changed* merge predictor: Δbullets=+8.00/pred-step, ΔIf=+1.00/pred-step, ΔWhen=+0.00/pred-step, ΔEnsure=+1.00/pred-step, Δmust=+0.00/pred-step, Δshould=+4.00/pred-step

---
