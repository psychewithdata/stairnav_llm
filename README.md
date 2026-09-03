# StairNav-LLM

Voice-guided LLM planning for a simulated indoor delivery robot in multi-floor buildings, moving from a graph MVP to HM3D + Habitat-Sim visual simulation.

This project evolves the original ViVLN starter notebook from outdoor alley navigation to a stair-aware building delivery setting. The MVP uses a topological building graph; the main research simulator target is Habitat-Sim with HM3D scenes.

## Research Question

Can a language-guided robot delivery agent understand Vietnamese voice commands, ground them to a multi-floor building map, ask clarification questions when commands are underspecified, and plan valid stair/elevator-aware routes?

## MVP Pipeline

```text
Voice/text command
  -> Vietnamese command parser or local LLM planner
  -> structured delivery intent
  -> clarification dialogue if needed
  -> vision + building-map affordance fusion
  -> SayCan-style stair/elevator-aware skill selection
  -> graph simulator execution
  -> SR / SPL / clarification accuracy metrics
```

## Technical Contribution Direction

The strongest research contribution is not simply "LLM controls a robot". The project studies how an LLM planner can be grounded by both:

- a structured building map with rooms, floors, stairs, elevators, and weighted edges
- robot visual observations such as room signs, stair/elevator detections, and blocked corridors

The notebook includes a SayCan-style scoring prototype:

```text
score(skill) = language_score(skill | instruction) * affordance_score(skill | map, vision, robot_state)
```

This lets the agent prefer actions that are linguistically relevant and physically/topologically feasible.

## Main Notebook

- `notebooks/StairNav_LLM_delivery_starter.ipynb`
- Detailed Vietnamese setup guide: `HUONG_DAN_CHAY_COLAB.md`

Run this notebook from top to bottom on Colab. The default mode uses a rule-based baseline so the full pipeline runs quickly. After that, set:

```python
USE_LOCAL_LLM = True
```

to test an open-weight local LLM such as `Qwen/Qwen2.5-3B-Instruct`.

## HM3D + Habitat-Sim Track

Use HM3D as the visual indoor dataset and Habitat-Sim/Habitat-Lab as the accurate simulator stack.

New files:

- `src/hm3d_habitat_adapter.py`: Habitat-Sim RGB-D-semantic navigation adapter
- `src/hm3d_dataset_builder.py`: sample HM3D start/goal delivery episodes into JSONL
- `src/vision_map_fusion.py`: map + visual affordance scoring
- `src/dialogue_policy.py`: ask-before-moving dialogue policy
- `src/interactive_delivery_loop.py`: minimal dialogue-before-navigation loop
- `configs/hm3d_paths.example.json`: sample Habitat/HM3D path config
- `HUONG_DAN_CHAY_COLAB.md`: step-by-step Colab setup
- `docs/hm3d_habitat_setup.md`: HM3D/Habitat technical notes

Recommended development order:

1. Run the graph notebook and debug command/dialogue/planning.
2. Download HM3D minival after getting Matterport academic access.
3. Use `HabitatHM3DSimulator` to collect RGB/depth/semantic observations.
4. Use `sample_delivery_episodes(...)` to build a small HM3D JSONL training/evaluation subset.
5. Replace simulated detections with detector/OCR output from Habitat frames.
6. Run SayCan-style action selection inside Habitat-Sim.

## Baselines

- Rule-based parser + weighted shortest path
- Local LLM command parser + weighted shortest path
- Local LLM planner + path validator
- Clarification-aware planner for missing destination or missing item
- Map-only planner vs vision-map fusion planner
- SayCan-lite skill selection vs direct path generation

## Metrics

- Valid path rate
- Success Rate
- SPL
- Clarification accuracy
- Stair/elevator preference adherence
- Affordance calibration under blocked corridors/elevator failures
- Recovery rate after visual obstacle detection

## Next Steps

1. Expand the Vietnamese command dataset to 100-300 samples.
2. Compare Qwen 2.5/3B, Qwen 3/8B, Llama 3.1/8B, and API-based LLMs if available.
3. Add faster-whisper for Vietnamese voice-to-text.
4. Replace simulated detections with a real/simulated vision module: OCR room signs, obstacle detection, stair/elevator detection.
5. Connect the planner to HM3D scenes in Habitat-Sim.
6. Add Habitat-Lab evaluation episodes and train/evaluate policies on HM3D subsets.
