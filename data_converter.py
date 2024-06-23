import sacn
import time
import json
from osc4py3.as_eventloop import osc_send, osc_startup, osc_udp_client, osc_terminate

class DataConverter:
    def __init__(self, mappings_file):
        self.load_mappings(mappings_file)
        self.sacn_sender = sacn.sACNsender(fps=30)
        self.sacn_sender.start()
        self.init_osc_sender()

    def load_mappings(self, mappings_file):
        with open(mappings_file, 'r') as file:
            self.mappings = json.load(file)

    def init_osc_sender(self):
        osc_startup()
        self.osc_clients = {}
        for mapping in self.mappings['mappings']:
            if 'osc_address' in mapping and mapping['osc_address'] not in self.osc_clients:
                osc_ip = mapping.get('osc_ip', '127.0.0.1')
                osc_port = mapping.get('osc_port', 8000)
                self.osc_clients[mapping['osc_address']] = osc_udp_client(osc_ip, osc_port,mapping['osc_address'])

    def convert_data(self, psn_data):
        print(psn_data)
        tracker_id, position_data, speed_data, orientation_data = psn_data

        for mapping in self.mappings['mappings']:
            if mapping['tracker_id'] == tracker_id:
                if mapping['data_type'] == 'position':
                    data = position_data
                elif mapping['data_type'] == 'speed':
                    data = speed_data
                elif mapping['data_type'] == 'orientation':
                    data = orientation_data
                else:
                    continue

                scaled_data = [x * mapping['scale'] for x in data]

                if 'sacn_universe' in mapping and 'sacn_address' in mapping:
                    self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])

                if 'osc_address' in mapping:
                    self.convert_to_osc(scaled_data, mapping['osc_address'])

    def convert_to_sacn(self, data, universe, address):
        self.init_sacn_universe(universe)
        self.sacn_sender[universe].dmx_data[address:address+len(data)] = data

    def init_sacn_universe(self, universe):
        if universe not in self.sacn_sender:
            self.sacn_sender.activate_output(universe)
            self.sacn_sender[universe].multicast = True

    def convert_to_osc(self, data, osc_address):
        if osc_address in self.osc_clients:
            osc_send(self.osc_clients[osc_address], osc_address, data)

    def stop(self):
        self.sacn_sender.stop()
        osc_terminate()
