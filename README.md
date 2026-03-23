# AxiomForge

**AI that does not just answer. It invents.**

AxiomForge is a self-improving cognitive engine for invention.

It combines a small persistent DNA core with external large models to create a system that can:
- generate ideas
- test them
- remember what works
- lock correct answers
- allocate more effort to hard problems
- improve its own strategy safely over time

---

## Why AxiomForge Exists

Most AI systems are optimized to respond.
AxiomForge is optimized to discover.

> Use a small, stable cognitive DNA to drive large models as tools for invention.

---

## Core DNA

Seven core capabilities:

- **World Model** - Predicts what will happen if the system takes an action
- **Meta-Control** - Decides what to do next, what to explore, and when to stop
- **Layered Memory** - Stores experience, compresses it into rules, uses it during decisions
- **Abstraction Engine** - Discovers patterns, rule families, and general principles
- **Answer Anchor** - Locks correct answers to prevent overthinking (Apple paper fix)
- **Effort Scaler** - Spends more reasoning budget on harder problems
- **Safe Self-Improvement** - Proposes changes, validates them, rolls back if needed

---

## What It Can Do

AxiomForge works as an invention engine across domains:

- Inventing visual patterns
- Generating and refining puzzles
- Discovering experimental rules
- Proposing cross-domain innovations
- Improving its own control policy over time

The loop: **observe -> propose -> test -> remember -> abstract -> improve**

---

## Demo

This repo includes visual demos showing the system inventing in real time.

- **AI Pattern Inventor** - generates geometric patterns, evaluates beauty with math, iterates
- **AI Puzzle Inventor** - creates 24-game puzzles, tests solvability, adjusts difficulty

---

## Experimental Results

- Discovered stable rules from 1750+ real experiments
- 39.4% training efficiency improvement
- Meta-controller achieved 100% autonomous takeover
- Cross-domain transfer validated
- Answer Anchor prevents overthinking (addresses Apple's "Illusion of Thinking" findings)
- Self-evolution: system diagnoses its own weaknesses and proposes fixes

---

## Design Principles

- Small DNA core, large model extension
- Safe recursion, not uncontrolled self-modification
- Memory affects decisions, not just storage
- High confidence protected, not overwritten by noise
- Hard problems receive more effort, not less

---

## Acknowledgements

This project was inspired by [Andrej Karpathy](https://github.com/karpathy)'s AutoResearch and his vision of AI-driven experimental optimization. His work on the "Karpathy Loop" — letting AI automatically run experiments, evaluate results, and discover improvements — provided the foundational concept that we built our cognitive architecture upon.

We extended the loop with world models, meta-control, layered memory, abstraction, answer anchoring, effort scaling, and safe self-improvement to create a system that doesn't just optimize — it invents.
