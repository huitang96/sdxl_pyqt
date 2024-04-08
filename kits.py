import configparser
def read_config_paths(config_filename):
    config = configparser.ConfigParser()
    config.read(config_filename, encoding='utf-8')

    workspace_section = config['WorkSpace']

    root_path = workspace_section.get('root')
    model_path = workspace_section.get('model_path')

    return root_path, model_path