import sys
import yaml

github_sha = sys.argv[1] if len(sys.argv) > 1 else None

if github_sha:
    # Read the docker-compose.yml file
    with open('docker-compose.yaml', 'r') as file:
        compose_file = yaml.safe_load(file)

    # Update the image tag for the nginx service
    if 'services' in compose_file and 'nginx' in compose_file['services']:
        compose_file['services']['nginx']['image'] = f"ddeeh/composegitops:{github_sha}"

    # Write the updated docker-compose.yml file
    with open('docker-compose.yml', 'w') as file:
        yaml.dump(compose_file, file)
else:
    print("GitHub SHA not provided.")
