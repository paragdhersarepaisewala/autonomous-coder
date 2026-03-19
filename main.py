#!/usr/bin/env python3
import sys
import os

# Ensure the package is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_populator.main import main

if __name__ == "__main__":
    sys.exit(main())
