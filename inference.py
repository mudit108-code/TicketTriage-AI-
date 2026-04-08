"""
inference.py — OpenEnv
Customer Support Ticket Triage Environment
Follows strict [START] / [STEP] / [END] stdout format.
"""
import os
import sys
import json
import textwrap
from typing import List, Optional

import requests
from openai import OpenAI

# ── Environment Variables ────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.getenv("HF_TOKEN")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN )

# ── Logging Helpers ──────────────────────────────────────────────────────────
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    err = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    r_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={r_str}", flush=True)

# ── Prompts ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = textwrap.dedent("""
You are an expert customer support manager. Your job is to triage support tickets.

For each ticket, respond with ONLY valid JSON in this exact format:
{
  "priority": "<low|medium|high|critical>",
  "category": "<billing|technical|account|general|refund>",
  "department": "<billing_team|tech_support|account_team|general_support>",
  "summary": "<one sentence summary of the issue>"
}

Priority guidelines:
- critical: production down, legal deadline, major data loss, revenue impact
- high: can't login, duplicate charge, broken core feature
- medium: performance issues, billing questions, integration problems
- low: general inquiries, feature requests, no urgency

Category guidelines:
- billing: invoices, charges, pricing, payments
- technical: bugs, API issues, integrations, performance
- account: login, access, user management, data export
- refund: refund requests, cancellations
- general: complaints, feedback, multi-topic

Department guidelines:
- billing_team: billing, refund, pricing issues
- tech_support: technical bugs, API, integrations
- account_team: account management, retention risk, compliance
- general_support: general inquiries
""").strip()

def get_action(obs: dict) -> dict:
    """Call LLM to get triage action for current ticket observation."""
    user_msg = textwrap.dedent(f"""
    Triage this support ticket:

    Subject: {obs['subject']}
    From: {obs['sender_email']}
    Body: {obs['body']}

    Respond with JSON only.
    """).strip()

    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        text = resp.choices[0].message.content.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return {
            "priority": "medium",
            "category": "general",
            "department": "general_support",
            "summary": "Could not parse ticket",
        }

# ── Environment API Calls ────────────────────────────────────────────────────
def env_reset(task_name: str) -> dict:
    r = requests.post(f"{ENV_BASE_URL}/reset", json={"task_name": task_name}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(task_name: str, action: dict) -> dict:
    payload = {"task_name": task_name, **action}
    r = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# ── Main Task Runner ─────────────────────────────────────────────────────────
def run_task(task_name: str, benchmark: str = "ticket_triage") -> float:
    rewards: List[float] = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(task=task_name, env=benchmark, model=MODEL_NAME)

    try:
        result = env_reset(task_name)
        obs = result["observation"]
        done = result.get("done", False)

        step = 0
        while not done:
            step += 1
            action = get_action(obs)
            action_str = (
                f"priority={action['priority']} "
                f"category={action['category']} "
                f"dept={action['department']}"
            )

            try:
                result = env_step(task_name, action)
                reward = float(result.get("reward", 0.0))
                done = result.get("done", False)
                obs = result.get("observation", obs)
                error = result.get("info", {}).get("error")
            except Exception as e:
                reward = 0.0
                done = True
                error = str(e)

            rewards.append(reward)
            steps_taken = step
            log_step(step=step, action=action_str, reward=reward, done=done, error=error)

        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= 0.5

    except Exception as e:
        print(f"[DEBUG] Task error: {e}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score

# ── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tasks = ["easy_triage", "medium_triage", "hard_triage"]
    all_scores = []

    print("=" * 60, flush=True)
    print("  Ticket Triage OpenEnv — Baseline Evaluation", flush=True)
    print("=" * 60, flush=True)

    for task in tasks:
        print(f"\n--- Running task: {task} ---", flush=True)
        s = run_task(task)
        all_scores.append(s)
        print(f"Task score: {s:.2f}", flush=True)

    overall = sum(all_scores) / len(all_scores)
    print(f"\n{'='*60}", flush=True)
    print(f"  OVERALL BASELINE SCORE: {overall:.2f}", flush=True)
    print(f"{'='*60}", flush=True)
