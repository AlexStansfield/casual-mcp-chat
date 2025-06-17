import sys
from pathlib import Path

from streamlit.web import cli as stcli

from casual_mcp_chat.utils import ensure_default_files


def app():
    ensure_default_files()
    app_path = Path(__file__).parent / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)]
    sys.exit(stcli.main())
