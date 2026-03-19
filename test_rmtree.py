
import os
import stat
import shutil
from github_populator.utils.system_utils import safe_rmtree

def test_safe_rmtree():
    # Create a test directory with a read-only file
    test_dir = "test_rmtree_dir"
    os.makedirs(test_dir, exist_ok=True)
    
    ro_file = os.path.join(test_dir, "ro_file.txt")
    with open(ro_file, 'w') as f:
        f.write("test content")
        
    # Make it read-only
    os.chmod(ro_file, stat.S_IREAD)
    
    print(f"Attempting to remove {test_dir} with safe_rmtree...")
    try:
        # Standard shutil.rmtree would fail on Windows with WinError 5 or PermissionError
        safe_rmtree(test_dir)
        print("Success! Directory removed.")
    except Exception as e:
        print(f"FAILED to remove directory: {e}")
        # Clean up if failed
        try:
            os.chmod(ro_file, stat.S_IWRITE)
            shutil.rmtree(test_dir)
        except:
            pass

if __name__ == "__main__":
    test_safe_rmtree()
