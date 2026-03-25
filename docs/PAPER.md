# AxiomForge DNA: When a Simple Prompt Beats a Complex Scaffold

## Abstract

We investigate whether structured reasoning scaffolds improve LLM output beyond what a well-designed single prompt achieves. Through systematic experiments on 80 reasoning tasks across 6 categories, we find that a single constitutional prompt (embedding self-critique and uncertainty requirements) scores 5.71 average on proxy metrics, outperforming both single-pass generation (4.08), multi-round iteration (4.58), and our own 508-line scaffold framework. A subsequent attempt to build a rule-based routing system that selects strategies per question type yielded only +0.028 improvement over the fixed prompt — effectively zero. We report these as honest negative results: complex scaffolding does not meaningfully improve over a simple, well-crafted prompt for our task set. We also report exploratory self-evolution results (score 78 to 100, +28%) and the system's self-review capability (issuing REJECT on its own overclaimed paper, then Accept after honest repositioning). Our primary contribution is methodological: a systematic framework for testing whether architectural complexity is justified, and evidence that for many reasoning tasks, it is not. Code available at: https://github.com/Feng-tech-ai-glass/axiomforge-lab

## 1. Introduction

The field of LLM reasoning enhancement is characterized by increasingly complex architectures: Tree of Thoughts with multi-path exploration (Yao et al., 2023), Reflexion with episodic memory (Shinn et al., 2023), and cognitive architectures with numerous interacting components (Sumers et al., 2024). A fundamental question is rarely asked: does this complexity actually help?

Recent findings on the "illusion of thinking" (Shojaee et al., 2025) suggest that longer outputs and structured formatting can create false impressions of deeper reasoning. This motivates our central question: when we add scaffolding around an LLM, are we improving reasoning or just adding overhead?

We address this through three phases of experimentation:
1. A/B/C comparison of single-pass, multi-round, and scaffolded reasoning (n=3 pilot, then n=80 extended)
2. Self-evolution experiments where the scaffold modifies itself
3. A rule-based routing system that attempts to select optimal strategies per question type

Our findings are primarily negative: a single well-crafted "constitutional" prompt consistently outperforms more complex alternatives. We report this honestly as evidence that the field may be over-engineering reasoning enhancement.

## 2. Related Work

Tree of Thoughts (Yao et al., 2023) introduced structured multi-path reasoning. Reflexion (Shinn et al., 2023) demonstrated verbal self-improvement with episodic memory. CoALA (Sumers et al., 2024) proposed a cognitive architecture framework for language agents. DSPy (Khattab et al., 2024) compiles declarative LM calls into optimized pipelines. OPRO (Yang et al., 2024) uses LLMs as optimizers. The weak-to-strong paradigm (Burns et al., 2023) explores small models supervising large ones. Self-Rewarding LMs (Yuan et al., 2024) demonstrate self-generated reward signals. Metacognitive prompting (Wang & Zhao, 2023) and Quiet-STaR (Zelikman et al., 2024) explore explicit reasoning processes.

These systems demonstrate clear improvements but typically do not isolate multi-round interaction effects from architectural contributions. Our work provides this isolation and finds that architectural complexity adds minimal value beyond what a good single prompt achieves.

## 3. Method

### 3.1 Four Experimental Conditions

**Condition A — Single-Pass**: One API call with basic instructions for specificity, self-criticism, and uncertainty acknowledgment.

**Condition B — Multi-Round**: Three sequential rounds: (1) answer the question, (2) attack your answer, (3) fix weaknesses. Three API calls.

**Condition C — Constitutional Single-Shot**: One API call with embedded self-evaluation requirements: "For each reasoning step, ask: Is this assumption justified? What would contradict this? Am I overconfident? What would experts critique?" Token budget approximately 3x that of Condition A.

**Condition D — Adaptive**: Difficulty assessment (1 API call) followed by proportional token allocation (1 API call). Two calls total.

### 3.2 Proxy Metrics

We use automated keyword-based scoring (0-10 scale):

- Self-criticism signals: "however," "flaw," "limitation," "weakness," etc.
- Uncertainty acknowledgment: "uncertain," "unclear," "might," "possibly," etc.
- Specificity: numbers, percentages, dates, quantified claims
- Weasel word penalty: "it could be argued," "some might say," etc.

**Critical caveat**: These are unvalidated proxy indicators. Higher self-criticism keyword counts do not necessarily indicate better reasoning. All conclusions are limited to proxy metric performance, not verified reasoning quality.

### 3.3 AxiomForge DNA v2.2 Scaffold

A 508-line, zero-parameter Python framework with four components: FlowController (dynamic step sequencing), MemoryLedger (cross-session persistence), QualityGate (output quality checks), and BiasDetector (novelty and confirmation bias detection). Used in the A/B/C comparison as the scaffold driving Condition C in the pilot study.

## 4. Experimental Setup

### 4.1 Pilot Study (n=3)

Three reasoning tasks: open-ended philosophy ("Time Currency"), falsifiable prediction ("Tech Prediction"), and adversarial self-criticism ("Self-Attack"). All conditions tested on the same questions using DeepSeek-chat API, temperature=0.7.

### 4.2 Extended Study (n=80)

300 questions generated across 6 categories (philosophy, technology, prediction, self_attack, policy, science). 80 questions sampled and tested with all four conditions. Each question evaluated by all four methods, producing 320 method-question pairs.

### 4.3 Level 1 Router Test

A rule-based router: prediction questions use multi-round (B), all other questions use constitutional (C). Tested offline against the 80-question dataset.

### 4.4 Known Limitations

1. Sample sizes (n=3 pilot, n=80 extended) are small
2. No human evaluation — all metrics are automated proxies
3. No comparison to Chain-of-Thought or other established baselines
4. Single model (DeepSeek-chat) — results may not generalize
5. Constitutional condition uses more tokens than single-pass — not equal-compute
6. Questions generated by same model family — potential circular bias

## 5. Results

### 5.1 Pilot Results (n=3)

| Condition | Avg Score | Avg Self-Criticism | Avg Time |
|-----------|-----------|-------------------|----------|
| A — Single-pass | 3.00 | 2.0 | 33.9s |
| B — Multi-round | 5.67 | 2.7 | 143.6s |
| C — Constitutional | 6.83 | 4.0 | 50.6s |
| D — Adaptive | 5.67 | 2.0 | 51.4s |

### 5.2 Extended Results (n=80)

| Condition | Avg Score | Win Count | Win Rate |
|-----------|-----------|-----------|----------|
| C — Constitutional | 5.71 | 37 | 46% |
| D — Adaptive | 5.10 | 13 | 16% |
| B — Multi-round | 4.58 | 19 | 24% |
| A — Single-pass | 4.08 | 11 | 14% |

Category-level analysis (wins by question type):

| Category | C wins | B wins | D wins | A wins |
|----------|--------|--------|--------|--------|
| philosophy (17) | 8 | 3 | 5 | 1 |
| policy (13) | 7 | 0 | 5 | 1 |
| technology (16) | 9 | 6 | 1 | 0 |
| science (9) | 4 | 3 | 1 | 1 |
| self_attack (15) | 8 | 2 | 1 | 4 |
| prediction (10) | 1 | 5 | 0 | 4 |

Constitutional wins 5 of 6 categories. Prediction is the sole exception where multi-round wins.

### 5.3 Router Test Results

| Method | Avg Score | Delta vs Fixed C |
|--------|-----------|-----------------|
| Fixed Constitutional | 5.639 | baseline |
| Router (pred->B, else->C) | 5.667 | +0.028 |
| Oracle (always pick best) | 6.378 | +0.739 |

The router captures only 3.8% of available oracle headroom. This improvement is not meaningful.

### 5.4 Self-Evolution Results

The scaffold was allowed to modify its own code across generations:

| Version | Score | Status |
|---------|-------|--------|
| v2.0 | 78 | Baseline |
| v2.1 | 61 | Regression, rolled back |
| v2.2 | 100 | Best (+28%) |
| v2.3 | 61 | Regression, rolled back |
| v2.4 | 93 | Regression, auto-stopped |

Pattern: oscillating, not monotonic. System auto-stopped after 2 consecutive regressions.

### 5.5 Self-Review Results

When the evolved scaffold (v2.2) reviewed a paper written by the baseline scaffold (v2.0):

- v2.0 paper: 37K chars, overclaimed results. v2.2 review: **REJECT** (22 flaws found)
- Rewritten with honest positioning. v2.2 re-review: **Accept** (strengths 40 vs flaws 27)

Key finding: same data, honest positioning = Accept; overclaiming = Reject.

## 6. Discussion

### 6.1 The Surprising Result

Constitutional single-shot prompting consistently outperforms multi-round iteration. This challenges the assumption underlying many reasoning enhancement systems — that more rounds of refinement produce better reasoning.

One well-crafted prompt that embeds self-evaluation requirements achieves higher proxy scores than five rounds of generate-critique-refine, while using approximately one-third of the API calls and one-third of the wall-clock time.

### 6.2 Why Multi-Round Loses

Multi-round iteration provides generic instructions ("attack your answer," "fix weaknesses") without specifying what good reasoning looks like. Constitutional prompting gives the LLM explicit evaluation criteria in a single pass. The LLM can apply all criteria simultaneously rather than discovering them sequentially across rounds.

The exception is prediction tasks, where iterative refinement of specific numbers may genuinely benefit from multiple passes. This is the one category where multi-round won.

### 6.3 The Router Was Not Worth Building

The rule-based router added +0.028 to the fixed constitutional baseline — effectively zero. Even the oracle (always picking the best method) only reaches 6.378, suggesting that the proxy metric ceiling may be close to what constitutional prompting already achieves.

### 6.4 Self-Evolution Is Interesting but Unstable

The scaffold's ability to modify itself and improve (+28%) is notable, but the oscillating pattern (improvements followed by regressions) suggests the optimization landscape is noisy. The system correctly auto-stopped, which is itself a useful capability.

### 6.5 Self-Review Works

The most practically useful capability demonstrated is self-review: the evolved scaffold identified 22 specific flaws in an overclaimed paper and provided actionable revision guidance. This monitoring function has clearer value than the reasoning enhancement function.

### 6.6 Scaffold Maturity Assessment

The evolved scaffold (v2.2) represents an early-stage control layer rather than a learning architecture. It can sense output quality, route reasoning strategy, log decisions, and issue bias correction commands. However, it does not adapt its internal decision policy from experience: learned rules are stored but never influence future decisions, quality thresholds are hardcoded rather than data-derived, and correction commands are issued without verifying whether they actually reduced bias.

Its practical value lies in instrumentation and monitoring — not in outperforming a strong fixed constitutional prompt. This distinction is critical: a scaffold that provides observability into reasoning processes has genuine utility even when it does not improve reasoning output.

## 7. Limitations

1. **Small sample sizes**: n=3 pilot and n=80 extended are insufficient for strong statistical claims
2. **Unvalidated proxy metrics**: Keyword-based scoring has not been validated against human judgment
3. **Single model**: Only DeepSeek-chat tested
4. **No established baselines**: No comparison to Chain-of-Thought, best-of-n, or self-consistency
5. **Unequal compute**: Constitutional uses more tokens than single-pass
6. **Same-family generation and evaluation**: Questions generated and answered by same model family
7. **Proxy metric ceiling**: The scoring function may cap observable improvements

## 8. Conclusion

We set out to build a reasoning enhancement scaffold and discovered that a simple constitutional prompt renders it largely unnecessary. Our primary finding is negative: architectural complexity does not meaningfully improve over a well-crafted single prompt for our task set and metrics.

We believe this negative result is valuable. The field invests significant effort in multi-round reasoning architectures that may primarily add latency and cost without proportional quality gains. We encourage researchers to establish simple constitutional prompting as a mandatory baseline before claiming benefits from more complex systems.

Our secondary finding — that the system can usefully review and critique its own output — suggests that scaffolding may have more value as a monitoring tool than as a reasoning enhancer.

We release this work as a methodology proposal with honest reporting of both positive and negative results. The code and all experimental data are available at https://github.com/Feng-tech-ai-glass/axiomforge-lab

## References

Burns, C., Ye, H., Klein, D., & Steinhardt, J. (2023). Weak-to-strong generalization. *arXiv:2312.09390*.

Khattab, O., et al. (2024). DSPy: Compiling declarative language model calls into self-improving pipelines. *ICLR 2024*.

Shinn, N., et al. (2023). Reflexion: Language agents with verbal reinforcement learning. *NeurIPS 2023*.

Shojaee, P., et al. (2025). The illusion of thinking. *arXiv:2506.01142*.

Sumers, T. R., et al. (2024). Cognitive architectures for language agents. *TMLR 2024*.

Wang, Y. & Zhao, Y. (2023). Metacognitive prompting improves understanding in large language models. *arXiv:2308.05342*.

Yang, C., et al. (2024). Large language models as optimizers. *ICLR 2024*.

Yao, S., et al. (2023). Tree of thoughts: Deliberate problem solving with large language models. *NeurIPS 2023*.

Yuan, W., et al. (2024). Self-rewarding language models. *ICML 2024*.

Zelikman, E., et al. (2024). Quiet-STaR: Language models can teach themselves to think before speaking. *arXiv:2403.09629*.
