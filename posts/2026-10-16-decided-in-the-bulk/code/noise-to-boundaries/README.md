# From Noise to Boundaries

Code and results for the blog essay *Decided in the Bulk, Written on the Boundary* and the working paper *From Noise to Boundaries: Area-Law Information Scaling Along the Diffusion Path* (Stéphane Cuenat, 2026).

**Question.** While a diffusion model turns pure noise into an image, does the information shared between an image patch and the rest of the image grow with the patch's border (area law) or with its size (volume law)?

**Method.** For Gaussian-mixture data, every stage of the diffusion path is known exactly, so mutual information can be computed with exact densities, no learned estimator. Each result is compared with a Gaussian control that has the same pixel correlations but no real structure.

**Main results.**
- Finished MNIST digits follow an area law (scaling exponent β ≈ 1.07).
- In the noisy phase, real structure adds up to 2.4× the control's information, scaling closer to a volume law; it moves toward the boundary as details form.
- The change is smooth, not a sharp transition (3 seeds, 11 noise levels).
- Region information can be recovered from denoising errors alone (I-MMSE relation), validated against the exact values. This route applies to trained diffusion models.

Everything runs on a laptop CPU. Total compute for all results: about 30 minutes on 2 cores.

## Setup

```bash
pip install -r requirements.txt
```

MNIST is not included. Download the single-file version (about 11 MB) into `data/`:

```bash
mkdir -p data
curl -L -o data/mnist.npz https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz
```

(or set `MNIST_PATH=/path/to/mnist.npz`). The 8×8 digits experiment uses the copy bundled with scikit-learn.

## Run

Run scripts from inside `src/`; each writes its JSON results and figures to the current folder.

| Step | Script | What it does | Time (2 CPU cores) |
|---|---|---|---|
| 1 | `area_law_pilot.py` | Estimator validation + Gaussian baseline | ~15 s |
| 2 | `mixture_pilot.py` → `plot_mixture.py` | Synthetic 16-class data vs control | ~20 s |
| 3 | `digits_fit.py` → `digits_mi.py` → `plot_digits.py` | 8×8 digits (scikit-learn) | ~30 s |
| 4 | `mnist_model.py` | Fit MNIST mixture; held-out likelihood check | ~40 s |
| 5 | `mnist_mi.py` → `plot_mnist.py` | MNIST along the full diffusion path | ~5 min |
| 6 | `mnist_fine.py 0`, `1`, `2` → `plot_fine.py` | Fine noise grid, 3 seeds | ~5 min (parallel) |
| 7 | `immse_validation.py 0 2`, `1 2` → `immse_compare.py` | Information from denoising errors vs exact | ~7 min (parallel) |

`run_all.sh` runs everything in order.

## Layout

```
src/       all scripts (mnist_model.py holds the shared model code)
results/   JSON outputs used in the essay and paper
figures/   all figures
paper/     working paper (LaTeX source + PDF)
data/      put mnist.npz here
```

## Key idea behind step 7

By the I-MMSE relation (Guo, Shamai, Verdú 2005), for a Gaussian noise channel

    I(Y_A; Y_B)(snr) = 1/2 ∫_0^snr [ mmse_A + mmse_B − mmse_full ] dγ

where `mmse_A` is the error of denoising region A from noisy A alone and `mmse_full` the error with the whole image visible. In words: *the information a region shares with the rest equals how much seeing the rest helps denoise it, accumulated over noise levels.* Only denoisers are needed, so the same measurement can be applied to trained diffusion models with masked context.

## Limitations

The model is a 40-component Gaussian mixture, not a neural network; images are small (28×28), so region sizes span 2–12 pixels; the holography connection is an analogy. See the paper for details.

## License

MIT. Developed with the help of Claude (Anthropic) as a coding and review partner.
