# DNA v3 Roadmap

## Decision

- Mainline: fixed Constitutional prompting
- Side branch: Level 2 semantic router
- Stop-loss: if routing improvement is below +0.3 over fixed Constitutional, stop the branch

The current Level 1 router is not strong enough to justify replacing the fixed Constitutional baseline. The prompt-compiler idea stays useful only if it can become a small, reliable module with measurable gains.

## Why This Is the Right Split

- Fixed Constitutional is the best known baseline on the current 80-question snapshot.
- The octopus-style router only captured a tiny fraction of the oracle headroom.
- Most of the value today comes from a good prompt, not from routing complexity.
- Future gains, if any, will likely come from better task understanding, not more scaffolding.

## Mainline

### Track A: Fixed Constitutional

Use the best current single-shot prompt as the default production path.

Acceptance:
- Mean score stays at or above the current Constitutional baseline
- Lower latency than multi-round
- No new moving parts required

If this remains the best option, keep it as the default and stop adding complexity.

## Side Branch

### Track B: Level 2 Semantic Router

Only pursue this if it can show a meaningful lift over the fixed baseline.

What changes:
- Replace keyword matching with semantic classification
- Predict task type from meaning, not surface form
- Select among a small set of strategies
- Keep the prompt compiler as a module, not a full framework

What it should output:
- task type
- recommended strategy
- token budget
- confidence
- reason for the choice

Acceptance:
- Classification accuracy at least 85%
- Mean score at least +0.3 over fixed Constitutional
- Improvement must hold across a validation split, not just the training snapshot

If any of these fail, do not continue to Level 3.

## Module Roadmap

### Phase 0: Baseline Lock

- Freeze the fixed Constitutional prompt
- Freeze the current evaluation metrics
- Keep the current 80-question snapshot as the first validation set

### Phase 1: Level 1 Validation

- Already completed
- Result: failed to beat fixed Constitutional in a meaningful way
- Action: do not promote the rule-based router

### Phase 2: Semantic Router

- Train a small classifier on question text and outcome labels
- Use embeddings or a tiny MLP
- Compare against the fixed Constitutional baseline

### Phase 3: Optional Memory Layer

- Add memory only if the router proves useful
- Use vector retrieval and forgetting, not JSON logs
- Memory should help routing decisions, not replace them

### Phase 4: Planning Layer

- Only after routing and memory are useful
- Break complex tasks into subgoals
- Keep this separate from the prompt compiler

## Stop Criteria

Stop the v3 branch if any of the following are true:

1. Semantic routing does not beat fixed Constitutional by at least +0.3
2. Improvements appear only on one category and regress on others
3. Latency or complexity grows faster than score improvement
4. The module becomes harder to debug than the gain it provides

If that happens, keep the prompt compiler as a small utility and move effort back to the stronger baseline.

## What "Success" Looks Like

- Default path remains simple and stable
- Router adds a real gain, not just a theoretical one
- Memory is only added when it solves a specific routing or adaptation problem
- The system becomes modular, not monolithic

## Bottom Line

DNA v3 should not try to become AGI.
It should become a small, reliable module in a larger cognitive system.

For now:
- Keep Constitutional as the main production path
- Treat Level 2 as an experiment
- Stop if the gain is not real

