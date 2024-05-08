import re
import json

def process_output(output):
    # Remove leading and trailing whitespace
    cleaned_output = output.strip()

    # Extract the JSON part using regular expressions
    json_match = re.search(r'\{.*\}|\[.*\]', cleaned_output)
    if json_match:
        json_data = json_match.group()
        return json_data
    else:
        # If no JSON data found, return an empty string
        return ''

# Example usage
output = """
2024-05-03 07:06:45.032850: Services running on this node:
  acropolis: [1221989, 1222046, 1222047, 1223150]
  alert_manager: [1221475, 1221566, 1221567, 1221622]
  ... (other output) ...
"""

# Clean the output and extract JSON data
cleaned_output = process_output(output)

# Attempt to decode the cleaned output as JSON
if cleaned_output:
    try:
        process_dict = json.loads(cleaned_output)
        print("JSON Data:")
    except json.JSONDecodeError as e:
        print("Error decoding JSON output:", e)
else:
    print("No JSON data found in the output.")

print(process_dict)

