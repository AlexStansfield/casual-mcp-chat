import sys
from pathlib import Path

from streamlit.web import cli as stcli


def app():
    app_path = Path(__file__).parent / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
