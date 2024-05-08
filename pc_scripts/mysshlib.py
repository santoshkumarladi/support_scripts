import paramiko

class SSHConnectionError(Exception):
    pass

def create_ssh_connection(host, username, password, cmd):
    """Creates an SSH connection to the specified host using the given username and password,
    executes the provided command, and returns the output of the command as a string"""

    try:
        # Create a new SSH client object
        client = paramiko.SSHClient()

        # Automatically add the server's host key
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the host using the provided credentials
        client.connect(host, username=username, password=password)

        # Execute the command on the remote host
        stdin, stdout, stderr = client.exec_command(cmd)

        # Read the output of the command from the stdout stream
        output = stdout.read().decode('utf-8')

        # Close the SSH connection
        client.close()

        # Return the output of the command
        return output

    except paramiko.AuthenticationException:
        raise SSHConnectionError("Authentication failed. Please check your credentials.")

    except paramiko.SSHException:
        raise SSHConnectionError("Unable to establish SSH connection to host.")

    except Exception as e:
        raise SSHConnectionError("An error occurred while creating the SSH connection: {}".format(str(e)))

