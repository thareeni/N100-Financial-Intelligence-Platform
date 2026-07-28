"""
Forwarder for Streamlit Dashboard. Imports and runs src/dashboard/app.py.
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.dashboard.app import main

if __name__ == "__main__":
    main()
