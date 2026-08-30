
import os


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "shopease.db"
)

MODEL_NAME = "qwen3:8b"

DEBUG_MODE = False
