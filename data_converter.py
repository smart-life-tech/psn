import json
import sacn
import pypsn
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import udp_client
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
                    mapping['tracker_id'],
                    mapping['psn_data_type'],
                    mapping['psn_field'],
                    mapping['sacn_universe'],
                    mapping['sacn_address'],
                    mapping['osc_ip'],
                    mapping['osc_port'],
                    mapping['osc_address'],
                    mapping['scale']
                )

    def add_mapping(self, tracker_id,psn_data_type,psn_field, sacn_universe, sacn_address, osc_ip, osc_port, osc_address, scale):
        self.mappings.append({
            'tracker_id':tracker_id,
            'psn_data_type':psn_data_type,
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
        for tracker_id, data in psn_data.items():
            #print(f"Tracker ID: {tracker_id}")
            print(f"Data: {data}")
            for mapping in self.mappings:
                if mapping['tracker_id'] == tracker_id:
                    psn_data_type = mapping['psn_data_type']
                    value = data.get(psn_data_type, None)
                    if value is not None:
                        scaled_value = int(value * mapping['scale'])
                        #print(f"Scaled Value: {scaled_value}")
                        self.send_dmx(mapping['sacn_universe'], mapping['sacn_address'], scaled_value)
                        self.send_osc(mapping['osc_ip'], mapping['osc_address'], psn_data)
                    else:
                        print(f"Field '{psn_data_type}' not found in data: {data}")
                else:
                    print(f"Tracker ID '{tracker_id}' does not match mapping tracker ID '{mapping['tracker_id']}'")

    def send_dmx(self, universe, address, value):
        self.sender.activate_output(universe)
        self.sender[universe].multicast = True
        dmx_data = [0] * 512
        if 0 <= address < 512:
            dmx_data[address] = value if 0 <= value < 256 else 0  # Ensure value is a valid byte
            self.sender[universe].dmx_data = dmx_data
        #dmx_data[address] = value
        #self.sender[universe].dmx_data = dmx_data

    def send_osc(self, ip, address, value):
        client = udp_client.SimpleUDPClient(ip, 5005)
        print(ip)
        client.send_message("/filter", value)
        print(value)
        if ip in self.osc_clients:
            self.osc_clients[ip].send_message(address, value)

    def stop(self):
        self.sender.stop()
