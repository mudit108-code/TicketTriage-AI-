#!/bin/bash
# Start FastAPI env server in background
uvicorn server:app --host 0.0.0.0 --port 7860 &

# Wait for server to be ready
sleep 3

# Start Streamlit UI (HF Spaces serves on port 7860 by default)
# Use 8501 for Streamlit and let HF proxy handle it
streamlit run app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
