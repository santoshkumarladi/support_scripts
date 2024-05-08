 #!/usr/bin/python

import os
import pandas as pd
import re

def parse_output_and_get_total_ssd_usage(output):
    # Split the output into lines and filter SSD lines (exclude rows with N/A)
    lines = [line for line in output.strip().split('\n') if "SSD" in line and "N/A" not in line]

    # Create a DataFrame from the filtered lines
    df = pd.DataFrame([re.split(r'\s{2,}', line.strip()) for line in lines], columns=["Tier Name", "Tier Usage", "Tier Size", "Tier Usage Pct"])

    # Remove percentage sign and convert "Tier Usage Pct" column to numeric, handling missing values
    df['Tier Usage Pct'] = pd.to_numeric(df['Tier Usage Pct'].str.replace('%', ''), errors='coerce')

    # Calculate the total SSD usage percentage (ignoring NaN values)
    total_ssd_usage_pct = df['Tier Usage Pct'].sum(skipna=True)

    return total_ssd_usage_pct

# Example usage:
output_from_remote_command = """
Storage Pool: default-storage-pool-73563 ILM Down Migrate threshold: 70

   +------------------------------------------------+
   | Tier Name  |Tier Usage|Tier Size|Tier Usage Pct|
   |------------+----------+---------+--------------|
   |SSD-MEM-NVMe|   N/A    |   N/A   |     N/A      |
   |------------+----------+---------+--------------|
   |  SSD-PCIe  |   N/A    |   N/A   |     N/A      |
   |------------+----------+---------+--------------|
   |[1]SSD-SATA | 4.86 TB  | 5.00 TB |     97%      |
   |------------+----------+---------+--------------|
   |[2]DAS-SATA | 50.40 TB |94.95 TB |     53%      |
   +------------------------------------------------+
"""

total_ssd_usage = parse_output_and_get_total_ssd_usage(output_from_remote_command)
print("Total SSD usage percentage (only digits):", total_ssd_usage)

