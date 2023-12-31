import logging


class ConfigHandler:
    def get_config_from_dockerfile(dockerfile_path='', silent=False):
        DEFAULT_DOCKERFILE_PATH = './Dockerfile'
        DEFAULT_ARG_DESCRIPTOR_NAME = 'APP_NAME'    # how we tag the tested resource
        DEFAULT_ARG_DESCRIPTOR_TESTED_API = 'TESTED_APIS_LIST'
        if not dockerfile_path:
            logging.info(f'setting default docker file path of: {DEFAULT_DOCKERFILE_PATH}')
            dockerfile_path = DEFAULT_DOCKERFILE_PATH
        app_config_dict = {
            'tested_resource_name':'',
            'exposed_ports': '',
            'resource_cmd': '',
            'tested_apis_list':'',
            'dockerfile_path': ''
        }
        properties_list = [
            (f'ARG {DEFAULT_ARG_DESCRIPTOR_NAME}', 'tested_resource_name'),
            (f'ARG {DEFAULT_ARG_DESCRIPTOR_TESTED_API}', 'tested_apis_list'),
            ('EXPOSE', 'exposed_ports'),
            ('CMD','resource_cmd')
        ]
        
        with open(dockerfile_path) as f:
            dockerfile_lines_list = f.readlines()
            logging.info(f'parsing dockerfile of [{len(dockerfile_lines_list)}] lines')
            for line_number, line_str in enumerate(dockerfile_lines_list):
                lines_stripped_str = line_str.strip()
                if not silent:
                    logging.info(f'{line_number: <4} {lines_stripped_str}')
                if not lines_stripped_str:
                    continue    # skipping empty lines
                for property_tupple in properties_list:
                    key_str = property_tupple[0]
                    config_field_key = property_tupple[1]
                    if lines_stripped_str.startswith(key_str):
                        logging.info(f'--> found expected item: {key_str} -> {lines_stripped_str}')
                        prefix_chars_number = len(key_str)+1
                        config_value = lines_stripped_str[prefix_chars_number:]
                        app_config_dict[config_field_key] = config_value
                        if DEFAULT_ARG_DESCRIPTOR_TESTED_API in key_str:
                            # dynamically handle each occurance of re-formatting ARG from dockerfile
                            logging.info('Splitting tested APIs into list - expected comma seperated')
                            app_config_dict[config_field_key] = config_value.split(',')
        app_config_dict['dockerfile_path'] = dockerfile_path
        return app_config_dict