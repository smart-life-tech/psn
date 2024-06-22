# data_converter.py
import sacn
import osc4py3.as_eventloop as osc_eventloop
import osc4py3.oscbuildparse as osc_parse
from osc4py3.as_eventloop import osc_startup, osc_send, osc_terminate
class DataConverter:
    def __init__(self):
        self.sacn_sender = sacn.sACNsender()
        self.sacn_sender.start()
        self.sacn_sender.start()
        osc_startup()
        self.mappings = []
    
    def add_mapping(self, psn_field, sacn_universe, sacn_address, osc_ip, osc_port, osc_address, scale):
        mapping = {
            'psn_field': psn_field,
            'sacn_universe': sacn_universe,
            'sacn_address': sacn_address,
            'osc_ip': osc_ip,
            'osc_port': osc_port,
            'osc_address': osc_address,
            'scale': scale
        }
        self.mappings.append(mapping)
    
    def convert_data(self, psn_data):
        for mapping in self.mappings:
            field_data = psn_data[mapping['psn_field']]
            scaled_data = tuple(x * mapping['scale'] for x in field_data)
            self.convert_to_sacn(scaled_data, mapping['sacn_universe'], mapping['sacn_address'])
            self.convert_to_osc(scaled_data, mapping['osc_ip'], mapping['osc_port'], mapping['osc_address'])
    
    def convert_to_sacn(self, data, universe, address):
        self.sacn_sender[universe].dmx_data[address:address+len(data)] = data
        self.sacn_sender[universe].multicast = True
    
    def convert_to_osc(self, data, ip, port, address):
        msg = osc_parse.OSCMessage(address, None, list(data))
        osc_eventloop.osc_send(msg, ip, port)
    
    def stop(self):
        self.sacn_sender.stop()
        osc_eventloop.shutdown()
