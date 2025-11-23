import json
from pipeline import EmailSupportPipeline



if __name__ == "__main__":
    pipeline = EmailSupportPipeline()

    test_email_subject = "Issue with my latest invoice"
    test_email_body = (
        "Hi, I noticed an extra charge on my latest bill. "
        "This is the third time I am asking about this. "
        "Please fix this as soon as possible."
    )

    result = pipeline.run(
        subject=test_email_subject,
        body=test_email_body,
        sender="customer_123"
    )

    # Pretty print pipeline stages
    print("=== INTAKE ===")
    print(json.dumps(result.get("intake"), indent=2))

    print("\n=== CLASSIFICATION ===")
    print(json.dumps(result.get("classification"), indent=2))

    print("\n=== DECISION ===")
    print(json.dumps(result.get("decision"), indent=2))

    print("\n=== REPLY (FROM REPLY AGENT) ===")
    print(json.dumps(result.get("reply"), indent=2))

    print("\n=== SUPERVISOR DECISION ===")
    print(json.dumps(result.get("supervisor"), indent=2))
