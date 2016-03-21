import yaml


class Config(object):
    pass


def filename_to_raw_dict(filename):
    return yaml.load(open(filename))


def process_raw_config_file(filename):
    raw_config = filename_to_raw_dict(filename)
    return process_raw_config(raw_config)


def process_raw_config(raw_config):
    resp = Config()
    resp.media_directory = raw_config['media directory']
    resp.entity = raw_config['who am i']
    resp.num_spots = raw_config['spot count']
    resp.graphic = raw_config['graphic']
    resp.file_config = _process_file_config(raw_config['menus'])
    resp.menu_config = _process_menu_config(raw_config['menus'])

    return resp


def _process_file_config(raw_menu_config):
    return {_prefix_from_file_format(x['file format']):
            x['file format']
            for x in raw_menu_config}


def _prefix_from_file_format(file_format):
    return file_format.split('_', 1)[0]


class MenuConfig(object):

    pass

def _process_menu_config(raw_menu_config):
    resp = {}
    for x in raw_menu_config:
        resp[_prefix_from_file_format(x['file format'])] = x['headers']
    m = MenuConfig()
    m.headers = resp
    m.order = [_prefix_from_file_format(x['file format']) for x in raw_menu_config]
    return m
