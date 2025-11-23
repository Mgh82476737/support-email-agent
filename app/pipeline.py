import json
import os
import sys

# Make sure project root is on sys.path so we can import 'agents'
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from agents.intake_agent import IntakeAgent
from agents.classification_agent import ClassificationAgent
from agents.reply_agent import ReplyAgent
from agents.supervisor_agent import SupervisorAgent
from agents.decision_agent import DecisionAgent


class EmailSupportPipeline:
    """
    Multi-Agent Email Support Pipeline
    Intake -> Classification -> Decision -> (Reply + Supervisor)
    """

    def __init__(self):
        self.intake = IntakeAgent()
        self.classifier = ClassificationAgent()
        self.decision = DecisionAgent()
        self.reply_agent = ReplyAgent()
        self.supervisor = SupervisorAgent()

    def run(self, subject: str, body: str, sender: str = "unknown") -> dict:
        """
        Run full pipeline on a single email.
        """

        # 1. Intake
        intake_output = self.intake.process_email(
            subject=subject,
            body=body
        )

        # 2. Classification
        classification_output = self.classifier.process(
            clean_email=intake_output,
            sender=sender
        )

        # 3. Decision (approve vs escalate_to_human)
        decision_input = {
            "id": intake_output.get("id"),
            "subject": subject,
            "body": body,
            "category": classification_output.get("category", "general_inquiry"),
            "urgency": classification_output.get("urgency", "normal"),
            "sentiment": classification_output.get("sentiment", "calm"),
            "needs_escalation": classification_output.get("needs_escalation", False),
        }

        decision_output = self.decision.decide(decision_input)
        final_action = decision_output.get("final_action", "escalate_to_human")

        # 4. Reply and Supervisor (only if approved)
        reply_output = None
        supervisor_output = None

        if final_action == "approve":
            reply_output = self.reply_agent.generate_reply(
                classification=classification_output,
                clean_email=intake_output
            )

            supervisor_output = self.supervisor.evaluate_reply(
                classification=classification_output,
                reply=reply_output
            )

        full_result = {
            "intake": intake_output,
            "classification": classification_output,
            "decision": decision_output,
            "reply": reply_output,
            "supervisor": supervisor_output
        }

        return full_result


if __name__ == "__main__":
    pipeline = EmailSupportPipeline()

    test_email_subject = "Refund request not processed"
    test_email_body = (
        "Hi team, this is the third time I'm asking about my refund. "
        "This is unacceptable. Please fix this now."
    )

    result = pipeline.run(
        subject=test_email_subject,
        body=test_email_body,
        sender="customer_123"
    )

    print(json.dumps(result, indent=2))
