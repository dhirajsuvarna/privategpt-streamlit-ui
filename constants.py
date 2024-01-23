TITLE_STR = "Chat with your docs 📄 using local LLM 🦙"
MODES = ["Query Docs", "Search in Docs", "LLM Chat"]
MODE_CAPTIONS = [
    "Chat with Ingested Docs",
    "Semantic Search in Vector Store",
    "Chat with LLM without context",
]

SERVER = "localhost"
PORT = "8001"

HEALTH_URL = f"http://{SERVER}:{PORT}/health"
INGEST_FILE_URL = f"http://{SERVER}:{PORT}/v1/ingest/file"
INGESTED_LIST_URL = f"http://{SERVER}:{PORT}/v1/ingest/list"
CHAT_COMPLETION_URL = f"http://{SERVER}:{PORT}/v1/chat/completions"
CHUNKS_RETRIEVAL_URL = f"http://{SERVER}:{PORT}/v1/chunks"
