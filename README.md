## Docker Compose GitOps Operator

This Python script ensures Docker configurations match `docker-compose.yml` and keeps the local Git repository up to date.

### Features

- **Docker Configuration Check**
  - Compares running Docker containers with specified configurations.
  - Verifies various docker compose configurations.
  - Automatically restarts containers if configurations differ.

- **Git Repository Sync**
  - Synchronizes the local Git repository with its remote counterpart.

### Usage

- **Docker Configuration Check**
  - Run `reconcile_docker.py` to maintain Docker setup consistency.

- **Git Repository Sync**
  - Execute `reconcile_git.py` to update the local Git repository from its remote.

- **Run Both Reconcilers**
  - Run the operator in the background using the following command:
`nohup python operator/reconcile.py > output.log &`
  - Kill the process: 
  `pgrep -f your_script.py` && `kill <PID>`

### Requirements

- **Python 3.x**
  - Necessary libraries: `pip install -r requirements.txt`
- **Docker**
- **Docker Compose**

### Configuration

- **Docker Configuration**
  - Define services in `docker-compose.yml` accurately.

- **Define the correct image in the github workflow file**
  - The image should be the same as the one defined in the `docker-compose.yml` file.

### Notes

- Customize error messages or adjust scheduling as needed.
- The operator is designed to run on a Linux machine.