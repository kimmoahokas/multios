from multios.base.exceptions import ConfigFileError

__author__ = 'Kimmo Ahokas'

import json

from multios.base.os_instance import OpenStackInstance


def load_config_file(file_name):
    config = {'instances': []}
    data = None
    with open(file_name, mode='r') as fp:
        data = json.load(fp)

    if data is None:
        raise ConfigFileError('Unable to read config file!')

    if data and 'instances' in data:
        for instance_params in data['instances']:
            instance = OpenStackInstance.create_from_config(instance_params)
            #instance.print_info()
            config['instances'].append(instance)

    return config

