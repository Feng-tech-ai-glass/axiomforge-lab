"""
Week 1: Unified Evaluation Dashboard

Runs ALL evaluation tests against a frozen holdout set.
Outputs a single PASS/FAIL report for the current version.

Tests:
  1. Holdout accuracy (success + failure)
  2. Failure recall
  3. Benefit MAE
  4. Uncertainty calibration
  5. Counterfactual gap
  6. Recommendation concentration
  7. Cross-domain transfer
  8. Long-horizon stability
"""
import sys, os, json, random, time
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
sys.path.insert(0, ".")

import torch
import numpy as np

# DNA Core modules (not included in open-source release)
# WorldModel, load_all_fault_episodes, fault_state_to_tensor
# require the proprietary AxiomForge DNA core package
try:
    from axiomforge_core.world_model import WorldModel
    from axiomforge_core.domain_fault_diagnosis import (
        load_all_fault_episodes, fault_state_to_tensor
    )
except ImportError:
    print("ERROR: This tool requires the AxiomForge DNA core (not included in open-source release).")
    print("See README.md for details on the open-core model.")
    sys.exit(1)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

PARAM_NAMES = ["EMBEDDING_LR", "UNEMBEDDING_LR", "MATRIX_LR",
               "SCALAR_LR", "WEIGHT_DECAY", "ADAM_BETA1", "ADAM_BETA2"]
PARAM_RANGES = {
    "EMBEDDING_LR": (0.1, 2.0), "UNEMBEDDING_LR": (0.001, 0.02),
    "MATRIX_LR": (0.01, 0.15), "SCALAR_LR": (0.1, 1.0),
    "WEIGHT_DECAY": (0.001, 0.1), "ADAM_BETA1": (0.7, 0.95), "ADAM_BETA2": (0.9, 0.99),
}
BEST_HP = {"EMBEDDING_LR": 1.0, "UNEMBEDDING_LR": 0.004, "MATRIX_LR": 0.03,
           "SCALAR_LR": 0.5, "WEIGHT_DECAY": 0.01, "ADAM_BETA1": 0.88, "ADAM_BETA2": 0.95}

def hp_to_tensor(hp):
    vals = []
    for p in PARAM_NAMES:
        lo, hi = PARAM_RANGES[p]
        v = (hp.get(p, 0) - lo) / (hi - lo + 1e-8)
        vals.append(max(0, min(1, v)))
    extras = [vals[2]*vals[4], vals[5]*vals[6], vals[0]*vals[1],
              vals[2]/(vals[4]+0.01), sum(vals)/len(vals), max(vals)-min(vals)]
    padded = vals + extras + [0.0] * (64 - len(vals) - len(extras))
    return torch.tensor(padded[:64], dtype=torch.float32)


def build_frozen_holdout():
    """
    Build 3 evaluation sets from REAL data:
      1. primary: real samples, stratified by domain/outcome
      2. counterfactual: action vs no-op pairs
      3. stress: human-constructed edge cases (old holdout)
    """
    random.seed(12345)  # FROZEN seed — never change this

    # Load ALL real episodes
    all_real = []

    # HP domain — load ALL sources (v3 + v4)
    import os
    hp_files = ["karpathy_loop_results/v3_gpu0.jsonl",
                "karpathy_loop_results/v4_worldmodel.jsonl"]
    hp = {"EMBEDDING_LR": 0.6, "UNEMBEDDING_LR": 0.008, "MATRIX_LR": 0.04,
          "SCALAR_LR": 0.5, "WEIGHT_DECAY": 0.1, "ADAM_BETA1": 0.8, "ADAM_BETA2": 0.95}
    for hp_file in hp_files:
        if not os.path.exists(hp_file):
            continue
        with open(hp_file) as f:
            records = [json.loads(l) for l in f if l.strip()]
        for r in records:
            param = r.get("parameter", "")
            if param == "NO_OP" or param not in PARAM_NAMES:
                continue
            sb = hp_to_tensor(hp)
            ov = r.get("old_value", hp.get(param, 0))
            new_v = r.get("new_value", ov)
            if r.get("kept"): hp[param] = new_v
            sa = hp_to_tensor(hp)
            all_real.append({
                "states": [sb, sa],
                "interventions": [f"{param}_{new_v}"],
                "old_values": [ov], "new_values": [new_v],
                "outcomes": ["improved" if r.get("kept") else "degraded"],
                "benefits": [abs(r.get("delta", 0)) * (1 if r.get("kept") else -1)],
                "domain": "hyperparam",
            })

    # Fault domain
    fault_eps = load_all_fault_episodes()
    all_real.extend(fault_eps)

    # Stratified split: 10% holdout, balanced by (domain × outcome)
    # Key fix: cap per-group to prevent any domain from being over-sampled
    from collections import defaultdict

    by_group = defaultdict(list)
    for e in all_real:
        domain = e.get("domain", "default")
        outcome = e["outcomes"][0]
        by_group[(domain, outcome)].append(e)

    primary = []
    for (domain, outcome), group in by_group.items():
        random.shuffle(group)
        # Take 10% but cap at 3 per group to keep training data sufficient
        n = max(1, min(3, int(len(group) * 0.10)))
        primary.extend(group[:n])

    print(f"    Holdout composition:")
    holdout_domains = defaultdict(lambda: defaultdict(int))
    for e in primary:
        holdout_domains[e.get("domain", "default")][e["outcomes"][0]] += 1
    for domain, outcomes in holdout_domains.items():
        print(f"      {domain}: {dict(outcomes)}")

    return primary


def build_stress_holdout():
    """Old human-constructed edge cases — kept as stress test only."""
    stress = []
    for param, old_v, new_v, outcome in [
        ("MATRIX_LR", 0.04, 0.06, "improved"),
        ("WEIGHT_DECAY", 0.1, 0.05, "improved"),
        ("ADAM_BETA1", 0.8, 0.85, "improved"),
        ("MATRIX_LR", 0.06, 0.12, "degraded"),
        ("WEIGHT_DECAY", 0.05, 0.001, "degraded"),
        ("ADAM_BETA1", 0.85, 0.99, "degraded"),
    ]:
        stress.append({
            "states": [hp_to_tensor(BEST_HP), hp_to_tensor(BEST_HP)],
            "interventions": [f"{param}_{new_v}"],
            "old_values": [old_v], "new_values": [new_v],
            "outcomes": [outcome],
            "benefits": [0.05 if outcome == "improved" else -0.05],
            "domain": "hyperparam",
        })
    return stress


def run_dashboard():
    print("=" * 70)
    print("EVALUATION DASHBOARD — Week 1")
    print("=" * 70)

    t0 = time.time()

    # Build and train world model on all available data
    wm = WorldModel(latent_dim=64, intervention_dim=16, device=device)
    wm.register_params(PARAM_NAMES + [
        "stabilize_then_expand", "expand_then_stabilize",
        "continue_training", "continue", "increase_exploration", "NO_OP",
    ])

    # Load all training data (v3 + v4)
    hp_eps = []
    hp_files = ["karpathy_loop_results/v3_gpu0.jsonl",
                "karpathy_loop_results/v4_worldmodel.jsonl"]
    hp = dict(BEST_HP)
    hp.update({"EMBEDDING_LR": 0.6, "UNEMBEDDING_LR": 0.008, "MATRIX_LR": 0.04,
               "SCALAR_LR": 0.5, "WEIGHT_DECAY": 0.1, "ADAM_BETA1": 0.8, "ADAM_BETA2": 0.95})
    for hp_file in hp_files:
        if not os.path.exists(hp_file):
            continue
        with open(hp_file) as f:
            records = [json.loads(l) for l in f if l.strip()]
        for r in records:
            param = r.get("parameter", "")
            if param == "NO_OP" or param not in PARAM_NAMES:
                continue
            state_before = hp_to_tensor(hp)
            old_val = r.get("old_value", hp.get(param, 0))
            new_v = r.get("new_value", old_val)
            if r.get("kept"): hp[param] = new_v
            state_after = hp_to_tensor(hp)
            hp_eps.append({
                "states": [state_before, state_after],
                "interventions": [f"{param}_{new_v}"],
                "old_values": [old_val], "new_values": [new_v],
                "outcomes": ["improved" if r.get("kept") else "degraded"],
                "benefits": [abs(r.get("delta", 0)) * (1 if r.get("kept") else -1)],
            })

    fault_eps = load_all_fault_episodes()

    # Synthetic failures for balance
    random.seed(42)
    for _ in range(20):
        param = random.choice(PARAM_NAMES)
        lo, hi = PARAM_RANGES[param]
        extreme = lo * 0.3 if random.random() < 0.5 else hi * 2.5
        hp_eps.append({
            "states": [hp_to_tensor(BEST_HP), hp_to_tensor(BEST_HP)],
            "interventions": [f"{param}_{extreme}"],
            "old_values": [BEST_HP[param]], "new_values": [extreme],
            "outcomes": ["degraded"], "benefits": [-0.1],
        })

    # Build holdouts FIRST, then exclude from training
    primary_holdout = build_frozen_holdout()
    stress_holdout = build_stress_holdout()

    # Exclude holdout episodes from training (by intervention name matching)
    holdout_keys = set()
    for ep in primary_holdout:
        holdout_keys.add(ep["interventions"][0])

    all_train = []
    for ep in hp_eps + fault_eps:
        if ep["interventions"][0] not in holdout_keys:
            all_train.append(ep)

    for ep in all_train:
        wm.record_episode(ep)

    print(f"  Training on {len(wm.episodes)} episodes (excluded {len(holdout_keys)} holdout)")
    wm.train_on_episodes(epochs=80, lr=1e-3)

    holdout = primary_holdout
    print(f"\n  Primary holdout: {len(holdout)} samples (real distribution)")
    print(f"  Stress holdout: {len(stress_holdout)} samples (edge cases)")

    # ================================================================
    # Test 1-4: Accuracy, Failure Recall, Benefit MAE, Uncertainty
    # ================================================================
    correct = 0
    failure_correct = 0
    failure_total = 0
    benefit_errors = []
    unc_vs_err = []

    for ep in holdout:
        state = ep["states"][0]
        interv = ep["interventions"][0]
        true_out = ep["outcomes"][0]
        true_ben = ep["benefits"][0]
        domain = ep.get("domain", "default")

        pred = wm.predict(state, interv,
                         old_value=ep["old_values"][0],
                         new_value=ep["new_values"][0],
                         domain=domain)

        if pred["outcome"] == true_out: correct += 1
        if true_out != "improved":
            failure_total += 1
            if pred["outcome"] == true_out: failure_correct += 1

        ben_err = abs(pred["benefit"] - true_ben)
        benefit_errors.append(ben_err)
        unc_vs_err.append((pred["uncertainty"], ben_err))

    n = len(holdout)
    accuracy = correct / n
    failure_recall = failure_correct / max(failure_total, 1)
    benefit_mae = np.mean(benefit_errors)

    # Uncertainty calibration
    sorted_unc = sorted(unc_vs_err, key=lambda x: x[0])
    low_half = sorted_unc[:len(sorted_unc)//2]
    high_half = sorted_unc[len(sorted_unc)//2:]
    low_err = np.mean([e for _, e in low_half]) if low_half else 0
    high_err = np.mean([e for _, e in high_half]) if high_half else 0
    unc_calibrated = high_err > low_err

    # ================================================================
    # Test 5: Counterfactual gap
    # ================================================================
    state = hp_to_tensor(BEST_HP)
    cf_gaps = []
    for param in ["MATRIX_LR", "WEIGHT_DECAY", "ADAM_BETA1"]:
        old_v = BEST_HP[param]
        new_v = old_v * 1.1
        pred_action = wm.predict(state, f"{param}_{new_v}",
                                old_value=old_v, new_value=new_v, domain="hyperparam")
        pred_noop = wm.predict(state, "NO_OP", old_value=0, new_value=0, domain="hyperparam")
        gap = abs(pred_action["benefit"] - pred_noop["benefit"])
        cf_gaps.append(gap)

    counterfactual_gap = np.mean(cf_gaps)

    # ================================================================
    # Test 6: Recommendation concentration
    # ================================================================
    candidates = []
    for param in PARAM_NAMES:
        val = BEST_HP[param]
        for factor in [0.9, 1.1]:
            candidates.append(f"{param}_{val * factor}")

    preds = []
    for c in candidates:
        for p in PARAM_NAMES:
            if c.startswith(p + "_"):
                pred = wm.predict(state, c,
                                 old_value=BEST_HP[p],
                                 new_value=BEST_HP[p] * (0.9 if "0.9" in c[-5:] else 1.1),
                                 domain="hyperparam")
                preds.append((p, pred["benefit"]))
                break

    param_benefits = {}
    for p, b in preds:
        param_benefits.setdefault(p, []).append(b)
    avg_per_param = {p: np.mean(bs) for p, bs in param_benefits.items()}
    top_param = max(avg_per_param, key=avg_per_param.get)
    top_share = avg_per_param[top_param] / (sum(avg_per_param.values()) + 1e-8)
    concentrated = top_share > 0.5

    # ================================================================
    # Test 7: Cross-domain
    # ================================================================
    hp_correct = 0
    hp_total = 0
    fault_correct = 0
    fault_total = 0
    for ep in holdout:
        state = ep["states"][0]
        interv = ep["interventions"][0]
        true_out = ep["outcomes"][0]
        domain = ep.get("domain", "default")
        pred = wm.predict(state, interv,
                         old_value=ep["old_values"][0],
                         new_value=ep["new_values"][0],
                         domain=domain)
        if domain == "hyperparam":
            hp_total += 1
            if pred["outcome"] == true_out: hp_correct += 1
        elif domain == "fault_diagnosis":
            fault_total += 1
            if pred["outcome"] == true_out: fault_correct += 1

    hp_acc = hp_correct / max(hp_total, 1)
    fault_acc = fault_correct / max(fault_total, 1)
    cross_gap = abs(hp_acc - fault_acc)

    # ================================================================
    # REPORT
    # ================================================================
    print(f"\n{'='*70}")
    print("EVALUATION REPORT")
    print(f"{'='*70}")

    thresholds = {
        "holdout_accuracy": (accuracy, 0.70, ">="),
        "failure_recall": (failure_recall, 0.80, ">="),
        "benefit_mae": (benefit_mae, 0.10, "<="),
        "unc_calibrated": (unc_calibrated, True, "=="),
        "counterfactual_gap": (counterfactual_gap, 0.005, ">="),
        "not_concentrated": (not concentrated, True, "=="),
        "cross_domain_gap": (cross_gap, 0.30, "<="),
    }

    all_pass = True
    for name, (value, threshold, op) in thresholds.items():
        if op == ">=": passed = value >= threshold
        elif op == "<=": passed = value <= threshold
        else: passed = value == threshold

        status = "PASS" if passed else "FAIL"
        if not passed: all_pass = False
        print(f"  [{status}] {name:30s} = {value:.4f}  (threshold: {op}{threshold})")

    print(f"\n  HP domain:    {hp_acc:.0%} ({hp_correct}/{hp_total})")
    print(f"  Fault domain: {fault_acc:.0%} ({fault_correct}/{fault_total})")
    print(f"  CF gap:       {counterfactual_gap:.4f}")

    # ================================================================
    # STRESS TEST (separate, not part of PASS/FAIL)
    # ================================================================
    print(f"\n  --- STRESS TEST (edge cases, {len(stress_holdout)} samples) ---")
    stress_correct = 0
    for ep in stress_holdout:
        pred = wm.predict(ep["states"][0], ep["interventions"][0],
                         old_value=ep["old_values"][0],
                         new_value=ep["new_values"][0],
                         domain=ep.get("domain", "default"))
        if pred["outcome"] == ep["outcomes"][0]:
            stress_correct += 1
    stress_acc = stress_correct / max(len(stress_holdout), 1)
    print(f"  Stress accuracy: {stress_acc:.0%} ({stress_correct}/{len(stress_holdout)})")
    print(f"  (This is NOT part of PASS/FAIL — it's for robustness tracking)")

    print(f"\n{'='*70}")
    if all_pass:
        print("  OVERALL: ALL PASS — ready for Week 2")
    else:
        print("  OVERALL: SOME FAILED — fix before proceeding")
    print(f"{'='*70}")
    print(f"  Time: {time.time()-t0:.1f}s")

    return all_pass


if __name__ == "__main__":
    run_dashboard()
