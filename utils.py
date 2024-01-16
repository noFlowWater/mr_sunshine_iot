import json
import subprocess

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def run_command(command):
    result = subprocess.run(command, check=True, capture_output=True)
    success_message = "Successfully executed: " + " ".join(command)
    failure_message = "Failed to execute: " + " ".join(command)

    if result.returncode == 0:
        print(success_message)
    else:
        print(failure_message)

    if result.stdout:
        print("Output:", result.stdout.decode())
    if result.stderr:
        print("Error:", result.stderr.decode())

def start_pigpiod():
    run_command(["sudo", "pigpiod"])

def stop_pigpiod():
    run_command(["sudo", "killall", "pigpiod"])
