# HM3D + Habitat-Sim Technical Notes

## Dataset

HM3D is the Habitat-Matterport 3D Research Dataset. It provides realistic indoor 3D scenes for academic, non-commercial research.

Use this order:

```text
hm3d_minival_v0.2 -> hm3d_val_v0.2 -> hm3d_train_v0.2
```

Start with `hm3d_minival_v0.2`.

## Expected Folder Layout

```text
data/
  scene_datasets/
    hm3d/
      hm3d_annotated_basis.scene_dataset_config.json
      minival/
        008xx-.../
          *.basis.glb
          *.basis.navmesh
          *.semantic.glb
          *.semantic.txt
```

## Download Command

```bash
python -m habitat_sim.utils.datasets_download \
  --username "$MATTERPORT_TOKEN_ID" \
  --password "$MATTERPORT_TOKEN_SECRET" \
  --uids hm3d_minival_v0.2 \
  --data-path data/
```

## Simulator Adapter

The file `src/hm3d_habitat_adapter.py` wraps Habitat-Sim with:

- RGB camera
- depth camera
- semantic camera
- `reset()`
- `step(action)`
- `geodesic_distance(start, goal)`

The first navigation evaluation uses Habitat pathfinder as an oracle. Later work can replace this with a learned Habitat-Lab navigation policy.

## Dataset Builder

The file `src/hm3d_dataset_builder.py` samples:

- random navigable start positions
- random navigable goal positions
- geodesic distance
- Vietnamese delivery instructions
- clarification-needed examples

It saves JSONL episodes that can be used for training and testing command-understanding models.

## Model Training

The file `src/command_model.py` trains a baseline command model:

```text
Vietnamese instruction -> clarification label / item label / goal label
```

Saved artifacts:

```text
outputs/models/command_model.joblib
outputs/models/command_model_metrics.json
```

## Dialogue Before Movement

The files `src/dialogue_policy.py` and `src/interactive_delivery_loop.py` implement the rule:

```text
If command is missing item or destination, ask first.
Only move after required slots are filled.
```

This is the current human-robot interaction contribution.
