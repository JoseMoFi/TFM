from pathlib import Path

NPC_PATH =  Path(".\data")
UTILS_PATH =  Path(".\utils")
LOG_DIR =  Path("./logs")

NPC_LOG_DIR = LOG_DIR / "npc_logs"
WORLD_LOG_DIR = LOG_DIR / "world"

SCREEN_WIDTH  = 960
SCREEN_HEIGHT = 640
SCREEN_TITLE  = "NPC World"
TILE_SIZE     = 32

GRID_COLS = 26
GRID_ROWS = 18

MOVE_SPEED_TPS = 6.0
FOV_RADIUS     = 5