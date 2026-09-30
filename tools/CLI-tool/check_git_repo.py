import sys
import subprocess

# We don't need Git lib for this, can just use subproc
if subprocess.run(["git", "status"], capture_output=True).returncode == 0:
    sys.exit(1)
else:
    sys.exit(0)
