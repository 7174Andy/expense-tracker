from pathlib import Path
import platform
import os


def get_data_directory() -> Path:
    """
    Returns the path to the data directory for the expense tracker application.
    Creates the directory if it does not exist.

    Platform-specific locations:
    - macOS: ~/Library/Application Support/spendwise-tracker/
    - Linux/Unix: ~/.local/share/spendwise-tracker/
    - Windows: %LOCALAPPDATA%/spendwise-tracker/
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        base_dir = Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        # Use LOCALAPPDATA environment variable, fallback to home/AppData/Local
        base_dir = Path(
            os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
        )
    else:  # Linux and other Unix-like systems
        base_dir = Path.home() / ".local" / "share"

    data_dir = base_dir / "spendwise-tracker"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path(filename: str) -> Path:
    """
    Returns the full path to a database file in the data directory.

    Args:
        filename: Name of the database file (e.g., "transactions.db")

    Returns:
        Path object pointing to the database file
    """
    return get_data_directory() / filename