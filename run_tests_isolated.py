import sys
import os
import subprocess

# Get the virtual environment's site-packages path
venv_site_packages = os.path.join(sys.prefix, 'Lib', 'site-packages')

# Filter sys.path to only include venv paths and project paths
new_sys_path = [p for p in sys.path if p.startswith(sys.prefix) or p.startswith(os.getcwd())]

# Add the backend directory to sys.path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in new_sys_path:
    new_sys_path.insert(0, backend_path) # Insert at the beginning for priority

# Add venv site-packages explicitly if not already there
if venv_site_packages not in new_sys_path:
    new_sys_path.insert(0, venv_site_packages) # Insert at the beginning for priority

sys.path = new_sys_path

# Debugging: Print the cleaned sys.path
print("Cleaned sys.path:")
for p in sys.path:
    print(f"  {p}")

# Now run pytest
# We need to run pytest as a subprocess to ensure it uses the modified sys.path
# and to capture its output correctly.
# The 'backend' directory is the rootdir for pytest.
pytest_command = [sys.executable, '-m', 'pytest', 'backend/tests'] # Path relative to project root

# Removed os.chdir calls

try:
    result = subprocess.run(pytest_command, capture_output=True, text=True, check=False)
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
finally:
    pass # No need to change back directory
