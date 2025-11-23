import json

class SupervisorAgent:
    """
    Supervisor Agent
    Evaluates reply quality and decides:
    - approve
    - rewrite
    - escalate_to_human
    """

    def __init__(self):
        pass

    def evaluate_reply(self, classification: dict, reply: dict):
        """
        Main evaluation logic.
        Determines if the reply from ReplyAgent is:
        - appropriate
        - safe
        - correct tone
        - correct escalation behavior
        """

        category = classification["category"]
        urgency = classification["urgency"]
        sentiment = classification["sentiment"]
        needs_escalation = classification["needs_escalation"]

        reply_text = reply["reply_text"]
        tone = reply["tone"]
        requires_human = reply["requires_human_review"]

        # ------------------------------
        # 1. Escalation Validation
        # ------------------------------
        if needs_escalation:
            # Reply MUST be a safe holding message
            if "I’ve checked" in reply_text or "I can help you" in reply_text:
                return self._reject(
                    reason="Reply gives full solution when escalation was required.",
                    needs_human=True
                )

            # tone must be empathetic or professional
            if sentiment in ["angry", "frustrated"] and tone != "empathetic":
                return self._reject(
                    reason="Tone must be empathetic for angry/frustrated customers.",
                    needs_human=True
                )

            # If all is good
            return self._approve(reply_text, sentiment)

        # ------------------------------
        # 2. Tone Validation
        # ------------------------------
        if sentiment in ["angry", "frustrated"] and tone not in ["empathetic"]:
            return self._reject(
                reason="Tone mismatch: angry/frustrated customers need empathy.",
                needs_human=True
            )

        if sentiment == "happy" and tone != "friendly":
            return self._reject(
                reason="Tone mismatch: happy customers should receive friendly tone.",
                needs_human=False
            )

        # ------------------------------
        # 3. Length Validation
        # ------------------------------
        sentence_count = len(reply_text.split("."))
        if sentence_count < 2 or sentence_count > 6:
            return self._reject(
                reason="Reply length is outside acceptable range (3-5 sentences).",
                needs_human=False
            )

        # ------------------------------
        # 4. Safety / Accuracy Checks
        # ------------------------------
        forbidden = [
            "guarantee",
            "legal responsibility",
            "we promise",
            "AI",
            "as an AI"
        ]

        for word in forbidden:
            if word.lower() in reply_text.lower():
                return self._reject(
                    reason=f"Unsafe or inappropriate phrase detected: '{word}'",
                    needs_human=True
                )

        # ------------------------------
        # 5. If everything is OK → APPROVE
        # ------------------------------
        return self._approve(reply_text, sentiment)

    # Helper functions
    def _approve(self, final_reply, sentiment):
        return {
            "action": "approve",
            "final_reply": final_reply,
            "reason": "Reply approved.",
            "needs_human": False,
            "memory_update": {
                "quality_score": 5,
                "last_interaction_sentiment": sentiment
            }
        }

    def _reject(self, reason, needs_human):
        return {
            "action": "rewrite" if not needs_human else "escalate_to_human",
            "final_reply": "",
            "reason": reason,
            "needs_human": needs_human,
            "memory_update": {
                "quality_score": 2,
                "last_interaction_sentiment": None
            }
        }


# quick test
if __name__ == "__main__":
    supervisor = SupervisorAgent()
    classification = {
        "category": "billing",
        "urgency": "high",
        "sentiment": "angry",
        "needs_escalation": True
    }
    reply = {
        "reply_text": "I’ve checked your billing information and can help.",
        "tone": "professional",
        "requires_human_review": False
    }

    output = supervisor.evaluate_reply(classification, reply)
    print(json.dumps(output, indent=2))
