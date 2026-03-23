# AxiomForge

**A cognitive engine for invention, memory, and safe self-improvement.**

**AI that does not just answer. It invents.**

AxiomForge combines a small persistent DNA core with external large models to create a system that can propose ideas, test them, remember what works, and improve its own strategy over time.

[Live Demo](./demo/ai_pattern_inventor_demo.html) | [Read the Docs](./STRUCTURE.md)

---

## What It Does

- **Invent** new ideas, patterns, and solutions
- **Remember** what works and compress it into reusable rules
- **Improve** safely through validation, rollback, and recursive self-updates

---

## Demo

- **AI Pattern Inventor** -- generates geometric patterns, evaluates beauty, and iterates toward stronger designs
- **AI Universal Inventor** -- takes any problem, generates candidate solutions, scores them, and refines the best one

Both modes use your own API key (OpenAI / DeepSeek / Anthropic). Your key stays in your browser. We never see it.

---

## Core DNA

Seven core capabilities:

- **World Model** -- Predicts what will happen if the system takes an action
- **Meta-Control** -- Decides what to do next, what to explore, and when to stop
- **Layered Memory** -- Stores experience, compresses it into rules, uses it during decisions
- **Abstraction Engine** -- Discovers patterns, rule families, and general principles
- **Answer Anchor** -- Locks correct answers to prevent overthinking (Apple paper fix)
- **Effort Scaler** -- Spends more reasoning budget on harder problems
- **Safe Self-Improvement** -- Proposes changes, validates them, rolls back if needed

---

## Experimental Results

- DNA provides **+29% absolute improvement** over random search (1915 experiments)
- **35 rules** and **3 universal principles** discovered automatically
- **39.4% training efficiency improvement**
- Meta-controller achieved **100% autonomous takeover** with safe fallback
- Cross-domain transfer validated across 2 domains
- System diagnoses its own weaknesses and proposes fixes (recursive self-improvement)

---

## Design Principles

- Small DNA core, large model extension
- Safe recursion, not uncontrolled self-modification
- Memory affects decisions, not just storage
- High confidence protected, not overwritten by noise
- Hard problems receive more effort, not less
- Good discoveries become reusable knowledge

---

## Open Core Approach

Open:
- Visual demos
- Evaluation tools
- Integration layers
- Public examples

Protected:
- DNA core strategies
- Training data
- Self-improvement rules
- Production weights

---

## Status

AxiomForge is actively evolving.

Current focus:
- Long-term stability testing
- Memory-to-decision integration
- Cross-domain generalization
- Safe recursive self-improvement

---

## Acknowledgements

This project was inspired by [Andrej Karpathy](https://github.com/karpathy)'s AutoResearch and his vision of AI-driven experimental optimization. His work on the "Karpathy Loop" -- letting AI automatically run experiments, evaluate results, and discover improvements -- provided the foundational concept that we built our cognitive architecture upon.

We extended the loop with world models, meta-control, layered memory, abstraction, answer anchoring, effort scaling, and safe self-improvement to create a system that doesn't just optimize -- it invents.

---

## License

This project uses a hybrid open-core model. See LICENSE for details.
