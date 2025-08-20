import sys
import os

print(f"sys.executable: {sys.executable}")
print(f"sys.prefix: {sys.prefix}")
print(f"sys.base_prefix: {sys.base_prefix}")
print(f"sys.path:")
for p in sys.path:
    print(f"  {p}")
print(f"os.environ['PATH']:")
for p in os.environ['PATH'].split(os.pathsep):
    print(f"  {p}")
