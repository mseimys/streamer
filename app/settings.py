import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
DATA_DIR = os.path.abspath(os.path.join(ROOT_DIR, "..", "DATA"))
ORIGINAL_DIR = os.path.join(DATA_DIR, "original")
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

print(f"ROOT_DIR: {ROOT_DIR}")
print(f"DATA_DIR: {DATA_DIR}")
print(f"ORIGINAL_DIR: {ORIGINAL_DIR}")
print(f"INPUT_DIR: {INPUT_DIR}")
print(f"OUTPUT_DIR: {OUTPUT_DIR}")

EXTENSIONS_TO_COPY = "*.jpg"
