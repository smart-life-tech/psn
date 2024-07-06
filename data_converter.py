import json

class DataConverter:
    def __init__(self, config_file):
        self.config_file = config_file
        self.mappings = []
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            self.mappings = config.get('mappings', [])

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'mappings': self.mappings}, f)

    def add_mapping(self, psn_field, sacn_universe, sacn_address, osc_ip, osc_port, osc_address, scale):
        self.mappings.append({
            'psn_field': psn_field,
            'sacn_universe': sacn_universe,
            'sacn_address': sacn_address,
            'osc_ip': osc_ip,
            'osc_port': osc_port,
            'osc_address': osc_address,
            'scale': scale
        })
        self.save_config()

    def convert_data(self, psn_data):
        # Implement the conversion logic
        pass

    def stop(self):
        # Implement stopping logic if needed
        pass
