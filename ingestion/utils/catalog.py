import yaml
from utils.dataset import Dataset


def load_catalog(config_path="config/catalog.yml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    catalog = {}
    for name, params in cfg.items():
        catalog[name] = Dataset(name, **params)
    return catalog


catalog = load_catalog()
