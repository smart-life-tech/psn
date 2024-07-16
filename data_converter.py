import json
import sacn
import pypsn
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import udp_client
sender = sacn.sACNsender()  # provide an IP-Address to bind to if you want to send multicast packets from a specific interface
sender.start()  # start the sending thread
sender.activate_output(1)  # start sending out data in the 1st universe
sender[1].multicast = True  # set multicast to True
class DataConverter:
    def __init__(self, config_file):
        self.config_file = config_file
        self.sender = sacn.sACNsender()
        self.osc_clients = {}
        self.mappings = []
        self.load_config()
        self.x=0
        self.y=0
        self.z=0
        self.mindmx=0
        self.maxdmx=0
        self.minpsn=0
        self.maxpsn=0
        

    def load_config(self):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            #print(config['mappings'])
            for mapping in config['mappings']:
                if mapping['type'] == 'sacn':
                    self.add_sacn_mapping(
                    mapping['type'],
                    mapping['psn_source'],
                    mapping['server_name'],
                    mapping['tracker_id'],
                    mapping['tracker_name'],
                    mapping['axis'],
                    mapping['psn_min'],
                    mapping['psn_max'],
                    mapping.get('dmx_min', None),
                    mapping.get('dmx_max', None),
                    mapping.get('sacn_universe', None),
                    mapping.get('sacn_addr', None),  
                )
                elif mapping['type'] == 'osc':
                    self.add_osc_mapping(
                    mapping['type'],
                    mapping['psn_source'],
                    mapping['server_name'],
                    mapping['tracker_id'],
                    mapping['tracker_name'],
                    mapping['axis'],
                    mapping['psn_min'],
                    mapping['psn_max'],
                    mapping.get('osc_min', None),
                    mapping.get('osc_max', None),
                    mapping.get('osc_addr', None),
                )

    def add_osc_mapping(self, type ,psn_source, server_name, tracker_id, tracker_name, axis, psn_min, psn_max, osc_min=None, osc_max=None, osc_addr=None):
        mapping = {
            'type': type,
            'psn_source': psn_source,
            'server_name': server_name,
            'tracker_id': tracker_id,
            'tracker_name': tracker_name,
            'axis': axis,
            'psn_min': psn_min,
            'psn_max': psn_max,
            'osc_min': osc_min,
            'osc_max': osc_max,
            'osc_addr': osc_addr
        }
        self.mappings.append(mapping)
    def add_sacn_mapping(self, type ,psn_source, server_name, tracker_id, tracker_name, axis, psn_min, psn_max, dmx_min=None, dmx_max=None, sacn_universe=None, sacn_addr=None):
        mapping = {
            'type': type,
            'psn_source': psn_source,
            'server_name': server_name,
            'tracker_id': tracker_id,
            'tracker_name': tracker_name,
            'axis': axis,
            'psn_min': psn_min,
            'psn_max': psn_max,
            'dmx_min': dmx_min,
            'dmx_max': dmx_max,
            'sacn_universe': sacn_universe,
            'sacn_addr': sacn_addr
        }
        self.mappings.append(mapping)
        

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({"mappings": self.mappings}, f)
            
    def remove_mapping(self, index):
        if 0 <= index < len(self.mappings):
            self.mappings.pop(index)
    def convert_data(self, psn_data):
        for tracker_id, data in psn_data.items():
            self.x=data['position']
            self.y=data['speed']
            self.z=data['orientation']
            #print(f"Data: {data}")
            for mapping in self.mappings:
                if 1: 
                    #psn_data_type = mapping['psn_data_type']
                    value = ( mapping['type'])
                    print(f"Value: {value}")
                    if value is not None:
                        if value=='osc':
                            print(f"OSC: {mapping}")
                            self.minpsn=mapping['psn_min']
                            self.maxpsn=mapping['psn_max']
                            
                            
                            axis_value = mapping['axis'].upper()
                            print(f"axis Value: {axis_value}")
                            if axis_value == 'X':
                                self.x = self.scale_value(self.x, mapping['psn_min'], mapping['psn_max'], mapping['osc_min'], mapping['osc_max'])
                                self.send_osc(mapping['osc_addr'], self.x ,mapping['tracker_name'])
                            elif axis_value=='Y':
                                self.y = self.scale_value(self.y, mapping['psn_min'], mapping['psn_max'], mapping['osc_min'], mapping['osc_max'])
                                self.send_osc(mapping['osc_addr'], self.y,mapping['tracker_name'] )
                            elif axis_value=='Z':
                                self.z = self.scale_value(self.z, mapping['psn_min'], mapping['psn_max'], mapping['osc_min'], mapping['osc_max'])
                                self.send_osc(mapping['osc_addr'], self.z,mapping['tracker_name'] )
                        elif value=='sacn':
                            self.mindmx=mapping['dmx_min']
                            self.maxdmx=mapping['dmx_max']
                            axis_value = psn_data[tracker_id].get(mapping['axis'], 0)
                            scaled_value = self.scale_value(axis_value, mapping['psn_min'], mapping['psn_max'], mapping['dmx_min'], mapping['dmx_max'])
                            self.send_dmx(mapping['sacn_universe'], mapping['sacn_addr'], mapping['axis'])
                        #================================================================#
                        if tracker_id in psn_data:
                            axis_value = psn_data[tracker_id].get(mapping['axis'], 0)
                            if mapping['type'] == 'osc':
                                output_value = self.scale_value(axis_value, mapping['psn_min'], mapping['psn_max'], mapping['osc_min'], mapping['osc_max'])
                                #self.send_osc(mapping['osc_addr'], output_value, mapping['server_name'])
                            elif mapping['type'] == 'sacn':
                                output_value = self.scale_value(axis_value, mapping['psn_min'], mapping['psn_max'], mapping['dmx_min'], mapping['dmx_max'])
                                #self.send_dmx(mapping['sacn_universe'], mapping['sacn_addr'], output_value)
                    else:
                        print(f"Field   not found in data: {data}")
                else:
                    print(f"Tracker ID '{tracker_id}' does not match mapping tracker ID '{mapping['tracker_id']}'")

    def scale_value(self, value, input_min, input_max, output_min, output_max):
        input_range = input_max - input_min
        output_range = output_max - output_min
        scaled_value = (((value - input_min) * output_range) / input_range) + output_min
        return scaled_value
    
    def send_dmx(self, universe, address, value):
        self.sender.activate_output(universe)
        self.sender[universe].multicast = True
        value=value.upper()
        dmx_data = [0] * 512
        if 1:
            #dmx_data[address] = value if 0 <= value < 256 else 0  # Ensure value is a valid byte
            #self.sender[universe].dmx_data = dmx_data
            #dmx_data[address] = value
            #self.sender[universe].dmx_data = dmx_data
            #dmx_data = [1] * 512
            dmx_data[0] =  self.x
            dmx_data[1] = self.y
            dmx_data[2] = self.z
            #print(f"DMX Data: {dmx_data}")
            #self.sender[universe].dmx_data = dmx_data
            #self.sender[universe].dmx_data = ( int(value) )
            # print("before mapping output x",self.x)
            # print("before mapping output y",self.y)
            # print("before mapping output z",self.z)
        
            # print("after mapping output x",outputx)
            # print("after mapping output y",outputy)
            # print("after mapping output z",outputz)
            if value == 'X':
                outputx = self.scale_value(self.x, self.minpsn, self.maxpsn, self.mindmx,self.maxdmx)
                print("after mapping output x",outputx)
                sender[universe].dmx_data = (int(outputx),)
            elif value == 'Y':
                outputy = self.scale_value(self.y, self.minpsn, self.maxpsn, self.mindmx,self.maxdmx)
                sender[universe].dmx_data = (0,int(outputy),)
            elif value == 'Z':
                outputz = self.scale_value(self.z, self.minpsn, self.maxpsn, self.mindmx,self.maxdmx)
                sender[universe].dmx_data = (0,0,int(outputz),)
            #sender[universe].dmx_data = (int(outputx), int(outputy), int(outputz), 4)  # some test DMX data
            

    def send_osc(self,  address, value,ip):
        client = udp_client.SimpleUDPClient(address, 5005) 
        print("address : ",address)
        client.send_message(ip, value)
        #print("address : ",address)
        #if ip in self.osc_clients:
            #self.osc_clients[ip].send_message(address, value)

    def stop(self):
        self.sender.stop()
