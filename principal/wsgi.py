import os
import sys


# Make imports work even if gunicorn is started from another working directory.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from app import create_app  # noqa: E402

app = create_app()

