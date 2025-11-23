import re
import json

class IntakeAgent:
    """
    Intake Agent
    Cleans and structures incoming raw emails.
    """

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """
        Basic text cleanup: remove extra spaces, signatures, repeated symbols.
        """
        if not text:
            return ""

        # remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # you can extend this later with more cleanup rules
        return text

    def detect_thread(self, body: str) -> str:
        """
        Detect whether the email is a reply or a single message.
        Basic detection using common reply markers.
        """
        reply_indicators = [
            "Re:", "RE:", "Fw:", "FW:", "On", "wrote:", "Forwarded message"
        ]

        for marker in reply_indicators:
            if marker.lower() in body.lower():
                return "reply"

        return "single"

    def process_email(self, subject: str, body: str):
        """
        Main processing function.
        Takes raw email subject + body and returns clean JSON output.
        """

        clean_subject = self.clean_text(subject)
        clean_body = self.clean_text(body)

        thread_status = self.detect_thread(body)

        result = {
            "clean_subject": clean_subject,
            "clean_body": clean_body,
            "sender_if_available": None,
            "thread_status": thread_status,
            "length": len(clean_body),
            "notes": ""
        }

        return result


# quick local test (optional)
if __name__ == "__main__":
    agent = IntakeAgent()
    test_output = agent.process_email(
        subject="  RE: Issue with my invoice   ",
        body="Hi team,\nI received a wrong invoice.\nThanks\nJohn"
    )
    print(json.dumps(test_output, indent=2))
