import datetime
import os
import subprocess

import yaml
import docker

COMPOSE_PATH = 'docker-compose.yml'

# Define error messages
error_messages = {
    'no_container_found': 'The service is not running as expected - no matching container found.',
    'ports_do_not_match': 'Ports configuration does not match between the compose file and the running container.',
    'environment_variables_do_not_match': 'Environment variables do not match between the compose file and the running container.',
    'restart_policy_does_not_match': 'Restart policy does not match between the compose file and the running container.',
    'networks_do_not_match': 'Networks configuration does not match between the compose file and the running container.',
    'healthcheck_does_not_match': 'Healthcheck configuration does not match between the compose file and the running container.',
    'logging_does_not_match': 'Logging configuration does not match between the compose file and the running container.',
    'labels_do_not_match': 'Labels configuration does not match between the compose file and the running container.',
    'extra_hosts_do_not_match': 'Extra hosts configuration does not match between the compose file and the running container.',
    'sysctls_do_not_match': 'Sysctls configuration does not match between the compose file and the running container.'
}


def load_docker_compose(file_path):
    with open(file_path, 'r') as file:
        try:
            compose_data = yaml.safe_load(file)
            return compose_data
        except yaml.YAMLError as exc:
            print(exc)
            return None


def get_running_containers(client):
    container_list = client.containers.list()
    return container_list


def find_matching_container(running_containers, service_config):
    found_container = None
    for container in running_containers:
        if is_image_matching(container.image.tags[0], service_config.get('image')):
            found_container = container
            break
    return found_container


def is_image_matching(container_image, config_image):
    """ Check that the container is running the correct image. """
    return container_image == config_image


def are_ports_matching(container_ports, config_ports):
    """ Check that the container is running the correct ports. """
    if not config_ports:
        return True

    for port, value in container_ports.items():
        container_port = f"{value[0]['HostPort']}:{port.split('/')[0]}"
        if container_port not in config_ports:
            return False
    return True


def are_environment_variables_matching(container_env, config_env):
    """Check if container environment variables match the configuration."""
    if not config_env:
        return True

    container_env_dict = {variable.split('=', 1)[0]: variable.split('=', 1)[1] for variable in container_env}

    for env_var in config_env:
        key, value = env_var.split('=', 1)
        if key not in container_env_dict or container_env_dict[key] != value:
            return False

    return True


def is_restart_policy_matching(container_restart, config_restart):
    """Check if the container's restart policy matches the configuration."""
    if not config_restart:
        return True

    return container_restart == config_restart


def are_networks_matching(container_networks, config_networks):
    """Check if container networks match the configuration."""
    if not config_networks:
        return True

    container_network_list = [net.split('_')[-1] for net in container_networks.keys()]

    for network in config_networks:
        if network not in container_network_list:
            return False

    return True


def normalize_time(time_value):
    """Normalize time values to string representation."""
    if isinstance(time_value, int):
        # Convert nanoseconds to seconds and format as string
        return f"{time_value // 10**9}s"
    return str(time_value)


def is_healthcheck_matching(container_healthcheck, config_healthcheck):
    """Check if container health check configuration matches the configuration."""
    if not config_healthcheck:
        return True

    container_test = container_healthcheck.get('Test', [])
    container_interval = normalize_time(container_healthcheck.get('Interval', ''))
    container_timeout = normalize_time(container_healthcheck.get('Timeout', ''))
    container_retries = container_healthcheck.get('Retries', '')

    return (
        container_test == config_healthcheck.get('test', []) and
        container_interval == config_healthcheck.get('interval', '') and
        container_timeout == config_healthcheck.get('timeout', '') and
        container_retries == config_healthcheck.get('retries', '')
    )


def is_logging_matching(container_logging, config_logging):
    """Check if container logging configuration matches the configuration."""
    if not config_logging:
        return True

    container_driver = container_logging.get('Type', '')
    container_options = container_logging.get('Config', {})

    return (
        container_driver == config_logging.get('driver', '') and
        container_options == config_logging.get('options', {})
    )


def is_labels_matching(container_labels, config_labels):
    """Check if container label configuration matches the configuration."""
    if not config_labels:
        return True

    # Filter container labels to only include keys present in config_labels
    filtered_container_labels = {key: container_labels.get(key, '') for key in config_labels}

    return filtered_container_labels == config_labels


def is_extra_hosts_matching(container_extra_hosts, config_extra_hosts):
    """Check if container extra_hosts configuration matches the configuration."""
    if not config_extra_hosts:
        return True

    # Extract host names from the container extra_hosts configuration
    container_hosts = [host.split(':')[0] for host in container_extra_hosts]

    # Extract host names from the config extra_hosts configuration
    config_hosts = [host.split(':')[0] for host in config_extra_hosts]

    return set(container_hosts) == set(config_hosts)


def is_sysctls_matching(container_sysctls, config_sysctls):
    """Check if container sysctls configuration matches the configuration."""
    if not config_sysctls:
        return True
    # Extract keys from the container sysctls configuration
    container_keys = [sysctl.split('=')[0] for sysctl in container_sysctls]

    # Extract keys from the config sysctls configuration
    config_keys = [sysctl.split('=')[0] for sysctl in config_sysctls]

    return set(container_keys) == set(config_keys)


def compare_config(container_info, service_config, service_name):
    error_msgs = []  # Store error messages for this comparison

    if not are_ports_matching(container_info['HostConfig']['PortBindings'], service_config.get('ports')):
        error_msgs.append((service_name, error_messages['ports_do_not_match']))

    if not are_environment_variables_matching(container_info['Config']['Env'], service_config.get('environment')):
        error_msgs.append((service_name, error_messages['environment_variables_do_not_match']))

    if not is_restart_policy_matching(container_info['HostConfig']['RestartPolicy']['Name'], service_config.get('restart')):
        error_msgs.append((service_name, error_messages['restart_policy_does_not_match']))

    if not are_networks_matching(container_info['NetworkSettings'].get('Networks'), service_config.get('networks')):
        error_msgs.append((service_name, error_messages['networks_do_not_match']))

    if not is_healthcheck_matching(container_info['Config'].get('Healthcheck'), service_config.get('healthcheck')):
        error_msgs.append((service_name, error_messages['healthcheck_does_not_match']))

    if not is_logging_matching(container_info['HostConfig'].get('LogConfig'), service_config.get('logging')):
        error_msgs.append((service_name, error_messages['logging_does_not_match']))

    if not is_labels_matching(container_info['Config'].get('Labels'), service_config.get('labels')):
        error_msgs.append((service_name, error_messages['labels_do_not_match']))

    if not is_extra_hosts_matching(container_info['HostConfig'].get('ExtraHosts'), service_config.get('extra_hosts')):
        error_msgs.append((service_name, error_messages['extra_hosts_do_not_match']))

    if not is_sysctls_matching(container_info['HostConfig'].get('Sysctls'), service_config.get('sysctls')):
        error_msgs.append((service_name, error_messages['sysctls_do_not_match']))

    return error_msgs  # Return any collected error messages with service names


def validate_services(compose_services, client):
    running_containers = get_running_containers(client)
    error_msgs = {}  # Store error messages for each service

    for service_name, service_config in compose_services.items():
        container = find_matching_container(running_containers, service_config)
        if container:
            error_msgs[service_name] = compare_config(container.attrs, service_config, service_name)
        else:
            error_msgs[service_name] = [error_messages['no_container_found']]

    return error_msgs  # Return error messages for all services


def validate_items(config_items, client, item_type, project_name):
    docker_items = getattr(client, item_type).list()
    docker_item_names = [item.name.split('/')[-1] for item in docker_items]

    error_msgs = []  # Store error messages for this item type

    for item_name in config_items:
        full_item_name = f"{project_name}_{item_name}" if project_name else item_name
        if full_item_name not in docker_item_names:
            error_msgs.append(f"{item_type.capitalize()} '{full_item_name}' is not present or not created.")

    return error_msgs  # Return error messages for the items


def get_project_name(compose_path):
    directory = os.path.dirname(os.path.abspath(compose_path))
    return os.path.basename(directory)


def docker_compose_down():
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        with open('/dev/null', 'w') as devnull:
            subprocess.run(["docker-compose", "down"], check=True, stdout=devnull, stderr=subprocess.STDOUT)
        print("Docker Compose down successful")
    except subprocess.CalledProcessError as e:
        print(f"Error executing docker-compose down: {e}")


def docker_compose_up():
    try:
        with open('/dev/null', 'w') as devnull:
            subprocess.run(["docker-compose", "up", "-d"], check=True, stdout=devnull, stderr=subprocess.STDOUT)
        print("Docker Compose up successful")
    except subprocess.CalledProcessError as e:
        print(f"Error executing docker-compose up: {e}")


def reconcile():
    """
    Check that the docker-compose file is running as expected.
    Dynamically check that the correct configuration is running.
    """
    client = docker.from_env()
    compose_config = load_docker_compose(COMPOSE_PATH)
    # In the reconcile function
    project_name = get_project_name(COMPOSE_PATH)

    # Validate that running containers are matching the configuration.
    validation_errors = {}  # Store all validation errors

    for root_level_key in compose_config:
        if root_level_key == 'services':
            validation_errors.update(validate_services(compose_config[root_level_key], client))
        elif root_level_key == 'volumes':
            validation_errors['volumes'] = validate_items(compose_config[root_level_key], client, 'volumes', project_name)
        elif root_level_key == 'networks':
            validation_errors['networks'] = validate_items(compose_config[root_level_key], client, 'networks', project_name)

    # Update the running containers to match the configuration if out of sync.
    reconcile_errors = [error for errors in validation_errors.values() for error in errors]
    if reconcile_errors:
        print("Reconcile failed:")
        for error_message in reconcile_errors:
            print(error_message)

        docker_compose_down()
        docker_compose_up()
    else:
        # print the timestamp and that the app is in sync
        print(f"{datetime.datetime.now()} - App is in sync")


if __name__ == '__main__':
    reconcile()
