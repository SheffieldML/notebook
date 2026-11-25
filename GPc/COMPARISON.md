# GPy ↔ GPc notebook comparison program

Living notes for CIP-0007: treat each GPy tutorial as the **spec**, walk its GPc twin cell-by-cell, and record (1) API / behaviour mismatches, (2) missing explanation, (3) intentional shortenings.

## Rubric

For each pair, ask:

1. **Pedagogy** — Does the GPc twin still teach *why*, or only *how*? Prefer restoring generative-model / approximation narrative over cloning GPy’s API surface.
2. **API map** — Is every GPy call either mirrored, aliased, or explicitly deferred with a one-line reason?
3. **Sign / objective** — Is `objective()` (= −log Z / −log-likelihood) called out wherever GPy prints `log_likelihood`?
4. **Plots** — Where GPy uses `m.plot` / `m.plot_f` / `fixed_inputs`, does GPc show the same quantity with matplotlib / `plot_1d` / `predict_noiseless`?
5. **Scope honesty** — Deferred features (sparse EP, `optimize_restarts`, hetero, `infer_newX`) named once, not silently dropped mid-story.

Severity:

| Tag | Meaning |
|---|---|
| **gap** | Reader following GPy will miss a concept or get a wrong impression |
| **api** | Behaviour or naming differs; needs a callout (may already have one) |
| **ok-short** | Shorter than GPy on purpose; content is still enough |
| **defer** | Out of façade subset; leave a pointer, do not fake it |

## Pairing map

| GPy | GPc | Wave | Status |
|---|---|---|---|
| `basic_gp.ipynb` | `basic_gp.ipynb` | 1 | Reviewed 2026-11-25 |
| `basic_kernels.ipynb` | `basic_kernels.ipynb` | 1 | Reviewed 2026-11-25 |
| `sparse_gp_regression.ipynb` | `sparse_gp_regression.ipynb` | 1 | Reviewed 2026-11-25 |
| `basic_classification.ipynb` | `basic_classification.ipynb` | 1 | Reviewed; narrative patch applied 2026-11-25 |
| `Poisson regression tutorial.ipynb` | `poisson_regression.ipynb` | 1 | Reviewed; narrative patch applied 2026-11-25 |
| `coregionalized_regression_tutorial.ipynb` | `coregionalization_toy.ipynb` | 2 | Reviewed; narrative patch applied 2026-11-25 |
| (GPy `gplvm_oil_100` / `BayesianGPLVM`; not in this repo) | `gplvm_oil100` / `bgplvm_oil100` | 2 | Reviewed vs native docs; narrative patch applied 2026-11-25 |
| (GPy `MRD` / DeepGP libs; not in this repo) | `mrd_toy`, `deepgp_sinc` | 2 | Reviewed vs native docs; narrative patch applied 2026-11-25 |
| Olympics / MLP / ExpQuad / weight-space | matching `GPc/*` | 3 | Reviewed; narrative patch applied 2026-11-25 |
| `sampling_hmc.ipynb` | `sampling_hmc.ipynb` | 4 | Ported 2026-11-25 (CIP-003B / a11); `infer_newX` deferred |

## Wave 1 findings (2026-11-25)

### `basic_gp` — mostly solid

- **ok-short**: Differences block covers objective sign, CIP-0027 noise, paths, ARD `inputScale_*`, no `optimize_restarts`.
- **gap (low)**: GPy’s short lesson that random restarts often land on the same minimum is absent. One sentence under the optimise cell would close it without implementing restarts.
- **api**: 2-D White-on-kernel + `likelihood.variance` is explained; keep that callout if the code changes.

### `basic_kernels` — good parity after a10

- **ok-short**: Catalogue + compounds + `active_dims` + new `k.K` / `k.plot` section.
- **api**: GPy keeps live-linked children after `+`; GPc snapshots parts — already noted in “Combining kernels”.
- **gap (low)**: GPy’s explicit “kernels remain linked” demo is the inverse lesson; worth a one-liner that editing `k1` after `k1+k2` does **not** mutate the compound.

### `sparse_gp_regression` — closest twin

- **ok-short**: Titsias free-energy story, poor-Z clump → underfit, free Z, more inducing, KL / bound tightness — all present.
- **api**: DTCVAR default and `objective()` sign called out. Good reference twin for other ports.

### `basic_classification` — largest pedagogy cut

Markdown ~46% of GPy length. Code path is fine (EP + Laplace + `predict_proba`); explanation is thin.

| Finding | Tag | Fix |
|---|---|---|
| No “why approximate?” opener (non-conjugate Bernoulli / probit) | **gap** | Restore 2–3 sentences from GPy intro |
| Generative model shown in plots but not narrated (latent → Φ → Bernoulli) | **gap** | Expand “Generative model” cell |
| EP interleaved with hyperparameter optimisation not explained | **gap** | Add short paragraph before/after first `optimize` |
| No mention that Laplace is the other classic approx (GPy points to it; we already run it) | **gap** | Tie Laplace section back to that sentence |
| Density / `plot_f` fine-grain Bernoulli surprise plot | **defer** | Optional later; not required for v1 |
| MCMC for kernel params | **ok-short** | See `sampling_hmc` (Wave 4); not repeated here |

### `poisson_regression` — API ok, story compressed hard

Markdown ~31% of GPy. Bus toy + Laplace fit work; several teaching beats are gone.

| Finding | Tag | Fix |
|---|---|---|
| Log-link / non-negativity of λ barely motivated | **gap** | Restore GPy’s “GP on λ can go negative” paragraph |
| Large-count → Gaussian approximation path only in the closing table | **gap** | One explicit sentence + optional small PMF-vs-Gaussian figure (GPy has two) |
| Pre- vs post-optimise “lengthscale too small” beat missing | **gap** | Show objective / lengthscale before optimise (already printed) with narrative |
| RBF lengthscale as *timescale* for half-hour bins | **gap** | One sentence when constructing the kernel |
| `plot` / `plot_f` vs `predict_noiseless` + `exp` | **api** | Already shown; name the GPy equivalents once |
| Student-t bonus | **ok-short** | Extra vs GPy; keep |

### Cross-cutting

- Install cells now enforce `gpc>=0.1.0a10` with a real version tuple (string `a8 >= a10` was a silent footgun).
- CIP-0007 still lists Poisson under “explicit non-goals”; update when closing Wave 1 narrative patches.



## Wave 2 findings (2026-11-25)

### `coregionalization_toy` ↔ GPy `coregionalized_regression_tutorial`

Markdown was ~41% of GPy. Structure already covered ICM, independent-vs-shared, Matérn, LCM.

| Finding | Tag | Fix |
|---|---|---|
| Kronecker / \(B=WW^\top+\mathrm{diag}(\kappa)\) under-explained | **gap** | Restored in intro + ICM section |
| IndexWhite vs spherical noise (GPy’s two noise params) | **gap** | Called out in intro / ICM model |
| Bias+Linear mean-offset sequence | **ok-short** / **defer** | Point to GPy; sinusoid toy keeps light LCM |
| Explicit `Y_metadata` / output_index deep dive | **api** | `predict_output` explained as the façade path |
| MixedNoise / Bernoulli multi-output | **defer** | Named at LCM close |

### `gplvm_oil100` (GPc-led; GPy example not in this repo)

| Finding | Tag | Fix |
|---|---|---|
| Unsupervised latent-\(X\) story missing | **gap** | Intro + MAP fit section |
| pods `X`/`Y` swap easy to miss | **api** | Load cell + intro notes |
| Labels colour only | **gap** | Stated in intro / load |
| Link to Bayesian sibling | **ok-short** | Cross-link to `bgplvm_oil100` |

### `bgplvm_oil100` (GPc-led)

| Finding | Tag | Fix |
|---|---|---|
| Section headers only — no \(q(X)\) / VarDTC / ARD story | **gap** | Full intro + fit / latent sections |
| ELBO vs `objective()` sign | **api** | Stated |
| SVI path | **defer** | CLI pointer kept |

### `mrd_toy` (GPc-led)

| Finding | Tag | Fix |
|---|---|---|
| Shared vs private ARD / `factorize_space` under-explained | **gap** | Intro + fit + plot sections |
| Single-KL assembly | **api** | Fit section |
| Plot shows dims 0–1 only | **ok-short** | Note that private structure may sit on dim 2 |

### `deepgp_sinc` (GPc-led)

| Finding | Tag | Fix |
|---|---|---|
| Why stack layers / DSVI missing | **gap** | Intro rewritten |
| `chi`, residual-off, when to prefer shallow GP | **gap** | Notes block |
| Long Adam budget unexplained | **api** | Two-layer section |
| No GPy twin in this repo | **ok-short** | Native `deepgp` docs are the checklist |




## Wave 3 findings (2026-11-25)

These are mostly **GPc-led / lab-data** tutorials rather than line-by-line GPy twins. Spec sources: `pods` olympics path (GPy courses), CIP-0024 ExpQuad naming, CIP-0028/0032 weight-space.

### `olympic_marathon`

| Finding | Tag | Fix |
|---|---|---|
| Single intro blob; no section structure | **gap** | Full GP / predict contract / sparse sections |
| Year-scale lengthscale story buried | **gap** | Promoted into intro + sparse init note |
| CIP-0031 \(y_*\) vs \(f_*\) under-taught | **gap** | Dedicated section + dual `plot_1d` |
| Sparse as afterthought | **ok-short** | Tied back to `sparse_gp_regression` |

### `mlp_olympic`

| Finding | Tag | Fix |
|---|---|---|
| Williams / arcsin geometry not named as the teaching point | **gap** | Intro + side-by-side section |
| Year-scale `weight_variance` looks like a silent library default | **api** | Explicit “notebook recipe, not library default” |
| Link to finite MLP ridges | **ok-short** | Cross-link `weightspace_ridge_1d` |

### `expquad_regression`

| Finding | Tag | Fix |
|---|---|---|
| CIP-0024 path lesson present but no sectioning | **gap** | Fit + side-by-side sections |
| CIP-0027 noise vs GPy White-on-kernel | **api** | Called out in intro |
| Same SE family as RBF | **ok-short** | Emphasised in comparison section |

### `weightspace_ridge_1d` (no GPy twin)

| Finding | Tag | Fix |
|---|---|---|
| Strong intro; code cells unlabelled | **gap** | Points vs ridges / tied \(s\) / CIP-0032 / plot sections |
| Relation to infinite MLP prior | **ok-short** | Cross-link `mlp_olympic` |
| Conditioning cost of untied \(s_m\) | **api** | Stated in CIP-0032 section |


## How to run the next wave

```bash
# Outline markdown headings for a pair
python3 scripts/compare_gpc_gpy_notebooks.py \
  --gpy "GPy/basic_classification.ipynb" \
  --gpc "GPc/basic_classification.ipynb"
```

Then edit this file: set Status, append findings, open backlog items for **gap** rows you intend to fix.


## Program status

Waves 1–3 reviewed and narrative-patched (2026-11-25). Remaining optional polish: GPy Bias+Linear coreg walkthrough, Bernoulli density plot, `optimize_restarts` helper, MixedNoise multi-output.
