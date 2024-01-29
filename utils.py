import json

def load_config():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def map_value(x, in_min, in_max, out_min, out_max):
    return max(out_min, min(out_max, (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min))