import requests
import ssl
import certifi

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context
# Load the system's trusted SSL certificates
#ssl_context = ssl.create_default_context(cafile=certifi.where())

class SSHRestAPIConnection:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def execute_command(self, cmd):
        url = f"http://{self.host}/ssh_command"
        data = {
            'username': self.username,
            'password': self.password,
            'cmd': cmd
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error executing command: {e}")

        try:
            response_data = response.json()
            if response_data.get('status') == 'error':
                raise Exception(f"Error executing command: {response_data.get('message')}")
            return response_data.get('output')
        except ValueError:
            raise Exception(f"Invalid response from server: {response.text}")

