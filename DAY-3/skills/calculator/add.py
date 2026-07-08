import os
import sys

# Read arguments from environment variables
a = float(os.environ.get("A", 0))
b = float(os.environ.get("B", 0))
print(f"Result of adding {a} and {b} is {a + b}")
