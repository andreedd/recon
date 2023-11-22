import yaml
import docker

COMPOSE_PATH = '/Users/andre/dev/recon/docker-compose.yml'

error_messages = {
    'no_container_found': 'The image defined in the compose file does not match a image of a running container.',
    'ports_do_not_match': 'The ports defined in the compose file does not match the ports of the running container.',
}


def load_docker_compose(file_path):
    # TODO: Extend to be able to read multiple compose files, e.g. if main compose extends other configuration yaml's.
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


def is_image_matching_config(container_image, config_image):
    """ Check that the container is running the correct image. """
    return container_image == config_image


def is_ports_matching_config(container_ports, config_ports):
    """ Check that the container is running the correct ports. """

    print(f"Container ports: {container_ports}")
    for port, value in container_ports.items():
        container_port = f"{value[0]['HostPort']}:{port.split('/')[0]}"
        if container_port in config_ports:
            print("Port matches")
        else:
            print(error_messages['ports_do_not_match'])
            return error_messages['ports_do_not_match']


def find_matching_container(running_containers, service_config):
    found_container = None
    for container in running_containers:
        if is_image_matching_config(container.image.tags[0], service_config.get('image')):
            print("Image matches")
            found_container = container
            break
    return found_container


def validate_services(compose_services, client):
    running_containers = get_running_containers(client)

    for service_name, service_config in compose_services.items():
        print(f"Service: {service_name}")
        print(f"Service config: {service_config}")
        container = find_matching_container(running_containers, service_config)
        if container:
            print(f"Found container: {container}")
            print(f"container config: {container.attrs['Config']}")
            is_ports_matching_config(container.ports, service_config.get('ports'))

        else:
            print(error_messages['image_do_not_match'])
            break


def reconcile():
    """
    Check that the docker-compose file is running as expected.
    Dynamically check that the correct configuration is running.
    """
    client = docker.from_env()
    compose_data = load_docker_compose(COMPOSE_PATH)
    print(compose_data)

    # Validate that running containers are matching the configuration.
    for root_level_key in compose_data:
        if root_level_key == 'version':
            print(f"Version: {compose_data[root_level_key]}")
        elif root_level_key == 'services':
            validate_services(compose_data[root_level_key], client)
        elif root_level_key == 'volumes':
            # validate_volumes(compose_data[root_level_key], client)
            pass
        elif root_level_key == 'networks':
            # validate_networks(compose_data[root_level_key], client)
            pass

    # Update the running containers to match the configuration if out of sync.
    # <Code here>
