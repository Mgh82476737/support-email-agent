# Multi-Agent Email Support System  
*A Kaggle ADK Capstone Project*

This project implements an end-to-end **Multi-Agent AI system** designed to process, classify, triage, and respond to customer support emails.  
The system follows a clean agent-based architecture inspired by modern LLM orchestration patterns and is fully reproducible for Kaggle reviewers.

---

## ⭐ Project Overview

The goal is to simulate a **professional customer-support pipeline** using multiple specialised AI agents:

1. **Intake Agent**  
   Cleans raw email text, extracts the subject/body, removes noise, and normalises content.

2. **Classification Agent**  
   Assigns:
   - category (billing, technical, refund, etc.)
   - urgency (low, medium, high)
   - sentiment (calm, frustrated, angry, confused)
   - escalation hints

3. **Decision Agent**  
   Chooses between:
   - `approve` → generate automatic reply  
   - `escalate_to_human` → route to human support  
   based on sentiment, urgency, and classification outputs.

4. **Reply Agent**  
   Generates a professional, context-aware email reply for all `approve` cases.

5. **Supervisor Agent**  
   Optional review layer that validates reply quality.

---

## 📊 Batch Processing Results

A dataset of **50 synthetic customer emails** is processed end-to-end using:

```bash
python app/run_batch.py
