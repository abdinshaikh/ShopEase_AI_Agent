import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


DB_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "shopease.db"
)


MEMORY_DB_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "agent_memory.db"
)


LLM_PROVIDER = "gemini"

OLLAMA_MODEL = "qwen3:8b"

GEMINI_MODEL = "gemini-3.5-flash-lite"


DEBUG_MODE = False
