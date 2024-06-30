import json
from pythonosc.udp_client import SimpleUDPClient
import sacn

class DataConverter:
    def __init__(self, config_file):
        self.mappings = []
        self.load_config(config_file)
        self.osc_clients = {}
        self.sacn_sender = sacn.sACNsender()
        self.sacn_sender.start()
        self.init_osc_clients()
        self.init_sacn_universes()

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            self.mappings = config.get('mappings', [])

    def init_osc_clients(self):
        print(self.mappings)
        for mapping in self.mappings:
            osc_ip = mapping.get('osc_ip')
            osc_port = mapping.get('osc_port')
            if (osc_ip, osc_port) not in self.osc_clients:
                self.osc_clients[(osc_ip, osc_port)] = SimpleUDPClient(osc_ip, osc_port)

    def init_sacn_universes(self):
        for mapping in self.mappings:
            universe = mapping['sacn_universe']
            if universe not in self.sacn_sender._outputs:
                self.sacn_sender.activate_output(universe)
                self.sacn_sender[universe].multicast = True

    def convert_data(self, psn_data):
        for mapping in self.mappings:
            tracker_id = mapping['tracker_id']
            if tracker_id in psn_data and mapping['psn_data_type'] in psn_data[tracker_id]:
                scaled_data = self.scale_data(psn_data[tracker_id][mapping['psn_data_type']], mapping['scale'])
                self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])
                self.convert_to_osc(scaled_data, mapping['osc_address'], mapping['osc_ip'], mapping['osc_port'])

    def scale_data(self, data, scale):
        return [d * scale for d in data]

    def convert_to_sacn(self, data, universe, address):
        self.sacn_sender[universe].dmx_data[address:address+len(data)] = data

    def convert_to_osc(self, data, address, osc_ip, osc_port):
        client = self.osc_clients[(osc_ip, osc_port)]
        client.send_message(address, data)

    def stop(self):
        self.sacn_sender.stop()