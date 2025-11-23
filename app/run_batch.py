import csv
import json
import os
import sys

# Make sure project root is on sys.path so we can import 'pipeline'
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from pipeline import EmailSupportPipeline


def load_emails_from_csv(csv_path: str):
    """
    Load emails from a CSV file.

    Automatically handles non-UTF8 encodings like ANSI/Windows-1252.
    """
    emails = []

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input CSV file not found: {csv_path}")

    # Try UTF-8 first, fall back to latin1
    try:
        f = open(csv_path, "r", encoding="utf-8")
        reader = csv.DictReader(f)
        reader.fieldnames  # force header read
    except UnicodeDecodeError:
        f = open(csv_path, "r", encoding="latin1", errors="ignore")
        reader = csv.DictReader(f)

    with f:
        has_id = "id" in reader.fieldnames
        has_subject = "subject" in reader.fieldnames
        has_body = "body" in reader.fieldnames

        if not has_subject or not has_body:
            raise ValueError("CSV must contain at least 'subject' and 'body' columns.")

        for i, row in enumerate(reader, start=1):
            email_id = row["id"] if has_id else str(i)
            emails.append(
                {
                    "id": email_id,
                    "subject": row["subject"],
                    "body": row["body"],
                }
            )

    return emails


def main():
    # Paths
    data_dir = os.path.join(PROJECT_ROOT, "data")
    input_csv = os.path.join(data_dir, "emails.csv")
    output_json = os.path.join(data_dir, "batch_results.json")

    print(f"Looking for file: {os.path.relpath(input_csv, PROJECT_ROOT)}")

    # Load emails
    emails = load_emails_from_csv(input_csv)
    print(f"Loaded {len(emails)} emails from CSV")

    # Initialize pipeline
    pipeline = EmailSupportPipeline()

    results = []

    for email in emails:
        subject = email["subject"]
        body = email["body"]
        sender = email.get("sender", "unknown")

        print(f"Processing email id={email['id']} subject={subject!r}")
        pipeline_output = pipeline.run(
            subject=subject,
            body=body,
            sender=sender
        )

        intake = pipeline_output.get("intake") or {}
        classification = pipeline_output.get("classification") or {}
        decision = pipeline_output.get("decision") or {}
        reply = pipeline_output.get("reply")
        supervisor = pipeline_output.get("supervisor")

        # Flatten pipeline output into a single result dict
        result = {
            "id": email["id"],
            "subject": subject,
        }

        # Intake fields
        result["clean_subject"] = intake.get("clean_subject")
        result["clean_body"] = intake.get("clean_body")

        # Classification fields
        result["category"] = classification.get("category")
        result["urgency"] = classification.get("urgency")
        result["sentiment"] = classification.get("sentiment")
        result["thread_status"] = classification.get("thread_status")
        result["needs_escalation"] = classification.get("needs_escalation")

        # Decision fields
        result["final_action"] = decision.get("final_action")
        result["decision_reason"] = decision.get("reason")
        result["decision_confidence"] = decision.get("confidence")

        # Reply and supervisor
        if reply is not None:
            if isinstance(reply, dict):
                # Map to the actual keys returned by ReplyAgent
                result["final_reply"] = (
                    reply.get("reply_text")
                    or reply.get("reply")
                    or reply.get("final_reply")
                    or reply.get("message")
                    or reply.get("content")
                )
            else:
                result["final_reply"] = str(reply)
        else:
            result["final_reply"] = ""

        if supervisor is not None:
            if isinstance(supervisor, dict):
                result["supervisor_decision"] = supervisor.get("decision")
                result["supervisor_notes"] = (
                    supervisor.get("summary_for_supervisor")
                    or supervisor.get("notes")
                )
            else:
                result["supervisor_decision"] = str(supervisor)
                result["supervisor_notes"] = None
        else:
            result["supervisor_decision"] = None
            result["supervisor_notes"] = None

        results.append(result)

    # Save batch results
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nBatch processing completed. Saved {len(results)} results to {os.path.relpath(output_json, PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
