import os
import sys

print(f"sys.executable: {sys.executable}")
print(f"sys.prefix: {sys.prefix}")
print(f"sys.base_prefix: {sys.base_prefix}")
print("sys.path:")
for p in sys.path:
	print(f"  {p}")
print("os.environ['PATH']:")
for p in os.environ["PATH"].split(os.pathsep):
	print(f"  {p}")
