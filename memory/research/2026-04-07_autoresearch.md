# Karpathy's AutoResearch Project

**Date:** 2026-04-07  
**Source:** Research compilation

---

## Overview

AutoResearch is Andrej Karpathy's experimental framework for **autonomous AI research agents** that optimize ML training code without human intervention. The project represents a shift from traditional human-in-the-loop research to AI-driven iterative experimentation.

> *"One day, frontier AI research used to be done by meat computers in between eating, sleeping, having other fun... That era is long gone."* — @karpathy, March 2026

---

## Key Statistics

| Metric | Value |
|--------|-------|
| GitHub Stars | ~68,000 |
| Forks | ~9,800 |
| Lines of Code | ~630 |
| Primary Language | Python (83.4%) |
| Created | March 2026 |

---

## Core Concept

The system runs **automated experiments on single-GPU nanochat training**:

1. **Fixed 5-minute time budget** per experiment
2. **AI agent modifies `train.py`** (architecture, hyperparameters, optimizer)
3. **Measures val_bpb** (validation bits per byte) — lower is better
4. **Keeps improvements, discards regressions** using git
5. **Runs autonomously** — ~12 experiments/hour, ~100 overnight

---

## Architecture

### Three Core Files

| File | Purpose | Edited By |
|------|---------|-----------|
| `prepare.py` | Data prep, tokenizer, evaluation harness | Fixed (read-only) |
| `train.py` | Model, optimizer, training loop | AI Agent |
| `program.md` | Agent instructions and research policy | Human |

### Key Design Principles

- **Single editable file** — keeps scope manageable
- **Fixed time budget** — makes experiments comparable regardless of hardware
- **Self-contained** — no distributed training, minimal dependencies
- **Git as memory** — branch stores experiment history and successful mutations

---

## The Experiment Loop

```
1. Create branch: autoresearch/<date>
2. Run baseline → record val_bpb
3. LOOP:
   - Modify train.py with new idea
   - git commit
   - Run: uv run train.py (5 min)
   - If val_bpb improved → keep commit
   - If worse or crash → git reset
```

---

## Results

According to reports, AutoResearch achieved:
- **11% performance improvement** over baseline
- **700+ automated experiments** in test runs
- Optimized nanochat training to GPT-2 benchmark faster

---

## Technical Details

### Model Configuration
- GPT-style transformer with RMSNorm, rotary embeddings
- Sliding/full attention windows (configurable via WINDOW_PATTERN)
- Muon + AdamW optimizer combination
- Configurable depth, aspect ratio, learning rates

### Key Hyperparameters (in train.py)
- `DEPTH` — controls model scale
- `ASPECT_RATIO` — width/depth ratio
- `WINDOW_PATTERN` — attention window pattern (e.g., "SSSL")
- `MATRIX_LR` / `EMBEDDING_LR` — learning rates
- `TOTAL_BATCH_SIZE` — batch size

### Evaluation Metric
- **val_bpb** (validation bits per byte)
- Vocab-size-independent
- Lower = better compression/prediction

---

## Significance

This project represents a paradigm shift:

| Traditional ML Research | AutoResearch |
|------------------------|--------------|
| Human changes code | Human writes agent policy |
| Human runs experiments | Agent runs experiments |
| Human decides next step | Agent decides next step |
| Research = model improvement | Research = process improvement |

**The real research object is not just the model, but the autonomous research process itself.**

---

## Resources

- **GitHub:** https://github.com/karpathy/autoresearch
- **Related:** https://github.com/karpathy/nanochat (base training harness)
- **Article:** "Inside Karpathy's autoresearch" by Balu Rama Chandra (Medium)

---

## Implications for AI Research

1. **Automated experimentation** at scale becomes feasible
2. **Human role shifts** from executor to policy designer
3. **Rapid iteration** — 100 experiments overnight vs. weeks manually
4. **Reproducibility** — every change is a git commit
5. **Platform for studying** how AI agents improve code over time
