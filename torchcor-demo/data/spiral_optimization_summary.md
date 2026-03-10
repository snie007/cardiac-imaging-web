# Spiral/reentry pacing protocol sweep

- Scenario: `protocol_sweep_20260310`
- Device: `cuda:0`
- Candidates tested: **6**
- Sweep dt: 0.15 ms; confirmation dt: 0.1 ms

## Ranked candidates
1. `cand_04` score=0.674 (strong_reentry_like)
2. `cand_03` score=0.331 (weak_reentry_like)
3. `cand_02` score=0.252 (weak_reentry_like)
4. `cand_05` score=0.113 (weak_reentry_like)
5. `cand_00` score=0.108 (weak_reentry_like)
6. `cand_01` score=0.104 (weak_reentry_like)

## Selected protocol
- From sweep: `cand_04` (score=0.674, class=strong_reentry_like)
- Confirmation: score=0.665, class=near_reentry_like
- Reactivated >=2 (post): 0.5166
- Spatial entropy post mean: 0.9130
- Heterogeneity persistence: 0.3333

Interpretation: heuristic evidence only; no clinical claim of fibrillation.
