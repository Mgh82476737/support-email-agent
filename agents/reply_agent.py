import json

class ReplyAgent:
    """
    Reply Agent (Gemini-powered)
    Generates a professional customer support reply.
    """

    def __init__(self, llm=None):
        """
        llm: placeholder for Gemini model connection
        For now, we simulate response generation.
        """
        self.llm = llm

    def generate_safe_holding_message(self, sentiment: str):
        """
        Used when needs_escalation = True
        """
        if sentiment in ["angry", "frustrated"]:
            return (
                "I understand how frustrating this situation must be. "
                "I've escalated your case to a specialist who will review it as a priority."
            )
        return (
            "Thanks for your patience. "
            "I've forwarded your case to our specialist team for further review."
        )

    def generate_normal_reply(self, category: str):
        """
        Simple simulation for a normal reply (non-escalation)
        This will later be replaced by Gemini.
        """
        templates = {
            "billing": "I’ve checked your billing details and I can help clarify the recent changes.",
            "technical_issue": "Thanks for reporting the issue. Let's walk through a few troubleshooting steps.",
            "refund": "I can help you with your refund request and explain the next steps.",
            "complaint": "Thanks for sharing your feedback. I’m here to help resolve this.",
            "general_inquiry": "Here’s the information you requested."
        }
        return templates.get(category, "Thanks for contacting us.")

    def generate_reply(self, classification: dict, clean_email: dict):
        """
        Core logic:
        - If escalation is needed → safe holding message
        - If not → generate a helpful reply
        - Output JSON for supervisor
        """

        category = classification["category"]
        sentiment = classification["sentiment"]
        needs_escalation = classification["needs_escalation"]

        # 1. Escalation logic
        if needs_escalation:
            reply_text = self.generate_safe_holding_message(sentiment)
            requires_human = True
            tone = "empathetic" if sentiment in ["angry", "frustrated"] else "professional"
        else:
            reply_text = self.generate_normal_reply(category)
            requires_human = False
            # basic tone selection
            if sentiment in ["angry", "frustrated"]:
                tone = "empathetic"
            elif sentiment in ["happy"]:
                tone = "friendly"
            else:
                tone = "professional"

        result = {
            "reply_text": reply_text,
            "tone": tone,
            "requires_human_review": requires_human,
            "summary_for_supervisor": f"Generated reply for category '{category}' with tone '{tone}'."
        }

        return result


# quick test
if __name__ == "__main__":
    agent = ReplyAgent()
    classification = {
        "category": "billing",
        "sentiment": "frustrated",
        "needs_escalation": True
    }
    clean_email = {
        "clean_subject": "Issue",
        "clean_body": "I'm really frustrated with this issue."
    }

    output = agent.generate_reply(classification, clean_email)
    print(json.dumps(output, indent=2))
