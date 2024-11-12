import sqlite3
import os
from pathlib import Path


def get_chrome_open_urls():
    """Get open URLs from Chrome."""
    urls = []
    user_data_path = Path(os.getenv('LOCALAPPDATA')) / "Google/Chrome/User Data/Default"
    history_file = user_data_path / "History"

    if not history_file.exists():
        print("Chrome history file not found.")
        return urls

    try:
        # Connect to the Chrome history SQLite database
        with sqlite3.connect(history_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM urls WHERE hidden = 0")
            urls = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        print(f"Error accessing Chrome history file: {e}")
    return urls


def get_edge_open_urls():
    """Get open URLs from Edge."""
    urls = []
    user_data_path = Path(os.getenv('LOCALAPPDATA')) / "Microsoft/Edge/User Data/Default"
    history_file = user_data_path / "History"

    if not history_file.exists():
        print("Edge history file not found.")
        return urls

    try:
        # Connect to the Edge history SQLite database
        with sqlite3.connect(history_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM urls WHERE hidden = 0")
            urls = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        print(f"Error accessing Edge history file: {e}")
    return urls


def get_firefox_open_urls():
    """Get open URLs from Firefox."""
    urls = []
    profile_path = Path(os.getenv('APPDATA')) / "Mozilla/Firefox/Profiles"

    # Find the default profile directory
    profile_dirs = list(profile_path.glob("*.default-release"))
    if not profile_dirs:
        print("Firefox profile directory not found.")
        return urls

    session_file = profile_dirs[0] / "places.sqlite"

    if not session_file.exists():
        print("Firefox session file not found.")
        return urls

    try:
        # Connect to the Firefox places.sqlite database
        with sqlite3.connect(session_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM moz_places")
            urls = [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        print(f"Error accessing Firefox session file: {e}")
    return urls
