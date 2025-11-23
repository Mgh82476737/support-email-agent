import json
import re

class ClassificationAgent:
    """
    Classification Agent
    Reads cleaned email and assigns:
    - category
    - urgency
    - sentiment
    - thread_status
    - needs_escalation
    Also updates simple memory values.
    """

    POSSIBLE_CATEGORIES = [
        "billing", "technical_issue", "refund", "complaint", "general_inquiry"
    ]

    SENTIMENT_KEYWORDS = {
        "angry": ["unacceptable", "angry", "furious", "not acceptable", "fix this now"],
        "frustrated": ["frustrating", "frustrated", "this is really", "not working"],
        "confused": ["don't understand", "what does this mean", "confusing"],
        "calm": ["hi", "hello", "kind regards", "thanks"],
        "neutral": [],
        "happy": ["thank you so much", "great", "happy", "appreciate"]
    }

    ESCALATION_TRIGGERS = ["unacceptable", "angry", "furious", "fix this now", "third time", "fourth email"]

    def __init__(self, memory_db=None):
        """
        memory_db: dictionary or custom memory system
        """
        self.memory_db = memory_db if memory_db is not None else {}

    def detect_category(self, text: str) -> str:
        text = text.lower()

        if "invoice" in text or "subscription" in text or "charge" in text:
            return "billing"
        if "refund" in text or "return" in text:
            return "refund"
        if "not working" in text or "error" in text or "crash" in text:
            return "technical_issue"
        if "disappointed" in text or "complaint" in text or "poor service" in text:
            return "complaint"
        if "how do i" in text or "can i" in text or "question" in text:
            return "general_inquiry"

        return "general_inquiry"

    def detect_sentiment(self, text: str) -> str:
        text = text.lower()

        for sentiment, keywords in self.SENTIMENT_KEYWORDS.items():
            for word in keywords:
                if word in text:
                    return sentiment

        return "neutral"

    def detect_urgency(self, text: str) -> str:
        text = text.lower()

        if "as soon as possible" in text or "urgent" in text or "fix today" in text:
            return "high"
        if "not urgent" in text or "whenever you can" in text:
            return "low"

        return "normal"

    def check_escalation(self, text: str, sentiment: str) -> bool:
        text_low = text.lower()

        if sentiment in ["angry", "frustrated"]:
            return True

        for keyword in self.ESCALATION_TRIGGERS:
            if keyword in text_low:
                return True

        return False

    def update_memory(self, sender: str, category: str, sentiment: str):
        if sender not in self.memory_db:
            self.memory_db[sender] = {
                "message_count": 0,
                "last_category": None,
                "last_sentiment": None
            }

        self.memory_db[sender]["message_count"] += 1
        self.memory_db[sender]["last_category"] = category
        self.memory_db[sender]["last_sentiment"] = sentiment

        return self.memory_db[sender]

    def process(self, clean_email: dict, sender: str = "unknown"):
        """
        clean_email is dictionary from IntakeAgent
        """

        text = clean_email["clean_body"]
        thread = clean_email["thread_status"]

        category = self.detect_category(text)
        sentiment = self.detect_sentiment(text)
        urgency = self.detect_urgency(text)
        needs_escalation = self.check_escalation(text, sentiment)

        memory_update = self.update_memory(sender, category, sentiment)

        result = {
            "category": category,
            "urgency": urgency,
            "sentiment": sentiment,
            "thread_status": thread,
            "needs_escalation": needs_escalation,
            "memory_update": memory_update,
            "notes": ""
        }

        return result


# quick test
if __name__ == "__main__":
    agent = ClassificationAgent()
    test_output = agent.process(
        clean_email={
            "clean_subject": "Issue with invoice",
            "clean_body": "Hi, this is the third time I'm asking. This is unacceptable. Fix this now.",
            "thread_status": "reply"
        }
    )
    print(json.dumps(test_output, indent=2))
