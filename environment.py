"""
Customer Support Ticket Triage Environment
Real-world task: classify, prioritize, and route support tickets
"""
import random
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel

# ── Data Models ─────────────────────────────────────────────────────────────

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Category(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"
    REFUND = "refund"

class Department(str, Enum):
    BILLING_TEAM = "billing_team"
    TECH_SUPPORT = "tech_support"
    ACCOUNT_TEAM = "account_team"
    GENERAL_SUPPORT = "general_support"

class TicketObservation(BaseModel):
    ticket_id: str
    subject: str
    body: str
    sender_email: str
    created_at: str
    task_name: str
    step: int
    max_steps: int
    tickets_processed: int
    current_score: float
    message: str = ""

class TicketAction(BaseModel):
    priority: Priority
    category: Category
    department: Department
    summary: str  # 1-sentence summary

class TicketReward(BaseModel):
    value: float
    reason: str

# ── Ticket Dataset ───────────────────────────────────────────────────────────

TICKETS = [
    # Easy tickets
    {
        "ticket_id": "T001",
        "subject": "Can't login to my account",
        "body": "Hi, I've been trying to login for 2 hours but keep getting 'invalid password'. I haven't changed anything. Please help!",
        "sender_email": "user@example.com",
        "created_at": "2024-01-15 09:00:00",
        "expected_priority": Priority.HIGH,
        "expected_category": Category.ACCOUNT,
        "expected_department": Department.ACCOUNT_TEAM,
    },
    {
        "ticket_id": "T002",
        "subject": "Question about pricing",
        "body": "Hello, I was wondering if you offer any discounts for annual subscriptions? No rush, just curious.",
        "sender_email": "prospect@gmail.com",
        "created_at": "2024-01-15 10:00:00",
        "expected_priority": Priority.LOW,
        "expected_category": Category.BILLING,
        "expected_department": Department.BILLING_TEAM,
    },
    {
        "ticket_id": "T003",
        "subject": "URGENT: Production system down!",
        "body": "CRITICAL: Our entire production system is down. We're losing $10k per minute. All API calls returning 500. This is a P0 incident. Need immediate help!",
        "sender_email": "cto@bigcorp.com",
        "created_at": "2024-01-15 11:00:00",
        "expected_priority": Priority.CRITICAL,
        "expected_category": Category.TECHNICAL,
        "expected_department": Department.TECH_SUPPORT,
    },
    # Medium tickets
    {
        "ticket_id": "T004",
        "subject": "Double charged on invoice #4521",
        "body": "I noticed I was charged twice for the same invoice this month. Invoice #4521 shows $99 charged on both Jan 5 and Jan 7. Please refund the duplicate charge.",
        "sender_email": "client@business.com",
        "created_at": "2024-01-15 12:00:00",
        "expected_priority": Priority.HIGH,
        "expected_category": Category.REFUND,
        "expected_department": Department.BILLING_TEAM,
    },
    {
        "ticket_id": "T005",
        "subject": "API rate limits seem off",
        "body": "We're hitting rate limits even though we're well under our plan's quota. Our plan allows 1000 req/min but we're getting throttled at ~200. This is affecting our app's performance.",
        "sender_email": "dev@startup.io",
        "created_at": "2024-01-15 13:00:00",
        "expected_priority": Priority.MEDIUM,
        "expected_category": Category.TECHNICAL,
        "expected_department": Department.TECH_SUPPORT,
    },
    {
        "ticket_id": "T006",
        "subject": "Need to update billing address",
        "body": "We've moved offices and need to update our billing address for tax purposes. New address: 123 New St, Austin TX 78701. Can you update this on our account?",
        "sender_email": "finance@company.com",
        "created_at": "2024-01-15 14:00:00",
        "expected_priority": Priority.MEDIUM,
        "expected_category": Category.BILLING,
        "expected_department": Department.BILLING_TEAM,
    },
    # Hard tickets (ambiguous)
    {
        "ticket_id": "T007",
        "subject": "Unhappy with service",
        "body": "I've been a customer for 3 years and frankly the service quality has declined. The dashboard is slow, support takes days to respond, and I was charged for features I don't use. I'm considering cancelling.",
        "sender_email": "loyal@customer.com",
        "created_at": "2024-01-15 15:00:00",
        "expected_priority": Priority.HIGH,
        "expected_category": Category.GENERAL,
        "expected_department": Department.ACCOUNT_TEAM,
    },
    {
        "ticket_id": "T008",
        "subject": "Integration not working after update",
        "body": "Since your last update, our Slack integration stopped posting notifications. Also, our billing webhook is failing — we're not getting payment confirmations. Started around Jan 12.",
        "sender_email": "admin@saas.com",
        "created_at": "2024-01-15 16:00:00",
        "expected_priority": Priority.HIGH,
        "expected_category": Category.TECHNICAL,
        "expected_department": Department.TECH_SUPPORT,
    },
    {
        "ticket_id": "T009",
        "subject": "Refund request for unused subscription",
        "body": "I signed up for the annual plan 3 days ago but realized it doesn't support my use case. Per your 7-day refund policy, I'd like a full refund. Order #ORD-2024-8821.",
        "sender_email": "newuser@email.com",
        "created_at": "2024-01-15 17:00:00",
        "expected_priority": Priority.MEDIUM,
        "expected_category": Category.REFUND,
        "expected_department": Department.BILLING_TEAM,
    },
    {
        "ticket_id": "T010",
        "subject": "Data export for compliance audit",
        "body": "We need a full export of all our data (users, logs, transactions) for a GDPR compliance audit due in 48 hours. This is legally required. What format can you provide?",
        "sender_email": "legal@enterprise.eu",
        "created_at": "2024-01-15 18:00:00",
        "expected_priority": Priority.CRITICAL,
        "expected_category": Category.ACCOUNT,
        "expected_department": Department.ACCOUNT_TEAM,
    },
]

# ── Task Configs ─────────────────────────────────────────────────────────────

TASKS = {
    "easy_triage": {
        "name": "easy_triage",
        "description": "Classify and prioritize 3 straightforward support tickets",
        "difficulty": "easy",
        "ticket_ids": ["T001", "T002", "T003"],
        "max_steps": 3,
    },
    "medium_triage": {
        "name": "medium_triage",
        "description": "Handle 5 mixed-complexity tickets requiring nuanced routing",
        "difficulty": "medium",
        "ticket_ids": ["T001", "T003", "T004", "T005", "T006"],
        "max_steps": 5,
    },
    "hard_triage": {
        "name": "hard_triage",
        "description": "Process 7 ambiguous, multi-issue tickets under pressure",
        "difficulty": "hard",
        "ticket_ids": ["T004", "T005", "T007", "T008", "T009", "T010", "T003"],
        "max_steps": 7,
    },
}

# ── Grader ───────────────────────────────────────────────────────────────────

def grade_action(action: TicketAction, ticket: dict) -> Tuple[float, str]:
    """Score an action against expected values. Returns (score 0-1, reason)."""
    score = 0.0
    reasons = []

    # Priority (40%)
    if action.priority == ticket["expected_priority"]:
        score += 0.40
        reasons.append("✓ Priority correct")
    elif _priority_adjacent(action.priority, ticket["expected_priority"]):
        score += 0.20
        reasons.append("~ Priority off by one level")
    else:
        reasons.append("✗ Priority wrong")

    # Category (35%)
    if action.category == ticket["expected_category"]:
        score += 0.35
        reasons.append("✓ Category correct")
    else:
        reasons.append("✗ Category wrong")

    # Department (25%)
    if action.department == ticket["expected_department"]:
        score += 0.25
        reasons.append("✓ Department correct")
    else:
        reasons.append("~ Department wrong")

    return round(score, 2), " | ".join(reasons)

def _priority_adjacent(a: Priority, b: Priority) -> bool:
    order = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL]
    return abs(order.index(a) - order.index(b)) == 1

# ── Environment ──────────────────────────────────────────────────────────────

class TicketTriageEnv:
    def __init__(self, task_name: str = "easy_triage"):
        if task_name not in TASKS:
            raise ValueError(f"Unknown task: {task_name}. Choose from {list(TASKS.keys())}")
        self.task_cfg = TASKS[task_name]
        self.ticket_lookup = {t["ticket_id"]: t for t in TICKETS}
        self._reset_state()

    def _reset_state(self):
        self._step = 0
        self._rewards: List[float] = []
        self._ticket_queue = [
            self.ticket_lookup[tid] for tid in self.task_cfg["ticket_ids"]
        ]
        self._current_idx = 0
        self._done = False
        self._total_score = 0.0
        self._history: List[dict] = []

    def reset(self) -> TicketObservation:
        self._reset_state()
        return self._make_obs("New session started. Process each ticket carefully.")

    def state(self) -> dict:
        return {
            "task": self.task_cfg["name"],
            "step": self._step,
            "done": self._done,
            "tickets_processed": self._current_idx,
            "total_tickets": len(self._ticket_queue),
            "rewards": self._rewards,
            "total_score": self._total_score,
            "history": self._history,
        }

    def step(self, action: TicketAction) -> Tuple[TicketObservation, float, bool, dict]:
        if self._done:
            obs = self._make_obs("Episode already done.")
            return obs, 0.0, True, {"error": "Episode done"}

        if self._current_idx >= len(self._ticket_queue):
            self._done = True
            obs = self._make_obs("All tickets processed!")
            return obs, 0.0, True, {}

        ticket = self._ticket_queue[self._current_idx]
        score, reason = grade_action(action, ticket)

        # Penalty for empty summary
        if not action.summary or len(action.summary.strip()) < 10:
            score = max(0.0, score - 0.1)
            reason += " | ✗ Summary too short"

        self._step += 1
        self._current_idx += 1
        self._rewards.append(score)
        self._total_score = sum(self._rewards) / len(self._rewards)

        self._history.append({
            "ticket_id": ticket["ticket_id"],
            "subject": ticket["subject"],
            "action": action.model_dump(),
            "score": score,
            "reason": reason,
            "expected": {
                "priority": ticket["expected_priority"],
                "category": ticket["expected_category"],
                "department": ticket["expected_department"],
            }
        })

        done = self._current_idx >= len(self._ticket_queue)
        self._done = done

        msg = f"Ticket {ticket['ticket_id']} scored {score:.2f}. {reason}"
        if done:
            msg += f" | Final score: {self._total_score:.2f}"

        obs = self._make_obs(msg)
        return obs, score, done, {"reason": reason, "ticket_id": ticket["ticket_id"]}

    def _make_obs(self, message: str = "") -> TicketObservation:
        if self._current_idx < len(self._ticket_queue):
            ticket = self._ticket_queue[self._current_idx]
        else:
            # Return last ticket info when done
            ticket = self._ticket_queue[-1] if self._ticket_queue else {
                "ticket_id": "NONE", "subject": "Done", "body": "",
                "sender_email": "", "created_at": ""
            }

        return TicketObservation(
            ticket_id=ticket["ticket_id"],
            subject=ticket["subject"],
            body=ticket["body"],
            sender_email=ticket["sender_email"],
            created_at=ticket["created_at"],
            task_name=self.task_cfg["name"],
            step=self._step,
            max_steps=self.task_cfg["max_steps"],
            tickets_processed=self._current_idx,
            current_score=self._total_score,
            message=message,
        )

    def close(self):
        pass
