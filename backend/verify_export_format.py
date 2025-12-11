import sys
import os
sys.path.append(os.getcwd())

from datetime import datetime
from app.services.reporting_service import format_datetime_for_export

print("--- Verifying Export Timestamp Format ---")

# Test case: 2025-12-11 11:09:00 UTC (which is 14:09 / 2:09 PM EAT)
test_dt = datetime(2025, 12, 11, 11, 9, 0)
formatted = format_datetime_for_export(test_dt)

print(f"UTC Input: {test_dt}")
print(f"Formatted Output (EAT): {formatted}")

expected = "Dec 11, 2025, 02:09 PM"
if formatted == expected:
    print("✅ SUCCESS: Format matches expected output.")
else:
    print(f"❌ FAILURE: Expected '{expected}', got '{formatted}'")

# Test case: Midnight UTC (3 AM EAT)
test_dt_2 = datetime(2025, 12, 11, 0, 0, 0)
formatted_2 = format_datetime_for_export(test_dt_2)
print(f"UTC Input: {test_dt_2}")
print(f"Formatted Output (EAT): {formatted_2}")

expected_2 = "Dec 11, 2025, 03:00 AM"
if formatted_2 == expected_2:
    print("✅ SUCCESS: Format matches expected output.")
else:
    print(f"❌ FAILURE: Expected '{expected_2}', got '{formatted_2}'")
