
import os
import stat
import shutil
import logging

logger = logging.getLogger(__name__)

def handle_remove_readonly(func, path, excinfo):
    """
    Error handler for shutil.rmtree.
    Clears the read-only bit and retries the removal.
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        # Re-raise the original exception if fixing the permission didn't work
        # This allows higher-level retry logic to see the failure
        raise excinfo[1]

def safe_rmtree(path: str):
    """
    Safely remove a directory tree, handling read-only files (common for .git on Windows).
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
        except Exception as e:
            # If it still fails, check if the path still exists
            if os.path.exists(path):
                raise e
