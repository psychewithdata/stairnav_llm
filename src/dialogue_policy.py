from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class DeliveryIntent:
    item: str | None
    destination: str | None
    recipient: str | None = None
    preferred_vertical_mode: str | None = None


def missing_slots(intent: DeliveryIntent) -> list[str]:
    slots = []
    if not intent.item:
        slots.append("item")
    if not intent.destination and not intent.recipient:
        slots.append("destination_or_recipient")
    return slots


def clarification_question(intent: DeliveryIntent) -> str | None:
    slots = missing_slots(intent)
    if "destination_or_recipient" in slots:
        return "Bạn muốn robot giao tới phòng nào hoặc cho người nhận nào?"
    if "item" in slots:
        return "Robot cần mang món gì?"
    return None


def apply_user_clarification(intent: DeliveryIntent, answer: str) -> DeliveryIntent:
    """Simple placeholder update; replace with LLM slot filling later."""

    text = answer.lower()
    if not intent.destination:
        for token in ("101", "201", "202", "301", "302", "503", "504"):
            if token in text:
                return replace(intent, destination=f"R{token}")
    if not intent.item:
        return replace(intent, item=answer.strip())
    return intent
