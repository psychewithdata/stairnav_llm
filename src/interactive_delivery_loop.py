from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from dialogue_policy import (
    DeliveryIntent,
    apply_user_clarification,
    clarification_question,
)


class PlannerBackend(Protocol):
    def plan(self, intent: DeliveryIntent) -> list[str]:
        """Return a route/action list after dialogue slots are complete."""


@dataclass
class DialogueBeforeMoveAgent:
    """Ask all required questions before committing to movement."""

    planner: PlannerBackend

    def prepare_and_plan(self, initial_intent: DeliveryIntent, user_answers: list[str]) -> dict:
        intent = initial_intent
        dialogue = []

        for answer in ["", *user_answers]:
            question = clarification_question(intent)
            if question is None:
                break
            dialogue.append({"robot": question})
            if not answer:
                continue
            dialogue.append({"user": answer})
            intent = apply_user_clarification(intent, answer)

        final_question = clarification_question(intent)
        if final_question is not None:
            return {
                "status": "waiting_for_user",
                "dialogue": dialogue,
                "question": final_question,
                "intent": intent,
                "route": [],
            }

        route = self.planner.plan(intent)
        return {
            "status": "ready_to_move",
            "dialogue": dialogue,
            "question": None,
            "intent": intent,
            "route": route,
        }


class ToyPlanner:
    """Tiny planner for tests; replace with graph planner or Habitat policy."""

    def plan(self, intent: DeliveryIntent) -> list[str]:
        destination = intent.destination or intent.recipient or "UNKNOWN"
        return ["confirm_payload", f"navigate_to:{destination}", "deliver"]


if __name__ == "__main__":
    agent = DialogueBeforeMoveAgent(planner=ToyPlanner())
    result = agent.prepare_and_plan(
        DeliveryIntent(item=None, destination="R503"),
        user_answers=["tài liệu seminar"],
    )
    print(result)
