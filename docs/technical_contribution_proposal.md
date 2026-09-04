# Technical Contribution Proposal

## Working Title

StairNav-HM3D: Dialogue-Before-Move Command Grounding for Vietnamese Indoor Delivery Robots in Habitat-Matterport 3D

## Core Problem

Most LLM-robot demos translate a user command directly into movement. For a delivery robot in an indoor building, this is risky because the command may be incomplete and the robot should not move until it knows:

- what item must be delivered
- where the item should go
- whether the target is reachable in the current HM3D scene
- whether visual observations support the planned action

The project therefore focuses on **dialogue-before-move grounding** in HM3D rather than a toy graph environment.

## Main Contribution

The proposed contribution is a reproducible HM3D/Habitat-Sim pipeline for Vietnamese indoor delivery commands:

```text
Vietnamese command
  -> command model predicts missing slots and goal class
  -> dialogue policy asks clarification if needed
  -> Habitat-Sim observation provides RGB/depth/semantic state
  -> Habitat pathfinder checks reachability
  -> model and metrics are saved for later runs
```

## Why HM3D

HM3D provides realistic 3D scans of indoor spaces and integrates naturally with Habitat-Sim. This lets the project move beyond a hand-written graph and evaluate commands in real scanned environments.

## Current Training Model

The first trainable model is a lightweight reproducible baseline:

- input: Vietnamese command text
- features: TF-IDF character n-grams
- classifiers: Logistic Regression
- outputs:
  - whether clarification is needed
  - item class
  - goal description class

This baseline is intentionally simple so that stronger models can be compared fairly later.

## Next Model Upgrades

After the baseline runs:

1. replace TF-IDF with Vietnamese transformer embeddings
2. fine-tune PhoBERT or XLM-R for slot classification
3. use Qwen/Llama instruction models for structured JSON parsing
4. add faster-whisper for voice-to-text and measure ASR error propagation
5. use Habitat RGB/semantic frames for visual goal grounding

## Research Questions

1. Does dialogue-before-move reduce wrong navigation attempts on underspecified Vietnamese commands?
2. How well does a lightweight command model predict missing slots, item class, and goal class?
3. How does performance change when commands come from ASR instead of clean text?
4. Can HM3D semantic/RGB observations improve grounding compared with command text alone?
5. How much does Habitat geodesic reachability filtering reduce invalid movement decisions?

## Experiments

### E1: Clean Text Command Understanding

Train/test on HM3D-generated Vietnamese delivery episodes.

Metrics:

- clarification accuracy
- item accuracy
- goal class accuracy

### E2: Dialogue Before Move

Compare:

- direct move after command
- ask clarification before move

Metrics:

- false movement rate
- clarification success
- final executable command rate

### E3: Habitat Reachability

Use Habitat-Sim pathfinder to check whether sampled goal positions are reachable.

Metrics:

- reachable episode rate
- geodesic distance distribution
- failed episode sampling rate

### E4: Voice Input

Use faster-whisper for Vietnamese ASR.

Metrics:

- WER/CER
- command-model accuracy after ASR
- clarification accuracy after ASR

### E5: Visual Grounding Extension

Use Habitat RGB/depth/semantic observations for:

- room/area landmark detection
- semantic goal matching
- obstacle or navigability cues

Metrics:

- text-only vs text+vision goal grounding
- reachability-filtered success
- failure case categories

## Minimum Paper-Ready Target

For a serious submission, aim for:

- 10-20 HM3D scenes
- 1,000-3,000 Vietnamese delivery commands
- clean text and ASR-transcribed command variants
- baseline command model plus transformer/LLM comparison
- Habitat reachability evaluation
- released code, dataset generation scripts, trained baseline artifact, and metrics
