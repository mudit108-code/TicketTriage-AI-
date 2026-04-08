"""
FastAPI server exposing OpenEnv-compliant endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from environment import (
    TicketTriageEnv, TicketAction, Priority, Category, Department
)

app = FastAPI(
    title="Ticket Triage OpenEnv",
    description="Customer Support Ticket Triage RL Environment",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global env registry (keyed by task_name for simplicity)
_envs: dict = {}

def get_env(task_name: str = "easy_triage") -> TicketTriageEnv:
    if task_name not in _envs:
        _envs[task_name] = TicketTriageEnv(task_name)
    return _envs[task_name]


class ResetRequest(BaseModel):
    task_name: Optional[str] = "easy_triage"

class StepRequest(BaseModel):
    task_name: Optional[str] = "easy_triage"
    priority: Priority
    category: Category
    department: Department
    summary: str


@app.get("/")
def root():
    return {"status": "ok", "env": "ticket_triage", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/reset")
def reset(req: ResetRequest = None):
    task = (req.task_name if req else None) or "easy_triage"
    env = TicketTriageEnv(task)
    _envs[task] = env
    obs = env.reset()
    return {"observation": obs.model_dump(), "done": False, "reward": 0.0}

@app.post("/step")
def step(req: StepRequest):
    env = get_env(req.task_name)
    action = TicketAction(
        priority=req.priority,
        category=req.category,
        department=req.department,
        summary=req.summary,
    )
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info,
    }

@app.get("/state")
def state(task_name: str = "easy_triage"):
    env = get_env(task_name)
    return env.state()

@app.get("/tasks")
def list_tasks():
    from environment import TASKS
    return {"tasks": list(TASKS.keys())}

@app.get("/info")
def info():
    return {
        "name": "ticket_triage",
        "description": "Customer Support Ticket Triage Environment",
        "tasks": ["easy_triage", "medium_triage", "hard_triage"],
        "action_space": {
            "priority": ["low", "medium", "high", "critical"],
            "category": ["billing", "technical", "account", "general", "refund"],
            "department": ["billing_team", "tech_support", "account_team", "general_support"],
            "summary": "string (1-sentence ticket summary)",
        },
        "observation_space": {
            "ticket_id": "string",
            "subject": "string",
            "body": "string",
            "sender_email": "string",
            "created_at": "string",
            "task_name": "string",
            "step": "int",
            "max_steps": "int",
            "tickets_processed": "int",
            "current_score": "float",
            "message": "string",
        },
        "reward_range": [0.0, 1.0],
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
