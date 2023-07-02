import os
from pathlib import Path

from dotenv import load_dotenv

__version__ = "0.0.1"

current_file = Path(__file__).parent.parent.resolve()
envfile = current_file / 'local.env'
load_dotenv(envfile)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
