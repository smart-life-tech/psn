import struct
import sacn
from pythonosc.udp_client import SimpleUDPClient
import json
class DataConverter:
    def __init__(self, mappings_file):
        self.sacn_sender = sacn.sACNsender()
        self.osc_clients = {}
        self.load_mappings(mappings_file)
        self.init_sacn_sender()
        self.init_osc_sender()

    def load_mappings(self, mappings_file):
        with open(mappings_file, 'r') as f:
            self.mappings = json.load(f)

    def init_sacn_sender(self):
        for mapping in self.mappings:
            universe = mapping['sacn_universe']
            self.sacn_sender.activate_output(universe)
            self.sacn_sender[universe].multicast = True

    def init_osc_sender(self):
        for mapping in self.mappings:
            osc_ip = mapping['osc_ip']
            osc_port = mapping['osc_port']
            osc_address = mapping['osc_address']
            self.osc_clients[osc_address] = SimpleUDPClient(osc_ip, osc_port)

    def convert_data(self, tracker_data):
        tracker_id = tracker_data['id']
        for mapping in self.mappings:
            if mapping['tracker_id'] == tracker_id:
                data_type = mapping['psn_data_type']
                scale = mapping['scale']
                data = [value * scale for value in tracker_data[data_type]]
                self.convert_to_sacn(data, mapping['sacn_universe'], mapping['sacn_address'])
                self.convert_to_osc(data, mapping['osc_address'])

    def convert_to_sacn(self, data, universe, address):
        self.sacn_sender[universe].dmx_data[address:address+len(data)] = data

    def convert_to_osc(self, data, address):
        self.osc_clients[address].send_message(address, data)

    def stop(self):
        self.sacn_sender.stop()
        for client in self.osc_clients.values():
            client.close()
