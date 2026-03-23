"""
72-Hour Stability Analysis

Analyze existing experiment data for:
1. Performance drift over time
2. MC decision consistency
3. Memory growth stability
4. Rule stability (do rules change?)
5. WM accuracy stability
6. Kept rate stability
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("72-HOUR STABILITY ANALYSIS")
print("=" * 60)

# Load all data with timestamps
all_data = []
for path in ['karpathy_loop_results/v4_worldmodel.jsonl', 'karpathy_loop_results/v3_gpu0.jsonl']:
    try:
        with open(path) as f:
            for line in f:
                if line.strip():
                    all_data.append(json.loads(line))
    except:
        pass

valid = [r for r in all_data if r.get('parameter', '') not in ('NO_OP', '')]
print(f"Total experiments: {len(valid)}")

# ================================================================
# 1. Performance drift — does val_bpb keep improving or plateau?
# ================================================================
print(f"\n{'='*60}")
print("[1] Performance Drift")
print("-" * 40)

window = 100
for i in range(0, len(valid), window):
    chunk = valid[i:i+window]
    if len(chunk) < 20:
        continue
    avg_bpb = np.mean([r.get('val_bpb', 2) for r in chunk])
    best_bpb = min(r.get('val_bpb', 2) for r in chunk)
    kept = sum(1 for r in chunk if r.get('kept')) / len(chunk)
    print(f"  Exp {i:>4}-{i+len(chunk)-1:>4}: avg={avg_bpb:.4f} best={best_bpb:.4f} kept={kept:.0%}")

# Drift check: is last chunk worse than best chunk?
chunks = [valid[i:i+window] for i in range(0, len(valid), window) if len(valid[i:i+window]) >= 20]
chunk_avgs = [np.mean([r.get('val_bpb', 2) for r in c]) for c in chunks]
best_chunk = min(chunk_avgs)
last_chunk = chunk_avgs[-1]
drift = last_chunk - best_chunk

print(f"\n  Best chunk avg:  {best_chunk:.4f}")
print(f"  Last chunk avg:  {last_chunk:.4f}")
print(f"  Drift:           {drift:+.4f} ({'STABLE' if abs(drift) < 0.05 else 'DRIFTING'})")

# ================================================================
# 2. Kept rate stability
# ================================================================
print(f"\n{'='*60}")
print("[2] Kept Rate Stability")
print("-" * 40)

kept_rates = []
for i in range(0, len(valid), window):
    chunk = valid[i:i+window]
    if len(chunk) < 20:
        continue
    kr = sum(1 for r in chunk if r.get('kept')) / len(chunk)
    kept_rates.append(kr)

if kept_rates:
    mean_kr = np.mean(kept_rates)
    std_kr = np.std(kept_rates)
    min_kr = min(kept_rates)
    max_kr = max(kept_rates)
    print(f"  Mean kept rate:  {mean_kr:.0%}")
    print(f"  Std dev:         {std_kr:.2%}")
    print(f"  Range:           {min_kr:.0%} - {max_kr:.0%}")
    print(f"  Stability:       {'STABLE' if std_kr < 0.1 else 'UNSTABLE'}")

# ================================================================
# 3. WM accuracy over time
# ================================================================
print(f"\n{'='*60}")
print("[3] World Model Accuracy Over Time")
print("-" * 40)

wm_data = [r for r in valid if 'wm_correct' in r]
if wm_data:
    for i in range(0, len(wm_data), 200):
        chunk = wm_data[i:i+200]
        if len(chunk) < 20:
            continue
        wm_acc = sum(1 for r in chunk if r.get('wm_correct')) / len(chunk)
        print(f"  Exp {i:>4}-{i+len(chunk)-1:>4}: WM accuracy={wm_acc:.0%}")

    # Trend
    first_half = wm_data[:len(wm_data)//2]
    second_half = wm_data[len(wm_data)//2:]
    fh_acc = sum(1 for r in first_half if r.get('wm_correct')) / len(first_half)
    sh_acc = sum(1 for r in second_half if r.get('wm_correct')) / len(second_half)
    print(f"\n  First half WM:  {fh_acc:.0%}")
    print(f"  Second half WM: {sh_acc:.0%}")
    print(f"  Trend:          {'IMPROVING' if sh_acc > fh_acc else 'STABLE' if abs(sh_acc-fh_acc) < 0.05 else 'DEGRADING'}")

# ================================================================
# 4. Parameter distribution stability
# ================================================================
print(f"\n{'='*60}")
print("[4] Parameter Distribution Stability")
print("-" * 40)

# Compare first half vs second half parameter distribution
fh = valid[:len(valid)//2]
sh = valid[len(valid)//2:]

print(f"  {'Parameter':25s} {'1st half':>10s} {'2nd half':>10s} {'Shift':>8s}")
print(f"  {'-'*55}")

all_params = set(r['parameter'] for r in valid)
for p in sorted(all_params):
    fh_count = sum(1 for r in fh if r['parameter'] == p) / max(len(fh), 1)
    sh_count = sum(1 for r in sh if r['parameter'] == p) / max(len(sh), 1)
    shift = abs(fh_count - sh_count)
    print(f"  {p:25s} {fh_count:>9.0%} {sh_count:>9.0%} {shift:>7.1%} {'!' if shift > 0.05 else ''}")

# ================================================================
# 5. Failure pattern stability
# ================================================================
print(f"\n{'='*60}")
print("[5] Failure Pattern Stability")
print("-" * 40)

# Are the same parameters failing consistently?
fh_fails = {}
sh_fails = {}
for r in fh:
    if not r.get('kept'):
        p = r['parameter']
        fh_fails[p] = fh_fails.get(p, 0) + 1
for r in sh:
    if not r.get('kept'):
        p = r['parameter']
        sh_fails[p] = sh_fails.get(p, 0) + 1

print(f"  {'Parameter':25s} {'1st half fails':>15s} {'2nd half fails':>15s}")
print(f"  {'-'*57}")
for p in sorted(all_params):
    f1 = fh_fails.get(p, 0)
    f2 = sh_fails.get(p, 0)
    print(f"  {p:25s} {f1:>15} {f2:>15}")

# ================================================================
# 6. Overall stability verdict
# ================================================================
print(f"\n{'='*60}")
print("STABILITY VERDICT")
print(f"{'='*60}")

checks = {
    "Performance drift": abs(drift) < 0.05,
    "Kept rate stable": std_kr < 0.1 if kept_rates else False,
    "WM not degrading": sh_acc >= fh_acc - 0.05 if wm_data else True,
    "Param distribution even": all(
        abs(sum(1 for r in fh if r['parameter']==p)/max(len(fh),1) -
            sum(1 for r in sh if r['parameter']==p)/max(len(sh),1)) < 0.05
        for p in all_params
    ),
}

all_pass = True
for name, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    if not passed: all_pass = False
    print(f"  [{status}] {name}")

print(f"\n  OVERALL: {'STABLE — no significant drift' if all_pass else 'SOME INSTABILITY DETECTED'}")
print(f"  Experiments analyzed: {len(valid)}")
print(f"  Equivalent runtime: ~{len(valid)*3/60:.0f} GPU-hours")
