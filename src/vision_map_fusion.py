from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisualDetection:
    label: str
    confidence: float


@dataclass(frozen=True)
class SkillScore:
    skill: str
    target: str | None
    language_score: float
    affordance_score: float

    @property
    def saycan_score(self) -> float:
        return self.language_score * self.affordance_score


def detect_blocked_edges(detections: list[VisualDetection]) -> set[tuple[str, str]]:
    blocked: set[tuple[str, str]] = set()
    for detection in detections:
        if not detection.label.startswith("blocked_edge:") or detection.confidence < 0.7:
            continue
        edge = detection.label.split("blocked_edge:", 1)[1]
        source, target = edge.split("-")
        blocked.add(tuple(sorted((source, target))))
    return blocked


def edge_affordance(
    *,
    edge_mode: str,
    source: str,
    target: str,
    detections: list[VisualDetection],
) -> float:
    """Estimate whether a graph edge is executable from map + visual evidence."""

    if tuple(sorted((source, target))) in detect_blocked_edges(detections):
        return 0.02

    base = {"flat": 0.95, "elevator": 0.82, "stairs": 0.68}.get(edge_mode, 0.2)
    labels = " ".join(d.label.lower() for d in detections)

    if edge_mode == "stairs" and "cầu thang" in labels:
        base += 0.12
    if edge_mode == "elevator" and "thang máy" in labels:
        base += 0.12

    return min(base, 1.0)


def saycan_select(scores: list[SkillScore]) -> SkillScore:
    if not scores:
        raise ValueError("Cannot select from an empty skill list.")
    return max(scores, key=lambda score: score.saycan_score)

