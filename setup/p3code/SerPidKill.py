import subprocess
import json
import argparse

def run_python_code_remote(python_code, remote_user, remote_host):
    try:
        # Construct the SSH command to run the Python code remotely
        ssh_command = f"ssh {remote_user}@{remote_host} \"python3.6 -c \\\"{python_code}\"\\\""
        print("SSH Command:", ssh_command)

        # Run the SSH command to execute the code on the remote machine
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode != 0:
            print("Error running code remotely:")
            print(result.stderr)
            return {}

        # Get the output from the SSH command
        output = result.stdout.strip()
        print("Output:")
        print(output)

        # Check if the output is empty
        if not output:
            print("Error: Empty output received.")
            return {}

        # Try to load the output as JSON
        try:
            process_dict = json.loads(output)
            return process_dict
        except json.JSONDecodeError as e:
            print("Error decoding JSON output:", e)
            return {}

    except subprocess.CalledProcessError as e:
        print(f"Error running code remotely: {e}")
        return {}

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Python code remotely.")
    parser.add_argument("remote_username", type=str, help="Remote username")
    parser.add_argument("remote_host", type=str, help="Remote host IP address or hostname")
    args = parser.parse_args()
    process_names=["curator", "stargate"]
    # Define the Python code to be executed remotely
    python_code = f"""
import psutil
import json

def get_pids_by_name(process_name):
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pids.append(proc.info['pid'])
    return pids

def get_process_names_with_pids():
    process_dict = {{}}
    process_names = {process_names}
    for name in process_names:
        pids = get_pids_by_name(name)
        process_dict[name] = pids
    return process_dict

result_dict = get_process_names_with_pids()
print(json.dumps(result_dict))

"""

    # Run the Python code remotely and get the process dictionary
    result_dict = run_python_code_remote(python_code, args.remote_username, args.remote_host)

    # Print the dictionary with process names and corresponding PIDs
    print("Process Dictionary:")
    print(result_dict)

