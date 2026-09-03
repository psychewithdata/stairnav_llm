from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HabitatHM3DConfig:
    """Runtime paths for HM3D inside Habitat-Sim."""

    scene_id: str
    scene_dataset_config: str | None = None
    width: int = 640
    height: int = 480
    sensor_height: float = 1.25
    forward_step_size: float = 0.25
    turn_angle: float = 15.0


@dataclass
class HabitatObservation:
    """Thin wrapper around Habitat observations used by the planner."""

    rgb: Any | None
    depth: Any | None
    semantic: Any | None
    agent_state: Any


def _import_habitat_sim():
    try:
        import habitat_sim
        from habitat_sim.agent import ActionSpec, ActuationSpec
    except ImportError as exc:
        raise ImportError(
            "Habitat-Sim is not installed in this Python environment. "
            "Install it in a Linux/Colab/conda environment before running HM3D simulation."
        ) from exc
    return habitat_sim, ActionSpec, ActuationSpec


def make_habitat_sim_config(config: HabitatHM3DConfig):
    """Create a Habitat-Sim configuration for RGB-D-semantic navigation."""

    habitat_sim, ActionSpec, ActuationSpec = _import_habitat_sim()

    sim_cfg = habitat_sim.SimulatorConfiguration()
    sim_cfg.scene_id = str(Path(config.scene_id))
    if config.scene_dataset_config:
        sim_cfg.scene_dataset_config_file = str(Path(config.scene_dataset_config))
    sim_cfg.enable_physics = False

    rgb_sensor = habitat_sim.CameraSensorSpec()
    rgb_sensor.uuid = "color_sensor"
    rgb_sensor.sensor_type = habitat_sim.SensorType.COLOR
    rgb_sensor.resolution = [config.height, config.width]
    rgb_sensor.position = [0.0, config.sensor_height, 0.0]

    depth_sensor = habitat_sim.CameraSensorSpec()
    depth_sensor.uuid = "depth_sensor"
    depth_sensor.sensor_type = habitat_sim.SensorType.DEPTH
    depth_sensor.resolution = [config.height, config.width]
    depth_sensor.position = [0.0, config.sensor_height, 0.0]

    semantic_sensor = habitat_sim.CameraSensorSpec()
    semantic_sensor.uuid = "semantic_sensor"
    semantic_sensor.sensor_type = habitat_sim.SensorType.SEMANTIC
    semantic_sensor.resolution = [config.height, config.width]
    semantic_sensor.position = [0.0, config.sensor_height, 0.0]

    agent_cfg = habitat_sim.agent.AgentConfiguration()
    agent_cfg.sensor_specifications = [rgb_sensor, depth_sensor, semantic_sensor]
    agent_cfg.action_space = {
        "move_forward": ActionSpec(
            "move_forward", ActuationSpec(amount=config.forward_step_size)
        ),
        "turn_left": ActionSpec("turn_left", ActuationSpec(amount=config.turn_angle)),
        "turn_right": ActionSpec("turn_right", ActuationSpec(amount=config.turn_angle)),
        "look_up": ActionSpec("look_up", ActuationSpec(amount=10.0)),
        "look_down": ActionSpec("look_down", ActuationSpec(amount=10.0)),
    }

    return habitat_sim.Configuration(sim_cfg, [agent_cfg])


class HabitatHM3DSimulator:
    """Small adapter that exposes Habitat-Sim as a navigation backend."""

    def __init__(self, config: HabitatHM3DConfig):
        habitat_sim, _, _ = _import_habitat_sim()
        self._habitat_sim = habitat_sim
        self.config = config
        self.sim = habitat_sim.Simulator(make_habitat_sim_config(config))
        self.pathfinder = self.sim.pathfinder
        if not self.pathfinder.is_loaded:
            raise RuntimeError(
                "Habitat navmesh/pathfinder was not loaded. Check scene_id and dataset config paths."
            )

    def reset(self, position: Any | None = None, rotation: Any | None = None) -> HabitatObservation:
        agent = self.sim.initialize_agent(0)
        state = agent.get_state()
        if position is None:
            position = self.pathfinder.get_random_navigable_point()
        state.position = position
        if rotation is not None:
            state.rotation = rotation
        agent.set_state(state)
        return self.get_observation()

    def step(self, action: str) -> HabitatObservation:
        if action not in self.sim.get_agent(0).agent_config.action_space:
            raise ValueError(f"Unknown Habitat action: {action}")
        self.sim.step(action)
        return self.get_observation()

    def get_observation(self) -> HabitatObservation:
        observations = self.sim.get_sensor_observations()
        return HabitatObservation(
            rgb=observations.get("color_sensor"),
            depth=observations.get("depth_sensor"),
            semantic=observations.get("semantic_sensor"),
            agent_state=self.sim.get_agent(0).get_state(),
        )

    def geodesic_distance(self, start: Any, goal: Any) -> float:
        path = self._habitat_sim.ShortestPath()
        path.requested_start = start
        path.requested_end = goal
        found = self.pathfinder.find_path(path)
        return float(path.geodesic_distance) if found else float("inf")

    def close(self) -> None:
        self.sim.close()

