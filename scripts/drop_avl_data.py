"""
Script to drop all data from the approved_vendor_list table
"""

import sys
import os

# Add parent directory to path so we can import from db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.approved_vendor_list import drop_approved_vendor_list_data

if __name__ == "__main__":
    # Drop all data from the approved_vendor_list table
    rows_deleted = drop_approved_vendor_list_data()
    print(f"Successfully dropped all data from the approved_vendor_list table.")
    print(f"The table is now empty and the auto-increment counter has been reset.")
