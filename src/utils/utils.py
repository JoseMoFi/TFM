import logging
from pathlib import Path
from typing import Any, Dict, Optional
import json

from src.utils.constants import NPC_LOG_DIR, WORLD_LOG_DIR 

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------

def setup_npc_logger(npc_name: str) -> logging.Logger:
    """Crea un logger independiente para un NPC concreto."""
    NPC_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = NPC_LOG_DIR / f"{npc_name}.log"

    logger = logging.getLogger(f"npc.{npc_name}")
    logger.setLevel(logging.INFO)

    # Evitar añadir duplicados si ya existe
    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

        logger.addHandler(fh)

    return logger

def setup_world_logger() -> logging.Logger:
    """Crea el logger para eventos del mundo."""
    WORLD_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = WORLD_LOG_DIR / "world.log"

    logger = logging.getLogger("world")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

        logger.addHandler(fh)

    return logger

# ------------------------------------------------------------------------------
# Utilidades de FS
# ------------------------------------------------------------------------------
def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def read_json(path: Path, logger, default: Optional[Dict[str, Any]] = None, ) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        raise
    except Exception as e:
        logger.error("Error leyendo JSON %s: %s", path, e)
        return default or {}

def write_json(path: Path, obj: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)