from typing import Dict


class DecisionAgent:
    """
    Rule-based decision agent.

    It decides whether an email should be:
      - handled by the auto reply agent ("approve"), or
      - escalated to a human agent ("escalate_to_human").
    """

    HIGH_RISK_CATEGORIES = {"complaint", "cancellation", "legal", "regulatory"}

    def __init__(self):
        pass

    def decide(self, decision_input: Dict) -> Dict:
        """
        decision_input should contain:
          - id: str
          - subject: str
          - body: str
          - category: str
          - urgency: str
          - sentiment: str
          - needs_escalation: bool

        Returns:
          {
            "final_action": "approve" | "escalate_to_human",
            "reason": str,
            "confidence": "high" | "medium" | "low"
          }
        """

        category = (decision_input.get("category") or "general_inquiry").lower()
        sentiment = (decision_input.get("sentiment") or "calm").lower()
        needs_escalation = bool(decision_input.get("needs_escalation", False))
        urgency = (decision_input.get("urgency") or "normal").lower()

        reasons = []

        # Rule 1: explicit escalation signal
        if needs_escalation:
            reasons.append("Escalation flag from escalation/supervisor logic is true.")
            final_action = "escalate_to_human"
            confidence = "high"
        # Rule 2: strong negative sentiment
        elif sentiment in {"angry", "frustrated"}:
            reasons.append(f"Customer sentiment is '{sentiment}', which is high-risk.")
            final_action = "escalate_to_human"
            confidence = "high"
        # Rule 3: high-risk categories
        elif category in self.HIGH_RISK_CATEGORIES:
            reasons.append(f"Email category '{category}' is considered high-risk.")
            final_action = "escalate_to_human"
            confidence = "medium"
        else:
            # Default: safe to auto reply
            reasons.append(
                "Calm or low-risk email with no escalation flag. "
                "It is safe to handle this with the auto reply agent."
            )
            final_action = "approve"
            confidence = "high" if sentiment == "calm" else "medium"

        reason_text = " ".join(reasons)

        return {
            "final_action": final_action,
            "reason": reason_text,
            "confidence": confidence,
        }
