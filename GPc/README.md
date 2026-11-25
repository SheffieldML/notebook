# GPc tutorial notebooks

Jupyter ports of the [GPy tutorial checklist](../GPy/index.ipynb) for the
[`gpc`](https://github.com/SheffieldML/GPc) Python façade.

| Role | Where |
|------|--------|
| Spec / checklist | [`GPy/`](../GPy/) in this repo |
| This tree | Public Jupyter / Colab share surface |
| Native C++ demos | [GPc `docs/tutorials`](https://github.com/SheffieldML/GPc/blob/main/docs/tutorials/README.md) |
| Package-local smoke notebooks | [GPc `python/examples`](https://github.com/SheffieldML/GPc/tree/main/python/examples) |

Design: [CIP-0007](../cip/cip0007.md).

## CI

[![GPc tutorials](https://github.com/SheffieldML/notebook/actions/workflows/gpc-tutorials.yml/badge.svg)](https://github.com/SheffieldML/notebook/actions/workflows/gpc-tutorials.yml)

```bash
# local smoke (needs gpc + nbclient + matplotlib)
bash scripts/run_gpc_tutorials.sh --output-dir executed-gpc-local
```

## Install

Notebooks try `import gpc` and install from PyPI (TestPyPI alpha fallback) if missing.
CI pins `gpc==0.1.0a11` from TestPyPI until the first PyPI release.

For a local editable build of GPc:

```bash
# from a GPc checkout with make.inc configured
cd python && make
pip install -e ".[plot,examples]"
export OPENBLAS_NUM_THREADS=1
```

Set `OPENBLAS_NUM_THREADS=1` in Colab / CI as well.

## Subset status

See [index.ipynb](./index.ipynb).

GPy ↔ GPc review notes: [COMPARISON.md](./COMPARISON.md) (rubric + Wave findings; `scripts/compare_gpc_gpy_notebooks.py`).

Executable tutorials (CIP-0007): `basic_gp`, `basic_kernels`, `sparse_gp_regression`, `sampling_hmc`,
`basic_classification`, `poisson_regression`, `coregionalization_toy`, `gplvm_oil100`,
`bgplvm_oil100`, `mrd_toy`, `deepgp_sinc`, `olympic_marathon`, `mlp_olympic`,
`expquad_regression`, `weightspace_ridge_1d`. Olympics / oil notebooks need `pods`
(installed in CI). DeepGP / Poisson / `k.K` need `gpc>=0.1.0a10`; HMC (`sampling_hmc`) needs `gpc>=0.1.0a11`.
