from pathlib import Path
import shutil
import logging

from expense_tracker.utils.path import get_data_directory

logger = logging.getLogger(__name__)


def migrate_legacy_databases() -> None:
    """
    Migrate databases from the legacy source code directory to the new
    platform-specific data directory.

    Legacy location: expense_tracker/data/
    New location: Platform-specific (e.g., ~/Library/Application Support/spendwise-tracker/)

    If legacy databases exist and new location doesn't have them, copy them over.
    If both exist, prefer the new location (no migration).
    """
    legacy_dir = Path("expense_tracker/data")

    # If legacy directory doesn't exist, no migration needed
    if not legacy_dir.exists():
        logger.debug("No legacy database directory found, skipping migration")
        return

    new_dir = get_data_directory()
    db_files = ["transactions.db", "merchant_categories.db"]
    migrated_files = []

    for db_file in db_files:
        legacy_path = legacy_dir / db_file
        new_path = new_dir / db_file

        # Only migrate if legacy file exists and new file doesn't
        if legacy_path.exists() and not new_path.exists():
            try:
                shutil.copy2(legacy_path, new_path)
                migrated_files.append(db_file)
                logger.info(f"Migrated {db_file} from {legacy_path} to {new_path}")
            except Exception as e:
                logger.error(f"Failed to migrate {db_file}: {e}")
                # Continue with other files even if one fails

    if migrated_files:
        logger.info(
            f"Database migration complete. Migrated: {', '.join(migrated_files)}"
        )
        logger.info(
            f"Legacy files remain at {legacy_dir} and can be manually deleted if desired"
        )
    else:
        logger.debug("No database files needed migration")
