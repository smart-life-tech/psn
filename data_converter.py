import json
import sacn
import pypsn
from pythonosc.udp_client import SimpleUDPClient

class DataConverter:
    def __init__(self, config_file):
        self.config_file = config_file
        self.sender = sacn.sACNsender()
        self.osc_clients = {}
        self.mappings = []
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            for mapping in config['mappings']:
                self.add_mapping(
                    mapping['psn_field'],
                    mapping['sacn_universe'],
                    mapping['sacn_address'],
                    mapping['osc_ip'],
                    mapping['osc_port'],
                    mapping['osc_address'],
                    mapping['scale']
                )

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
        if osc_ip not in self.osc_clients:
            self.osc_clients[osc_ip] = SimpleUDPClient(osc_ip, osc_port)

    def convert_data(self, psn_data):
        print(psn_data)
        for tracker_id, data in psn_data.items():
            for mapping in self.mappings:
                value = getattr(data['position'], mapping['psn_field'], None)
                if value is not None:
                    scaled_value = int(value * mapping['scale'])
                    print(f"Sending {value} to {mapping['osc_ip']}:{mapping['osc_port']} {mapping['osc_address']}")
                    self.send_dmx(mapping['sacn_universe'], mapping['sacn_address'], scaled_value)
                    self.send_osc(mapping['osc_ip'], mapping['osc_address'], scaled_value)

    def send_dmx(self, universe, address, value):
        self.sender.activate_output(universe)
        self.sender[universe].multicast = True
        dmx_data = [0] * 512
        dmx_data[address] = value
        self.sender[universe].dmx_data = dmx_data

    def send_osc(self, ip, address, value):
        if ip in self.osc_clients:
            self.osc_clients[ip].send_message(address, value)

    def stop(self):
        self.sender.stop()
