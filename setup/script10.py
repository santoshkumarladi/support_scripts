import random
import hashlib
import sqlite3
from datetime import datetime
import os
import platform
import subprocess
import sys
import re
from multiprocessing.pool import ThreadPool

def check_sqlite():
    # Check if SQLite is present
    try:
        import sqlite3
        return True
    except ImportError:
        return False

def install_sqlite():
    system = platform.system()

    # Install SQLite based on the system
    if system == 'Windows':
        subprocess.call(['pip', 'install', 'pysqlite'])
    elif system == 'Linux':
        subprocess.call(['sudo', 'apt-get', 'install', 'sqlite3', 'libsqlite3-dev'])
    elif system == 'Darwin':
        subprocess.call(['brew', 'install', 'sqlite3'])

def configure_sqlite():
    # Set the SQLite library path
    system = platform.system()
    if system == 'Windows':
        os.environ['PATH'] += ';C:\\sqlite'
    elif system == 'Linux':
        os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'

def create_checksum_table(connection):
    cursor = connection.cursor()

    # Create the checksum table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checksums (
            block_id INTEGER PRIMARY KEY,
            checksum TEXT
        )
    """)

    connection.commit()

def parse_size(size_str):
    units = {'B': 1, 'K': 1024, 'M': 1024 ** 2, 'G': 1024 ** 3, 'T': 1024 ** 4}
    matches = re.match(r'(\d+)([BKMGT])', size_str)
    if matches:
        size = int(matches.group(1))
        unit = matches.group(2)
        return size * units[unit]
    else:
        raise ValueError("Invalid size format. Examples: 1024B, 1M, 2G")

def perform_random_io(file_path, block_size, file_size):
    num_blocks = file_size // block_size

    pool = ThreadPool()
    pool.map(lambda block_id: process_block(file_path, block_id, block_size), range(num_blocks))
    pool.close()
    pool.join()

    connection = sqlite3.connect(":memory:")
    create_checksum_table(connection)

    for block_id in range(num_blocks):
        checksum = retrieve_checksum(file_path, block_id)
        save_checksum(connection, block_id, checksum)

    print("Random I/O completed. {} blocks of size {} bytes written to {}.".format(num_blocks, block_size, file_path))

    return connection

def process_block(file_path, block_id, block_size):
    # Generate random data of block size
    data = ''.join([chr(random.randint(0, 255)) for _ in range(block_size)])

    with open(file_path, "r+b") as file:
        # Generate a random offset within the block
        offset = random.randint(0, block_size - 1)

        # Move the file pointer to the block position
        file.seek(block_id * block_size + offset)

        # Write the random data at the current position
        file.write(data)

def save_checksum(connection, block_id, checksum):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO checksums (block_id, checksum) VALUES (?, ?)", (block_id, checksum))
    connection.commit()

def retrieve_checksum(file_path, block_id):
    with open(file_path, 'rb') as file:
        file.seek(block_id * block_size)
        data = file.read(block_size)
        return hashlib.md5(data).hexdigest()

def compare_checksums(connection, file_path, block_size):
    cursor = connection.cursor()
    cursor.execute("SELECT block_id, checksum FROM checksums")

    saved_checksums = cursor.fetchall()
    # Calculate file checksum
    file_checksum = calculate_file_checksum(file_path)
    print("File checksum: {}".format(file_checksum))

    for block_id, saved_checksum in saved_checksums:
        # Retrieve the data from the file at the corresponding block ID
        # and calculate the checksum
        data = retrieve_data(file_path, block_id, block_size)
        calculated_checksum = hashlib.md5(data).hexdigest()

        if saved_checksum != calculated_checksum:
            print("Checksum mismatch for block {}.".format(block_id))
            print("Saved Checksum: {}".format(saved_checksum))
            print("Calculated Checksum: {}".format(calculated_checksum))
        else:
            print("Checksum for block {} matches.".format(block_id))


    # Compare file checksum with the calculated checksums
    with open(file_path + ".checksums", "r") as file:
        lines = file.readlines()

        for line in lines:
            block_id, checksum = line.strip().split(': ')
            block_id = int(block_id)

            data = retrieve_data(file_path, block_id, block_size)
            calculated_checksum = hashlib.md5(data).hexdigest()

            if checksum != calculated_checksum:
                print("Checksum mismatch for block {}.".format(block_id))
                print("Saved Checksum: {}".format(checksum))
                print("Calculated Checksum: {}".format(calculated_checksum))
            else:
                print("Checksum for block {} matches.".format(block_id))

        if file_checksum == calculate_file_checksum(file_path):
            print("File checksum matches.")
        else:
            print("File checksum mismatch.")

def retrieve_data(file_path, block_id, block_size):
    with open(file_path, 'rb') as file:
        file.seek(block_id * block_size)
        return file.read(block_size)

def calculate_file_checksum(file_path):
    with open(file_path, 'rb') as file:
        file_data = file.read()
        return hashlib.md5(file_data).hexdigest()

# Example usage
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <block_size> <file_size> <file_path>")
        sys.exit(1)

    block_size = parse_size(sys.argv[1])
    file_size = parse_size(sys.argv[2])
    file_path = sys.argv[3]

    if not check_sqlite():
        print("SQLite not found. Installing...")
        install_sqlite()
        configure_sqlite()

    connection = perform_random_io(file_path, block_size, file_size)
    compare_checksums(connection, file_path, block_size)

