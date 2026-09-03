# HM3D + Habitat-Sim Setup

## Why Habitat-Sim

For this project, Habitat-Sim/Habitat-Lab should be the main simulator because HM3D is a native Habitat dataset and Habitat provides RGB, depth, semantic sensors, navmesh/pathfinder, and navigation tasks.

Use the graph notebook for fast ablations. Use Habitat-Sim for visual navigation and realistic indoor observations.

## Dataset Access

HM3D is an academic, non-commercial dataset released by Matterport and Facebook AI Research. You need Matterport access and an API token before downloading.

Recommended first split:

- `hm3d_minival_v0.2`, small enough for early testing
- then `hm3d_val_v0.2`
- only use `hm3d_train_v0.2` when the pipeline is stable

Expected Habitat-Lab structure:

```text
data/
  scene_datasets/
    hm3d/
      hm3d_annotated_basis.scene_dataset_config.json
      minival/
      val/
      train/
```

## Download Example

After generating a Matterport API token:

```bash
python -m habitat_sim.utils.datasets_download \
  --username "$MATTERPORT_TOKEN_ID" \
  --password "$MATTERPORT_TOKEN_SECRET" \
  --uids hm3d_minival_v0.2 \
  --data-path data/
```

Never commit token values to GitHub.

## How HM3D Fits This Project

HM3D scenes provide the robot's visual world:

- RGB camera images
- depth observations
- semantic observations when semantic annotations are available
- navigable mesh and geodesic distances

The project layer adds:

- Vietnamese voice/text commands
- delivery intent parsing
- dialogue before movement
- building-level topological abstraction
- SayCan-style language score times visual-map affordance score

## Training Data From HM3D

Use only a subset first:

1. Sample 10-20 HM3D minival scenes.
2. Sample navigable start and goal positions.
3. Extract RGB/depth snapshots near doors, rooms, stairs, corridors.
4. Create synthetic Vietnamese delivery commands around those goals.
5. Label whether the command is clear or requires clarification.

Minimum fields:

```json
{
  "scene_id": "...basis.glb",
  "start_position": [0.0, 0.0, 0.0],
  "goal_position": [1.0, 0.0, 2.0],
  "instruction_vi": "Đem tài liệu tới khu văn phòng ở cuối hành lang.",
  "needs_clarification": false,
  "preferred_vertical_mode": null
}
```

## Simulation Loop

```text
User voice command
  -> ASR text
  -> dialogue policy checks missing slots
  -> LLM produces delivery intent
  -> Habitat observation gives RGB/depth/semantic evidence
  -> vision module extracts landmarks/obstacles
  -> SayCan-style selector chooses next action
  -> Habitat-Sim executes action
```

## Immediate Limitation

HM3D contains realistic 3D scans, but it is not automatically a labeled "building delivery" dataset. The research value comes from creating the delivery-language layer and grounding it in HM3D visual/navigation data.
