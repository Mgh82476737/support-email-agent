import json
from collections import Counter

# Load the batch results file
path = "data/batch_results.json"   # Update the path if your file is somewhere else

with open(path, "r", encoding="utf-8") as f:
    results = json.load(f)

print(f"Total emails processed: {len(results)}")

# Count final actions
actions = Counter(r.get("final_action", "None") for r in results)
print("\nFinal actions distribution:")
for action, count in actions.items():
    print(f"  {action}: {count}")

# Count sentiments
sentiments = Counter(r.get("sentiment", "None") for r in results)
print("\nSentiment distribution:")
for sentiment, count in sentiments.items():
    print(f"  {sentiment}: {count}")

# Find items with empty final_reply
empty_replies = [r for r in results if not r.get("final_reply")]
print(f"\nEmails with EMPTY final_reply: {len(empty_replies)}")

# Check for logical inconsistencies
weird_cases = [
    r for r in results
    if r.get("needs_escalation") is False and r.get("final_action") == "escalate_to_human"
]

print(f"\nWeird cases (needs_escalation is False but final_action is escalate_to_human): {len(weird_cases)}")

# Show sample weird cases
print("\nSample weird cases:")
for r in weird_cases[:3]:
    print(" id:", r.get("id"))
    print(" subject:", r.get("subject"))
    print(" needs_escalation:", r.get("needs_escalation"))
    print(" final_action:", r.get("final_action"))
    print(" final_reply:", repr(r.get("final_reply")))
    print("-" * 40)

# Show sample empty replies
print("\nSample emails with empty final_reply:")
for r in empty_replies[:3]:
    print(" id:", r.get("id"))
    print(" subject:", r.get("subject"))
    print(" final_action:", r.get("final_action"))
    print(" needs_escalation:", r.get("needs_escalation"))
    print(" sentiment:", r.get("sentiment"))
    print("-" * 40)
