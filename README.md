# AQUA-Bench: Beyond Finding Answers to Knowing When There Are None in Audio Question Answering

[![arXiv](https://img.shields.io/badge/arXiv-2601.12248-b31b1b.svg)](https://arxiv.org/abs/2601.12248)
[![ICASSP 2026](https://img.shields.io/badge/ICASSP%202026-Oral-5f7257.svg)](https://ieeexplore.ieee.org/document/11460647/)
[![Demo](https://img.shields.io/badge/Demo-Page-6f8265.svg)](https://kuan2jiu99.github.io/aqua-bench/)

🎉 **Accepted to ICASSP 2026 (Oral Presentation)**

**Authors:** [Chun-Yi Kuan](https://kuan2jiu99.github.io/), [Hung-yi Lee](https://speech.ee.ntu.edu.tw/~hylee/index.php) · National Taiwan University

> **TL;DR** — Most audio QA benchmarks assume every question has an answer. AQUA-Bench asks the opposite: *can a model recognize when a question is unanswerable and abstain, instead of forcing a guess?* It turns out current audio-aware LLMs often can't.

🔗 **[Paper](https://arxiv.org/abs/2601.12248)** · **[Interactive Demo](https://kuan2jiu99.github.io/aqua-bench/)** · **[Dataset](evaluation-data/)**

---

## Overview

Existing audio QA benchmarks assume every question has a correct answer. But real-world queries can be
misleading, ill-posed, or irrelevant to the audio. **AQUA-Bench** tests whether audio-aware large language
models (ALLMs) can recognize these cases and abstain, rather than always forcing an answer.

Every audio clip is paired with a standard **Solvable** question plus three unanswerable settings:

| Setting | Name | What is wrong | Correct response |
|---------|------|---------------|------------------|
| **AAD**  | Absent Answer Detection            | The correct option is deliberately **removed** from the choices. | *None of the above* |
| **IASD** | Incompatible Answer Set Detection  | The options are from a **categorically mismatched** set (e.g. drinks for an instrument question). | *None of the above* |
| **IAQD** | Incompatible Audio–Question Detection | The **question itself** is not grounded in the audio (e.g. "which city is the instrument in?"). | *Unanswerable* |

**Keywords:** unanswerable questions · audio question answering · audio-aware large language models

![overview](figures/overview.png)

### Key Findings

- **Large solvable-vs-unanswerable gap.** ALLMs do well on standard answerable questions but drop sharply on unanswerable ones — a critical reliability blind spot.
- **Forced-choice bias.** Models tend to always pick an option even when none is valid, instead of abstaining.
- **Chain-of-Thought helps.** CoT prompting unlocks a latent ability to detect unanswerability; some models recover from near-zero to substantial accuracy when asked to reason step by step.
- **Phrasing matters.** Rewording the abstain option (e.g. *"None of the above"* vs. *"All answers are incorrect"*) and adding explicit guidance both shift model behavior — see the ablation variants below.

---

## Repository Structure

```
aqua-bench/
├── index.html            # Source of the interactive demo page
├── evaluation.py         # Dual-accuracy evaluation script
├── evaluation-data/      # Benchmark JSON files (main + ablation variants)
├── assets/               # Audio clips & images used by the demo
└── figures/              # Paper figures
```

---

## Dataset

The benchmark lives in [`evaluation-data/`](evaluation-data/), one JSON file per audio domain.

### File naming

```
AQUA-Bench-{domain}{variant}.json
```

- `domain` ∈ { `Animal-Sounds-Track`, `Music-Instruments-Sounds-Track`, `Vocal-Sounds-Track` }
- `variant` ∈ { *(empty = main benchmark)*, `-Option-Design1`, `-Option-Design2`, `-Uncertainty` }

Each file is a JSON list. Entries are ordered in **groups of four** — `Solvable`, `AAD`, `IASD`, `IAQD` for the same
audio clip — which the evaluation script relies on (see [Evaluation](#evaluation)).

### Entry schema

| Key | Description |
|-----|-------------|
| `type` | One of `Solvable`, `AAD`, `IASD`, or `IAQD`. |
| `question` | The full question prompt (stem + options + guidance instruction). |
| `options` | List of answer choices, mapped to letters `(a)`, `(b)`, … in order. |
| `answer` | The ground-truth answer text (matches one entry in `options`). |
| `audio_filename` | Path relative to the original source dataset — use it to resolve the audio file (see [Step 1](#1-download-source-datasets)). |

Domain files also carry helper metadata (e.g. `audio_id`, `audio_verb`, `audio_animal`) used during construction;
they are not required for evaluation.

### Ablation variants

Three variants modify how the unanswerable option is phrased:

| Variant | AAD / IASD option | IAQD option |
|---------|-------------------|-------------|
| **Main** | *None of the above* | *Unanswerable* |
| **`-Option-Design1`** | *No correct answer* | *Cannot be determined from the given information* |
| **`-Option-Design2`** | *All answers are incorrect* | *Insufficient information to answer* |
| **`-Uncertainty`** | adds hint: *"Select 'None of the above' if you believe none of the listed answers is right."* | adds hint: *"Pick 'Unanswerable' when the audio lacks the details needed to decide."* |

Results for all variants are illustrated on the **[demo page](https://kuan2jiu99.github.io/aqua-bench/)**.

---

## Evaluation

### 1. Download source datasets

AQUA-Bench ships the questions and metadata, not the raw audio. Download the source audio from:

| Domain | Source dataset | Link |
|--------|----------------|------|
| Animal Sounds | ESC-50 | [GitHub](https://github.com/karolpiczak/ESC-50) |
| Musical Instruments | Music Instrument Sounds | [Kaggle](https://www.kaggle.com/datasets/abdulvahap/music-instrunment-sounds-for-classification) |
| Vocal Sounds | VocalSound | [GitHub](https://github.com/YuanGongND/vocalsound) |

Use `audio_filename` to map each entry to its audio file in the downloaded dataset.

### 2. Run inference

Prompt your model with each entry's `question` (plus the resolved audio) and store the model's reply under a new
`response` key, **keeping the original entry order**. The result is the same JSON list with one extra key per entry:

```json
{ "type": "AAD", "question": "...", "options": ["..."], "answer": "...",
  "audio_filename": "...", "response": "(e) None of the above" }
```

### 3. Run evaluation

```bash
python evaluation.py --results_path YOUR_RESULTS.json
```

The script reports **dual accuracy**:

- **Standard accuracy** — per-type accuracy (`Solvable`, `AAD`, `IASD`, `IAQD`).
- **Conditional accuracy** — accuracy on the unanswerable types *only for clips whose Solvable question was answered
  correctly*. This isolates abstention ability from basic audio recognition: a model is credited for detecting
  unanswerability only when it actually understood the audio.

Answer extraction is option-letter based and tolerant of surrounding text, so free-form responses
(e.g. *"… therefore the answer is (e)"*) are scored correctly.

---

## Citation

```bibtex
@inproceedings{kuan2026aqua,
  title     = {AQUA-Bench: Beyond Finding Answers to Knowing When There Are None in Audio Question Answering},
  author    = {Kuan, Chun-Yi and Lee, Hung-yi},
  booktitle = {ICASSP 2026 - 2026 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages     = {16262--16266},
  year      = {2026},
  doi       = {10.1109/ICASSP55912.2026.11460647}
}
```

---

## References

- [1] K. J. Piczak. *ESC: Dataset for Environmental Sound Classification.* ACM Multimedia, 2015.
- [2] Abdulvahap. *Music Instrument Sounds for Classification.* Kaggle.
- [3] Y. Gong, J. Yu, J. Glass. *VocalSound: A Dataset for Improving Human Vocal Sounds Recognition.* ICASSP, 2022.
- [4] S. Sakshi et al. *MMAU: A Massive Multi-Task Audio Understanding and Reasoning Benchmark.* ICLR, 2024.
