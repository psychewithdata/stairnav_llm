from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hm3d_habitat_adapter import HabitatHM3DSimulator


@dataclass(frozen=True)
class HM3DDeliveryEpisode:
    episode_id: str
    scene_id: str
    start_position: list[float]
    goal_position: list[float]
    geodesic_distance: float
    instruction_vi: str
    item: str
    goal_description: str
    needs_clarification: bool
    preferred_vertical_mode: str | None = None


ITEMS = [
    "tài liệu",
    "hộp thuốc",
    "laptop",
    "linh kiện robot",
    "biên bản họp",
    "gói hàng nhỏ",
]

GOAL_DESCRIPTIONS = [
    "khu văn phòng ở cuối hành lang",
    "cửa phòng phía trước",
    "khu sinh hoạt chung",
    "phòng gần cầu thang",
    "vị trí được đánh dấu trong bản đồ",
]

CLARIFICATION_TEMPLATES = [
    "Giao gói hàng này giúp tôi.",
    "Mang món này tới cho giảng viên.",
    "Đem lên giúp tôi.",
    "Robot giao đồ tới phòng đó nhé.",
]


def _vec3_to_list(value: Any) -> list[float]:
    return [float(value[0]), float(value[1]), float(value[2])]


def make_instruction(item: str, goal_description: str, rng: random.Random) -> str:
    templates = [
        "Đem {item} tới {goal}.",
        "Giao {item} giúp tôi tới {goal}.",
        "Mang {item} đến {goal}, nếu đường bị chặn thì chọn lối khác.",
        "Robot hãy giao {item} tới {goal}.",
    ]
    return rng.choice(templates).format(item=item, goal=goal_description)


def make_clarification_instruction(rng: random.Random) -> str:
    return rng.choice(CLARIFICATION_TEMPLATES)


def sample_delivery_episodes(
    sim: HabitatHM3DSimulator,
    *,
    scene_id: str,
    count: int,
    seed: int = 7,
    min_distance: float = 2.0,
    clarification_ratio: float = 0.2,
    max_attempts_per_episode: int = 100,
) -> list[HM3DDeliveryEpisode]:
    """Sample navigable start/goal pairs from an HM3D scene."""

    rng = random.Random(seed)
    episodes: list[HM3DDeliveryEpisode] = []

    for episode_idx in range(count):
        for _ in range(max_attempts_per_episode):
            start = sim.pathfinder.get_random_navigable_point()
            goal = sim.pathfinder.get_random_navigable_point()
            distance = sim.geodesic_distance(start, goal)
            if distance >= min_distance and distance < float("inf"):
                item = rng.choice(ITEMS)
                goal_description = rng.choice(GOAL_DESCRIPTIONS)
                needs_clarification = rng.random() < clarification_ratio
                episodes.append(
                    HM3DDeliveryEpisode(
                        episode_id=f"{Path(scene_id).stem}_{episode_idx:05d}",
                        scene_id=scene_id,
                        start_position=_vec3_to_list(start),
                        goal_position=_vec3_to_list(goal),
                        geodesic_distance=float(distance),
                        instruction_vi=(
                            make_clarification_instruction(rng)
                            if needs_clarification
                            else make_instruction(item, goal_description, rng)
                        ),
                        item="" if needs_clarification else item,
                        goal_description=goal_description,
                        needs_clarification=needs_clarification,
                    )
                )
                break

    return episodes


def save_jsonl(episodes: list[HM3DDeliveryEpisode], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for episode in episodes:
            f.write(json.dumps(asdict(episode), ensure_ascii=False) + "\n")


def load_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
