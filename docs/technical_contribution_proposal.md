# Technical Contribution Proposal

## Working Title

StairNav-LLM: Vision- and Map-Grounded SayCan Planning for Vietnamese Voice-Guided Indoor Delivery Robots

## Core Problem

Most LLM-robot demos translate a natural-language command directly into a path or action sequence. This is weak for a delivery robot in a real building because the LLM does not know whether:

- a corridor is blocked
- a stair/elevator transition is physically feasible
- a room sign is actually visible
- the user command is underspecified
- the building map is stale or partially wrong

The project should therefore study **grounded decision-making**, not only language parsing.

## Main Technical Contribution

Combine three signals when selecting the robot's next skill:

```text
SayCan score = language score * affordance score
affordance score = f(building map, robot visual observation, robot state)
```

In the original SayCan setting, affordance estimates whether a low-level manipulation skill is likely to succeed. In this project, affordance estimates whether an indoor navigation/delivery skill is likely to succeed:

- move through a flat corridor
- take stairs
- take elevator
- enter a target room
- deliver item
- ask a clarification question

## Vision + Map Fusion

The robot camera can provide:

- OCR room-sign detection: "R503", "phòng 503", "lab robot"
- landmark detection: stairs, elevator, lobby, corridor
- obstacle detection: blocked corridor, broken elevator, crowded stair
- confidence scores for each detection

The building map provides:

- node type: room, corridor, stairs, elevator, lobby
- floor index
- edge mode: flat, stairs, elevator
- edge cost
- known room aliases and recipient locations

Fusion idea:

```text
edge_affordance = base_map_feasibility(edge)
                  * visual_support(edge_mode or landmark)
                  * obstacle_penalty(edge)
```

## Research Questions

1. Does vision-map fusion improve route success compared with map-only planning when the environment changes?
2. Does SayCan-style skill selection reduce invalid actions compared with direct LLM path generation?
3. Does clarification dialogue improve delivery success on underspecified Vietnamese voice commands?
4. How sensitive is the system to ASR errors in Vietnamese commands?

## Experiments

### E1: Map-only vs Vision+Map

Inject dynamic failures:

- blocked corridor
- elevator unavailable
- stair unavailable
- incorrect/missing room sign

Compare:

- shortest path on static map
- replanning with visual blocked-edge detection
- SayCan-lite with visual affordance

### E2: LLM-only vs Grounded Planner

Compare:

- LLM directly outputs full path
- LLM outputs structured intent, graph planner computes path
- LLM + SayCan-lite selects skills step by step

### E3: Clarification Dialogue

Commands:

- missing item: "Mang lên phòng 503 giúp tôi"
- missing destination: "Giao gói hàng cho giảng viên"
- ambiguous recipient: "Giao cho thầy ở lab"

Metrics:

- clarification accuracy
- false clarification rate
- final delivery success after user answer

### E4: Voice Robustness

Use faster-whisper or Whisper to transcribe Vietnamese audio commands.

Metrics:

- WER/CER
- intent accuracy after ASR
- destination accuracy after ASR
- delivery success after ASR

## Minimum Publishable System

For a serious paper target, build:

- 50-100 synthetic building graphs
- 1,000+ Vietnamese delivery commands
- dynamic obstacle/failure generator
- 4-6 baselines
- open-source code and reproducible configs
- error analysis with examples

## Simulator Path

### Current notebook

Graph simulator with simulated vision detections. Best for fast iteration and ablation.

### SayCan-style simulation

Use the notebook's `saycan_select_skill` and `run_saycan_episode` functions as the first SayCan abstraction.

### Physical/visual simulator extension

After the graph version is stable, connect observations from:

- Habitat-Sim for indoor navigation scenes
- PyBullet for simple robot/body visualization
- Genesis or ManiSkill for physics-based robot locomotion
- Isaac Sim only if hardware/setup is available

The graph/SayCan layer should remain independent from the simulator backend.
