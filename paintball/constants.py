import os

from dotenv import load_dotenv
from pathlib2 import Path

# Load env variables
env_path = Path('.') / '.env'
load_dotenv(str(env_path))

PAINT_BALL_GRAPH = os.getenv('PAINT_BALL_GRAPH_PATH')
SYNSETS_GRAPH = os.getenv('SYNSET_GRAPH_PATH')

IMPEDANCE_TABLE = os.getenv('IMPEDANCE_TABLE_PATH')
