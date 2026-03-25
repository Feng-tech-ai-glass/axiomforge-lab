# AxiomForge DNA: When a Simple Prompt Beats a Complex Scaffold

**An honest experiment in LLM reasoning enhancement.**

We built a structured reasoning scaffold, tested it rigorously, and discovered that a single well-crafted prompt outperforms our entire framework. We report this honestly.

> *Without self-negation, there is no real evolution — only local optimization.*

---

## Key Findings

| Method | Avg Score (80 questions) | API Calls | Time |
|--------|------------------------|-----------|------|
| A — Single-pass | 4.08 | 1 | 34s |
| B — Multi-round (5 turns) | 4.58 | 3 | 144s |
| **C — Constitutional prompt** | **5.71** | **1** | **51s** |
| D — Adaptive | 5.10 | 2 | 51s |

**One good prompt > five rounds of iteration.** Constitutional prompting embeds self-evaluation requirements in a single call and consistently outperforms multi-round scaffolding across 5 of 6 question categories.

### What We Also Tested (and Failed)

| Experiment | Result | Conclusion |
|-----------|--------|-----------|
| Level 1: Keyword router | +0.028 | Effectively zero improvement |
| Level 2: Semantic router (2 runs) | -0.417, -1.217 | Actively harmful |
| 4,545-param trained brain | -0.25, 50% accuracy | Worse than fixed prompt |

**Every attempt to add complexity made things worse.** The trained brain independently converged to the same conclusion: "always pick Constitutional."

---

## What This Project Actually Contributes

This is not a better reasoning system. It is an honest record of building one, testing it, and discovering it wasn't needed.

1. **Negative results**: Complex scaffolding does not meaningfully improve over a well-crafted single prompt
2. **Self-refutation**: The system reviewed its own paper (REJECT, 22 flaws), then helped rewrite it (Accept)
3. **Self-evolution**: The scaffold evolved itself (+28%), but with oscillating, unstable convergence
4. **Methodology**: A systematic framework for testing whether architectural complexity is justified

---

## Self-Evolution Data

The scaffold modified its own code across generations:

| Version | Score | Status |
|---------|-------|--------|
| v2.0 | 78 | Baseline |
| v2.1 | 61 | Regression, rolled back |
| v2.2 | 100 | Best (+28%) |
| v2.3 | 61 | Regression, rolled back |
| v2.4 | 93 | Auto-stopped after 2 regressions |

---

## The Self-Review Experiment

The evolved scaffold (v2.2) reviewed a paper written by the baseline (v2.0):

- **First review**: REJECT — found 22 specific flaws, including overclaimed results
- **After honest rewrite**: Accept — strengths (40) outweighed flaws (27)

Same data, honest positioning = Accept. Overclaiming = Reject.

---

## Documentation

| File | Content |
|------|---------|
| [docs/PAPER.md](docs/PAPER.md) | Full paper with all experimental data |
| [docs/FINAL_PACKAGE.md](docs/FINAL_PACKAGE.md) | Project summary and verified results |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Frozen roadmap (main line: fixed Constitutional) |

---

## Limitations

1. Small sample sizes (n=3 pilot, n=80 extended)
2. No human evaluation — all metrics are automated keyword-based proxies
3. No comparison to Chain-of-Thought or other established baselines
4. Single model tested (DeepSeek-chat)
5. Constitutional prompt uses more tokens than single-pass — not equal-compute
6. Proxy metrics are unvalidated — "more self-criticism keywords" ≠ "better reasoning"
7. Bias detector is self-referential (same LLM evaluates itself)

---

## The Honest Conclusion

We set out to build a cognitive architecture for LLMs. Through systematic experimentation, we discovered:

- A simple constitutional prompt renders complex scaffolding unnecessary
- Routing and classification add overhead without proportional benefit
- The most valuable capability we built was self-review, not reasoning enhancement
- A 4,545-parameter brain trained for 200 epochs learned one thing: "always use the simple prompt"

We believe reporting these negative results honestly is more valuable than claiming our scaffold works.

---

## Acknowledgements

Inspired by [Andrej Karpathy](https://github.com/karpathy)'s vision of AI-driven experimental optimization.

Built with Claude (Anthropic) and DeepSeek APIs.

---

## License

This project uses a hybrid open-core model. See LICENSE for details.

---

**Author**: Di Wu, Independent Researcher | [HuggingFace Space](https://huggingface.co/spaces/wudifff/axiomforge-dna) | wudifff@gmail.com
