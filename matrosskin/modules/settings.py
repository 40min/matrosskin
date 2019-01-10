import os
import yaml

config = dict()
config_file = os.environ.get('CONFIG_FILE', 'config.yaml')
if os.path.exists(config_file):
    with open(config_file, 'r') as stream:
        config = yaml.load(stream)
