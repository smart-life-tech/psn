import json
import socket
import struct
import sacn
#from pythonosc.udp_client import SimpleUDPClient
from osc4py3.as_eventloop import osc_udp_client, osc_send ,osc_terminate
from osc4py3 import oscsender
from threading import Thread

class DataConverter:
    def __init__(self, mappings_file):
        self.load_mappings(mappings_file)
        self.init_sacn_sender()
        self.init_osc_sender()

    def load_mappings(self, mappings_file):
        with open(mappings_file, 'r') as f:
            self.mappings = json.load(f)

    def init_sacn_sender(self):
        self.sacn_sender = sacn.sACNsender()
        self.sacn_sender.start()

        for mapping in self.mappings:
            universe = mapping['sacn_universe']
            self.sacn_sender.activate_output(universe)
            self.sacn_sender[universe].multicast = True

    def init_osc_sender(self):
        self.osc_clients = {}
        for mapping in self.mappings:
            osc_ip = mapping['osc_ip']
            osc_port = mapping['osc_port']
            self.osc_clients[mapping['osc_address']] = osc_udp_client(osc_ip, osc_port, mapping['osc_address'])

    def scale_data(self, data, scale):
        return [x * scale for x in data]

    def convert_to_sacn(self, data, universe, address):
        self.sacn_sender[universe].dmx_data[address:address + len(data)] = data

    def convert_to_osc(self, data, address):
        osc_send(self.osc_clients[address], data)

    def convert_data(self, psn_data):
        tracker_id, position_data, speed_data, orientation_data = psn_data
        for mapping in self.mappings:
            if mapping['tracker_id'] == tracker_id:
                if 'position' in mapping['psn_data_type']:
                    scaled_data = self.scale_data(position_data, mapping['scale'])
                    self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])
                    self.convert_to_osc(scaled_data, mapping['osc_address'])
                elif 'speed' in mapping['psn_data_type']:
                    scaled_data = self.scale_data(speed_data, mapping['scale'])
                    self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])
                    self.convert_to_osc(scaled_data, mapping['osc_address'])
                elif 'orientation' in mapping['psn_data_type']:
                    scaled_data = self.scale_data(orientation_data, mapping['scale'])
                    self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])
                    self.convert_to_osc(scaled_data, mapping['osc_address'])

def run():
    psn_data = (1, [47.8955, 0, 0], [0, 0, 0], [0, 0, 0])  # Sample data for testing
    data_converter.convert_data(psn_data)

if __name__ == "__main__":
    CONFIG_FILE = "config.json"
    data_converter = DataConverter(CONFIG_FILE)

    try:
        thread = Thread(target=run)
        thread.start()
    except KeyboardInterrupt:
        osc_terminate()
        #sacn_sender.stop()
