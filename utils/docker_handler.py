
from pathlib import Path

import logging
import docker
import requests



class DokerHandler:
    """
    Helper class for managing docker related elements
    """

    def get_images_list(repository_name=''):
        """
        docstring
        """
        # curl --unix-socket /var/run/docker.sock http://localhost/images/json
        client = docker.from_env()
        if not repository_name:
            images_list = client.images.list(all=True)
        else:
            images_list = client.images.list(name=repository_name)
        return images_list


    @classmethod
    def get_latest_image_shasum(cls, repository_name=''):
        client = docker.from_env()
        latest_str = f'{repository_name}:latest'
        images_list = cls.get_images_list(latest_str)
        if not images_list:
            raise Exception(f'was not able to find latest image for repository: {repository_name}')
        latest_image = images_list.pop()
        return latest_image.id


    def get_container_image_shasum(container_name):
        client = docker.from_env()


    def get_containers_list(image_name=''):
        """
        docstring
        """
        client = docker.from_env()
        if not image_name:
            containers_list = client.containers.list(all=True)
        else:
            containers_list = client.containers.list(filters={'ancestor':image_name})
        return containers_list


    @classmethod
    def rebuild_image_from_docker_file(cls, app_config):
        # future imporvement -> watch over files in src dir -> on file change, hot reload image
        docker_file_path = app_config.get('dockerfile_path')
        new_tag = app_config.get('tested_resource_name')
        path_obj = Path(docker_file_path)
        print(f'building new image from docker file, using dockerfile path: {docker_file_path}')
        containing_dir_path_str = str(path_obj.parent.absolute())
        docker_file_path_abs_str = str(path_obj.absolute())
        print(f'containing dir abs path: {containing_dir_path_str}')
        client = docker.from_env()
        new_image_tupple = client.images.build(path=containing_dir_path_str, tag=new_tag)
        if new_image_tupple:
            image_obj = new_image_tupple[0]
            image_latest_tag_str = image_obj.tags.pop()
        else:
            raise Exception(f'failed to create new image from: {docker_file_path}')
        new_image_shasum = cls.get_latest_image_shasum(new_tag)
        print(f'Success, created:{image_latest_tag_str} with id: {new_image_shasum}')


    @classmethod
    def start_container(cls, app_config):
        """
        docstring
        """
        client = docker.from_env()
        image_name = app_config.get('tested_resource_name')
        dockerfile_path = app_config.get('dockerfile_path')
        exposed_port_number = app_config.get('exposed_ports')
        ports_dict = {
            f'{exposed_port_number}/tcp': ('127.0.0.1', exposed_port_number)
        }
        logging.info(f'Spinning a new container from: {image_name}')
        if not image_name:
            raise Exception('please provide image nage to init container from')
        images_list = client.images.list(name=image_name)
        if not images_list:
            logging.info(f'building new image based on dockerfile: {dockerfile_path}')
            cls.rebuild_image_from_docker_file(app_config)
        try:
            a_new_container_obj = client.containers.run(image_name, detach=True,
                ports=ports_dict)
        except requests.exceptions.HTTPError as ex:
            if 'failed: port is already allocated' in str(ex):
                logging.error('Please stop previous instances')
            raise ex
        return a_new_container_obj


    def stop_container(container_name='', image_name=''):
        """
        docstring
        """
        client = docker.from_env()
        if image_name:
            logging.info(f'selecting ancestors for image: {image_name}')
            containers_list = client.containers.list(filters={'ancestor':image_name})
        if container_name:
            containers_list = [client.containers.get(container_name)]
        if not container_name and not image_name:
            raise Exception('please provide either image_name or container name to stop')
        logging.info(f'attempting to stop: {len(containers_list)} containers')
        for container_obj in containers_list:
            logging.info(f'Stopping a running container with name: {container_obj.name}')
            container_obj.stop()
            logging.info(f'Stopped {container_obj.name}.')


    def rm_containers(app_config):
        client = docker.from_env()
        image_name = app_config.get('tested_resource_name')
        containers_list = client.containers.list(all=True, filters={'ancestor':image_name})
        logging.info(f'Deleting: {len(containers_list)} containers')
        for container_obj in containers_list:
            logging.info(f'Deleting: {container_obj}')
            container_obj.remove()
        logging.info(f'finished cleanup of total: {len(containers_list)} containers')


    def rm_images(app_config):
        # optional -> can be also more dangarouse command
        raise NotImplemented

    @classmethod
    def cleanup(cls, app_config):
        """
        A wrapper method to control the level of wanted cleanup,
        potentional for example
            * rm containers
            * rm images
            * rm stale elements -> images and containers with older sha
        """
        cls.rm_containers(app_config)