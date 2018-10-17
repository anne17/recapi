import yaml


def load_data(yamlfile):
    with open(yamlfile) as f:
        return yaml.load(f)
