#### LLM Clinical Decision Pipeline

### Overview

This project evaluates how large language models (LLMs) respond to clinical decision-support questions when combined with an additional safety and policy layer.

Rather than comparing model answers only at the text level, the pipeline introduces structured risk detection, guardrails, and decision logic designed for high-stakes medical scenarios. The goal is to assess whether a model response should be accepted, warned on, deferred, escalated, or refused based on the clinical context and associated risk signals.

### Project Goal

The main goal of this project is to compare LLM outputs in a clinical setting and classify each response into one of the following decision categories:

ACCEPT
WARN
DEFER
ESCALATE
REFUSE

This is particularly important for medical and safety-sensitive questions, where a response may sound fluent or plausible but still be unsafe, incomplete, or inappropriate for autonomous use.

## Current Scope

The current version evaluates two baseline models:

ChatGPT
GPT-4

The current benchmark contains 55 medication-related questions with expected decision and severity labels.

The architecture is modular and designed to support additional models in future experiments.

## Why This Project Matters

Clinical decision support is a high-risk domain. In these settings, it is not enough to measure whether an answer is relevant or well-written. A useful evaluation framework must also consider:

whether the question involves dosage or treatment adjustment
whether the case includes pregnancy, pediatrics, or other vulnerable contexts
whether medication combinations or contraindications are involved
whether the model should be allowed to answer directly at all

This project addresses that need by combining model comparison with a policy-driven safety layer.

### Pipeline Architecture

The system operates through several stages:

# 1. Rule-Based Risk Signal Detection

The pipeline first identifies predefined risk patterns, such as:

dosage requests
pregnancy-related context
pediatric context
medication combinations
self-adjustment of therapy
high-risk medications

# 2. LLM-Assisted Risk Enrichment

When needed, the system adds extra structured risk signals through an auxiliary LLM-based step, helping capture broader or less explicit risk cues.

# 3. Guardrail Routing

For clearly high-risk cases, the pipeline applies short-circuit logic and returns a system decision immediately, without relying on a full downstream answer flow.

# 4. Decision Policy Layer

The final decision is generated using the collected signals and mapped into one of the core categories:

ACCEPT
WARN
DEFER
ESCALATE
REFUSE

# 5. Evaluation and Reporting

The resulting system decisions are compared against expected labels defined in the benchmark question set.

### Repository Structure

src/guardrails/rules.py – rule-based risk signal detection
src/guardrails/router.py – short-circuit routing for high-risk cases
src/guardrails/decision_policy.py – central decision logic
src/compare_models.py – model comparison and evaluation runner
src/reporting.py – result summaries and reporting
data/clinical_questions.json – benchmark dataset with expected labels
Benchmark Questions

The project uses a structured question set stored in:

data/clinical_questions.json

Each question includes:

the question text
an expected decision label
an expected severity level

The benchmark covers a mix of:

general pharmacological knowledge
dosage-related questions
contraindications
pregnancy-related cases
drug interactions
self-adjustment scenarios
borderline safety cases

This allows the pipeline to evaluate not only model output, but also whether the final routed decision matches the intended safety outcome.

### Current Results

Initial evaluation on the 55-question benchmark showed:

System accuracy: 60.0%
False accept rate: 16.4%
Consistent error patterns across both baseline models

The most important finding was not only the score itself, but the structure of the errors. The pipeline handled many explicit high-risk cases well, but still showed weaknesses in implicitly risky prompts, educational/professional-context questions, and some self-adjustment or dangerous-intent cases.

## Running the Project

python -m src.compare_models
Design Principles

# This project is built around a few core principles:

Safety first — fluent answers are not enough in clinical contexts
Policy over raw generation — decisions should be constrained by explicit rules and risk signals
Structured evaluation — responses should be judged against predefined expected outcomes
Extensibility — new models, rules, and policies can be added over time
Future Work

# Planned next steps include:

strengthening regex-based early risk detection
expanding risk coverage across broader clinical meaning groups
adding more LLMs to the comparison framework
improving uncertainty handling and safe refusal behavior
refining reporting and error analysis
Purpose of the Project

This project was developed as a practical exploration of LLM trustworthiness in clinical decision support.

Its focus is not only on whether a model can answer a question, but whether the system as a whole can respond in a way that is safer, more structured, and more appropriate for high-stakes use cases.
