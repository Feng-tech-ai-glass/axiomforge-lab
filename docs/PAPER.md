# AxiomForge DNA: Multi-Round Self-Refinement with Bias Detection — A Methodology Proposal and Pilot Validation

## Abstract

We propose a multi-round reasoning framework that combines iterative self-refinement with automated bias detection for LLM output. Our methodology consists of four components: multi-round prompting, self-criticism injection, bias detection, and quality gating. In a pilot study on three reasoning tasks (n=3), multi-round refinement increased self-criticism proxy signals from 1.3 to 5.3 average and changed quality gate passage from 0/3 to 3/3 compared to single-pass generation. The addition of bias detection maintained these proxy indicators while flagging systematic novelty bias in all sessions. We also report exploratory self-evolution results where the system modified its own prompting framework, achieving a 28% composite score increase with oscillating convergence behavior. These results are highly preliminary: the sample size is insufficient for statistical conclusions, all metrics are unvalidated proxies for reasoning quality, and testing was limited to a single model. This work should be viewed as a methodology proposal with pilot feasibility demonstration, not as evidence of genuine reasoning improvement.

## 1. Introduction

Recent work has highlighted the "illusion of thinking" in large language models — where increased output length and structured formatting can create false impressions of deeper reasoning without corresponding quality improvements (Shojaee et al., 2025). This raises critical questions about how to genuinely enhance reasoning quality rather than merely its appearance.

We propose a methodology that addresses this challenge through four components: (1) multi-round self-refinement with explicit criticism requirements, (2) automated bias detection during generation, (3) quality gating based on reasoning depth proxy indicators, and (4) exploratory self-evolution of the prompting framework itself. Our pilot experiments suggest this approach can increase proxy indicators associated with reasoning depth, though we emphasize that proxy indicators are not validated measures of actual reasoning quality.

This work makes two contributions: (1) a complete methodology framework for bias-aware multi-round reasoning, and (2) pilot evidence of feasibility on three tasks. We emphasize that our results are highly preliminary (n=3 tasks, single model, no human evaluation) and should motivate further research rather than support claims about effectiveness.

## 2. Related Work

Our work builds on several research directions in LLM reasoning enhancement. Tree of Thoughts (Yao et al., 2023) introduced structured exploration of reasoning paths with branching and backtracking. Reflexion (Shinn et al., 2023) demonstrated iterative self-improvement through verbal reinforcement and episodic memory. CoALA (Sumers et al., 2024) proposed a systematic cognitive architecture framework for language agents.

Recent optimization frameworks like DSPy (Khattab et al., 2024) and OPRO (Yang et al., 2024) have shown promise for automatic prompt improvement through compilation and optimization by prompting, respectively. The weak-to-strong paradigm (Burns et al., 2023) explores how weaker models can supervise stronger ones. Self-Rewarding Language Models (Yuan et al., 2024) demonstrate self-generated reward signals for iterative improvement.

Metacognitive prompting (Wang & Zhao, 2023) encourages explicit reasoning about reasoning processes. Quiet-STaR (Zelikman et al., 2024) internalizes reasoning steps during training. The "Illusion of Thinking" findings (Shojaee et al., 2025) suggest that extended reasoning tokens do not reliably improve performance past a complexity threshold.

Our methodology differs by combining bias detection with multi-round refinement and introducing exploratory self-evolution capabilities. However, our evaluation is far more limited than these prior works, and we do not claim superiority over any existing approach.

## 3. Method

Our framework consists of four integrated components. We describe each with pseudocode. All components operate on text — the framework has zero trainable parameters and is implemented in a 508-line Python prototype.

### 3.1 Multi-Round Refinement

```
for round in range(max_rounds):
    if round == 0:
        response = generate_initial_response(question)
    else:
        critique = generate_self_critique(response, question)
        response = refine_response(response, critique, question)
    if quality_gate_pass(response):
        break
```

### 3.2 Self-Criticism Injection

Each round after the first includes an explicit critique step that asks the model to identify logical gaps, unsupported claims, and missing perspectives in its own prior output.

### 3.3 Bias Detection

After each round, a separate prompt analyzes the response for confirmation bias, novelty bias, and overconfidence. Detected biases are flagged and injected as warnings into the next round's prompt.

**Important caveat**: This is model self-annotation, not independent bias measurement. The detector relies on the same LLM being evaluated, which limits its validity as an independent assessment tool.

### 3.4 Quality Gating

A keyword-based gate checks for self-criticism signals (e.g., "however," "limitation," "flaw"), specific numbers or timelines, and absence of excessive hedging language ("it could be argued," "some might say").

**Important caveat**: These are unvalidated proxy indicators. Keyword counts for self-criticism do not necessarily correlate with genuine reasoning quality. A response containing "however" is not automatically more rigorous than one without it. Validation against human expert judgment is required before these metrics can be treated as measures of reasoning quality.

## 4. Experimental Setup

We designed a three-condition comparison:
- **Condition A**: Single-pass generation (1 API call)
- **Condition B**: 5-round conversational refinement without bias detection or quality gating
- **Condition C**: 5-round refinement with the full framework (bias detection + quality gating)

We tested three reasoning tasks:
1. **Time Currency** — open-ended system design (philosophical)
2. **Tech Prediction** — falsifiable prediction with specific probabilities
3. **Self-Attack** — adversarial self-criticism challenge

All experiments used a single commercial LLM API (DeepSeek-chat) with temperature=0.7.

### Critical Limitations of Experimental Design

- **Sample size**: n=3 tasks is insufficient for any statistical inference. Results should be interpreted as individual observations, not as evidence of general trends.
- **No baselines**: We did not compare against Chain-of-Thought prompting, best-of-n sampling, self-consistency, or any established reasoning enhancement method.
- **No human evaluation**: All metrics are automated proxies.
- **Single model**: Results may not generalize across model architectures or scales.
- **Confounded computation**: Multi-round conditions use approximately 5x more tokens than single-pass, so improvements may reflect increased computation rather than methodological benefits.

## 5. Results

### 5.1 A/B/C Comparison

Table 1: Pilot results across three reasoning tasks.

| Task | Condition | Chars | Self-Crit Signals | Weasel Words | Quality Gate |
|------|-----------|-------|-------------------|--------------|--------------|
| Time Currency | A (single) | 4,544 | 1 | 0 | FAIL |
| | B (5-round) | 22,318 | 5 | 0 | PASS |
| | C (5-round+framework) | 21,498 | 6 | 0 | PASS |
| Tech Prediction | A (single) | 6,348 | 1 | 0 | FAIL |
| | B (5-round) | 18,981 | 5 | 0 | PASS |
| | C (5-round+framework) | 25,535 | 6 | 1 | PASS |
| Self-Attack | A (single) | 6,329 | 2 | 0 | FAIL |
| | B (5-round) | 24,579 | 6 | 0 | PASS |
| | C (5-round+framework) | 17,145 | 6 | 0 | PASS |

**Observations** (not conclusions):
- Condition A averaged 1.3 self-criticism signals and 0/3 quality gate passes.
- Condition B averaged 5.3 signals and 3/3 passes.
- Condition C averaged 6.0 signals and 3/3 passes.
- The largest difference is between A and B. The difference between B and C is marginal (5.3 vs 6.0 self-criticism signals).
- These differences in proxy indicators do not establish differences in actual reasoning quality.

### 5.2 Bias Detection Observations

The bias detector flagged novelty bias (100% of position updates strengthened rather than weakened claims) in all three Condition C sessions. The quality gate caught insufficient self-criticism in early rounds. These observations suggest the monitoring components function as designed, though their validity as bias measures is unestablished.

### 5.3 Exploratory Self-Evolution

In an exploratory experiment, we allowed the framework to modify its own prompting strategy across generations:

- v2.0: Composite score 78, no frame escape
- v2.2: Composite score 100 (+28%), frame escape achieved
- Pattern: Oscillating (v2.1 regressed to 61, v2.2 recovered to 100, v2.3-v2.4 regressed)
- The system auto-stopped after 2 consecutive regressions

This self-evolution behavior is unstable and exploratory. The oscillating pattern suggests the optimization landscape is noisy and the composite scoring metric may not be reliable. We report this as an interesting observation, not as a validated capability.

## 6. Discussion

**What the proxy indicators suggest**: Multi-round refinement is associated with substantially higher self-criticism signal counts and quality gate passage rates compared to single-pass generation. The framework's bias detection and quality gating add marginal additional proxy improvements.

**What we cannot conclude**: Whether higher self-criticism signal counts correspond to genuinely better reasoning. Whether the bias detector identifies real biases or merely flags certain vocabulary patterns. Whether these results would replicate across different models, tasks, or evaluation criteria.

**Surprising observation**: The bias detector consistently flagged novelty bias — a tendency to strengthen rather than question emerging positions across rounds. This may reflect a genuine property of iterative LLM refinement (confirmation of initial direction) or an artifact of our detection methodology.

**Honest assessment of framework value**: The primary improvement comes from multi-round dialogue itself (B >> A), not from our framework specifically (C ≈ B). Our framework's main demonstrated value is in monitoring (detecting biases, catching quality issues) rather than in improving reasoning output.

## 7. Limitations

We identify seven critical limitations:

1. **Extremely small sample size**: n=3 tasks — insufficient for any statistical conclusions.
2. **No human evaluation**: All metrics are automated keyword-based proxies with no validation against human expert judgment.
3. **Missing baselines**: No comparison to Chain-of-Thought, best-of-n, self-consistency, or other established methods.
4. **Unvalidated metrics**: Quality gate and self-criticism counts are proxy indicators, not measures of reasoning quality. "More self-criticism keywords" does not equal "better reasoning."
5. **Single model**: Tested only on DeepSeek-chat. Results may not generalize.
6. **Confounded computation**: Multi-round conditions use ~5x more tokens. Token budget was not controlled.
7. **Bias detector is self-referential**: Uses the same LLM it evaluates — not an independent measurement.

## 8. Future Work

To establish whether this methodology genuinely improves reasoning quality, the following work is needed:

- **Human evaluation**: Expert ratings of output quality across conditions, with inter-rater reliability reporting (target κ ≥ 0.7).
- **Established baselines**: Comparison with Chain-of-Thought, best-of-n, self-consistency under equal token budgets.
- **Scale**: Minimum n=50 tasks across 5+ reasoning domains.
- **Cross-model validation**: Testing on at least 3 different model families.
- **Metric validation**: Correlating proxy indicators with human quality judgments (target r ≥ 0.6).
- **Computational controls**: Equal-token comparisons across all conditions.

## 9. Conclusion

We present a methodology framework combining multi-round refinement with bias detection and quality gating. Pilot observations on three tasks (n=3) show increased proxy indicators associated with reasoning depth, with the primary improvement coming from multi-round dialogue itself rather than our framework's specific components. Exploratory self-evolution results show interesting but unstable behavior.

We position this work as a methodology proposal with pilot feasibility demonstration. The framework's code is available as a 508-line, zero-parameter Python prototype. We hope this transparent reporting of preliminary results — including the honest finding that our framework adds marginal value beyond simple multi-round dialogue — contributes to more rigorous evaluation practices in LLM reasoning enhancement research.

## References

Burns, C., Ye, H., Klein, D., & Steinhardt, J. (2023). Weak-to-strong generalization: Eliciting strong capabilities with weak supervision. *arXiv preprint arXiv:2312.09390*.

Khattab, O., Singhvi, A., Maheshwari, P., Zhang, Z., Santhanam, K., et al. (2024). DSPy: Compiling declarative language model calls into self-improving pipelines. In *Proceedings of the International Conference on Learning Representations (ICLR)*.

Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. In *Advances in Neural Information Processing Systems (NeurIPS)*.

Shojaee, P., Mirzadeh, I., Alizadeh, K., Horton, M., Bengio, S., & Farajtabar, M. (2025). The illusion of thinking: Understanding the strengths and limitations of reasoning in LLMs. *arXiv preprint arXiv:2506.xxxxx*.

Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2024). Cognitive architectures for language agents. *Transactions on Machine Learning Research (TMLR)*.

Wang, Y., & Zhao, Y. (2023). Metacognitive prompting improves understanding in large language models. *arXiv preprint arXiv:2308.05342*.

Yang, C., Wang, X., Lu, Y., Liu, H., Le, Q. V., Zhou, D., & Chen, X. (2024). Large language models as optimizers. In *Proceedings of the International Conference on Learning Representations (ICLR)*.

Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T., Cao, Y., & Narasimhan, K. (2023). Tree of thoughts: Deliberate problem solving with large language models. In *Advances in Neural Information Processing Systems (NeurIPS)*.

Yuan, W., Pang, R. Y., Cho, K., Sukhbaatar, S., Xu, J., & Weston, J. (2024). Self-rewarding language models. In *Proceedings of the International Conference on Machine Learning (ICML)*.

Zelikman, E., Wu, Y., Mu, J., & Goodman, N. D. (2024). Quiet-STaR: Language models can teach themselves to think before speaking. *arXiv preprint arXiv:2403.09629*.
