import json
from sacn import sACNsender
from pythonosc.udp_client import SimpleUDPClient

class DataConverter:
    def __init__(self, mappings):
        self.mappings = mappings
        self.sacn_sender = sACNsender()
        self.sacn_sender.start()
        self.osc_clients = {}
        self.init_osc_sender()

    def init_osc_sender(self):
        for mapping in self.mappings:
            osc_ip = mapping['osc_ip']
            osc_port = mapping['osc_port']
            osc_address = mapping['osc_address']
            if osc_address not in self.osc_clients:
                self.osc_clients[osc_address] = SimpleUDPClient(osc_ip, osc_port)

    def convert_data(self, psn_data):
        tracker_id, position_data, speed_data, orientation_data = psn_data
        for mapping in self.mappings:
            if mapping['tracker_id'] == tracker_id:
                if mapping['psn_data_type'] == 'position':
                    data = position_data
                elif mapping['psn_data_type'] == 'speed':
                    data = speed_data
                elif mapping['psn_data_type'] == 'orientation':
                    data = orientation_data
                else:
                    continue

                scaled_data = [x * mapping['scale'] for x in data]

                # Send to sACN
                self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])

                # Send to OSC
                self.convert_to_osc(scaled_data, mapping['osc_address'])

    def convert_to_sacn(self, data, universe, address):
        self.sacn_sender[universe].dmx_data[address:address+len(data)] = data

    def convert_to_osc(self, data, address):
        client = self.osc_clients[address]
        client.send_message(address, data)

    def stop(self):
        self.sacn_sender.stop()
