import os
import subprocess
import sys

if __name__ == "__main__":
	# Add the current directory to the PYTHONPATH
	env = os.environ.copy()
	env["PYTHONPATH"] = "." + os.pathsep + env.get("PYTHONPATH", "")

	# Run pytest
	sys.exit(subprocess.call([sys.executable, "-m", "pytest"], env=env))
