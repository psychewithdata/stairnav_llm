# StairNav-HM3D

Vietnamese voice/text command understanding and dialogue-before-navigation for an indoor delivery robot in HM3D scenes using Habitat-Sim.

## Goal

Build a simulated delivery robot that:

1. receives a Vietnamese command such as "Đem tài liệu tới khu văn phòng ở cuối hành lang",
2. asks clarification questions before moving if the item or destination is missing,
3. grounds the command in an HM3D indoor scene,
4. uses Habitat-Sim observations and pathfinder for simulation,
5. trains/tests a reusable command-understanding model,
6. saves the trained model so it can be loaded again for later runs.

## Main Notebook

- `notebooks/StairNav_HM3D_Colab.ipynb`

This is now the only notebook workflow. The previous graph MVP notebook has been removed.

## Project Structure

```text
stairnav_llm/
  README.md
  HUONG_DAN_CHAY_COLAB.md
  requirements.txt

  notebooks/
    StairNav_HM3D_Colab.ipynb

  src/
    __init__.py
    command_model.py
    dialogue_policy.py
    hm3d_dataset_builder.py
    hm3d_habitat_adapter.py
    interactive_delivery_loop.py
    vision_map_fusion.py

  configs/
    hm3d_paths.example.json

  docs/
    hm3d_habitat_setup.md
    technical_contribution_proposal.md
```

## Pipeline

```text
HM3D scene
  -> Habitat-Sim RGB/depth/semantic observations
  -> sampled delivery episodes
  -> Vietnamese command dataset
  -> train/test command model
  -> save model to outputs/models/command_model.joblib
  -> load model for new command
  -> dialogue policy asks missing questions
  -> Habitat pathfinder checks navigability
```

## Training Artifact

The Colab notebook saves:

```text
outputs/models/command_model.joblib
outputs/models/command_model_metrics.json
data/stairnav_hm3d_minival_80.jsonl
```

It also includes a Google Drive cell to preserve these files after the Colab runtime disconnects.

## Current Model

The first training model is intentionally lightweight:

- TF-IDF character n-grams
- Logistic Regression classifiers
- labels: clarification needed, item class, goal description class

This gives a reproducible baseline before replacing it with PhoBERT, Qwen embeddings, or LoRA fine-tuning.

## Research Contribution Direction

The technical contribution should be:

> Dialogue-before-move command grounding for Vietnamese indoor delivery robots in HM3D, with Habitat-Sim visual observations and reusable trained command models.

Next upgrades:

- add faster-whisper for speech-to-text
- add visual room/landmark detection from Habitat RGB frames
- add semantic-map grounding from HM3D semantic observations
- compare text-only vs voice
- compare map/pathfinder oracle vs learned navigation policy
- integrate SayCan-style skill scoring using language confidence times visual/navigation affordance
