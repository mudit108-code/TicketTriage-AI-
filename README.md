# 🎫 TicketTriage AI — OpenEnv RL Environment

> **Real-world task**: Train & evaluate AI agents to triage customer support tickets — classifying priority, category, and routing department.

---

## 🌍 Environment Overview

Customer support ticket triage is a high-stakes daily task at every SaaS company. Agents must read raw ticket text and make three simultaneous decisions:

1. **Priority** — How urgently does this need attention? (low / medium / high / critical)
2. **Category** — What type of issue is this? (billing / technical / account / general / refund)
3. **Department** — Who should handle it? (billing_team / tech_support / account_team / general_support)

This is non-trivial: tickets are often ambiguous, multi-topic, and emotionally charged. Frontier models score ~0.65–0.80 on the hard task.

---

## 📐 Action & Observation Space

### Observation 
| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | str | Unique ticket ID |
| `subject` | str | Email subject line |
| `body` | str | Full ticket body |
| `sender_email` | str | Customer email |
| `created_at` | str | Submission timestamp |
| `step` | int | Current step number |
| `max_steps` | int | Total tickets in task |
| `tickets_processed` | int | How many done so far |
| `current_score` | float | Running average score |
| `message` | str | Feedback from last action |

### Action
| Field | Type | Values |
|-------|------|--------|
| `priority` | enum | `low`, `medium`, `high`, `critical` |
| `category` | enum | `billing`, `technical`, `account`, `general`, `refund` |
| `department` | enum | `billing_team`, `tech_support`, `account_team`, `general_support` |
| `summary` | str | 1-sentence summary (required, ≥10 chars) |

---

## 🎯 Tasks

| Task | Difficulty | Tickets | Description |
|------|-----------|---------|-------------|
| `easy_triage` | 🟢 Easy | 3 | Clear-cut tickets with obvious classification |
| `medium_triage` | 🟡 Medium | 5 | Mixed complexity, some ambiguity |
| `hard_triage` | 🔴 Hard | 7 | Ambiguous, multi-issue, high-stakes tickets |

---

## 🏆 Reward Function

Each ticket action is scored 0.0–1.0:
- **Priority** (40%): Exact match = 0.40 | Adjacent = 0.20 | Wrong = 0.00
- **Category** (35%): Exact match = 0.35 | Wrong = 0.00
- **Department** (25%): Exact match = 0.25 | Wrong = 0.00
- **Summary penalty**: -0.10 if summary is missing or < 10 chars

Episode score = mean of all ticket scores.

---

## 🚀 Setup & Usage

### Local Development

```bash
# 1. Clone & install
git clone <your-repo>
cd <your-repo name>
pip install -r requirements.txt

# 2. Start the FastAPI env server
uvicorn server:app --host 0.0.0.0 --port 7860

# 3. Start the Streamlit UI (new terminal)
streamlit run app.py

# 4. Run inference baseline
export HF_TOKEN=your_token
export MODEL_NAME=gpt-4o-mini
python inference.py
```

### Docker

```bash
docker build -t ticket-triage .
docker run -p 7860:7860 -p 8501:8501 \
  -e HF_TOKEN=your_token \
  -e MODEL_NAME=gpt-4o-mini \
  ticket-triage
```

### API Endpoints

```
POST /reset          → Start new episode
POST /step           → Submit triage action
GET  /state          → Current environment state
GET  /tasks          → List available tasks
GET  /info           → Environment metadata
GET  /health         → Health check
```


