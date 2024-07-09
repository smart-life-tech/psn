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
            for mapping in config['mappings']:
                self.add_mapping(
                    mapping['type'],
                    mapping.get('osc_ip',None),
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
                    mapping.get('dmx_min', None),
                    mapping.get('dmx_max', None),
                    mapping.get('sacn_universe', None),
                    mapping.get('sacn_addr', None),
                    
                )

    def add_mapping(self, mapping_type,osc_ip, psn_source, server_name, tracker_id, tracker_name, axis, psn_min, psn_max, osc_min=None, osc_max=None, osc_addr=None, dmx_min=None, dmx_max=None, sacn_universe=None, sacn_addr=None):
        mapping = {
            'type': mapping_type,
            'psn_source': psn_source,
            'server_name': server_name,
            'tracker_id': tracker_id,
            'tracker_name': tracker_name,
            'axis': axis,
            'psn_min': psn_min,
            'psn_max': psn_max,
            'osc_min': osc_min,
            'osc_max': osc_max,
            'osc_addr': osc_addr,
            'dmx_min': dmx_min,
            'dmx_max': dmx_max,
            'sacn_universe': sacn_universe,
            'sacn_addr': sacn_addr,
            'osc_ip':osc_ip
        }
        self.mappings.append(mapping)
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({"mappings": self.mappings}, f)

    def convert_data(self, psn_data):
        for tracker_id, data in psn_data.items():
            #print(f"Tracker ID: {tracker_id}")
            self.x=data['position']
            self.y=data['speed']
            self.z=data['orientation']
            print(f"Data: {data}")
            for mapping in self.mappings:
                if mapping['tracker_id'] == tracker_id: 
                    #psn_data_type = mapping['psn_data_type']
                    value = 1#data.get(psn_data_type, None)
                    if value is not None:
                        self.minpsn=mapping['psn_min']
                        self.maxpsn=mapping['psn_max']
                        self.mindmx=mapping['dmx_min']
                        self.maxdmx=mapping['dmx_max']
                        
                        axis_value = psn_data[tracker_id].get(mapping['axis'], 0)
                        scaled_value = self.scale_value(axis_value, mapping['psn_min'], mapping['psn_max'], mapping['osc_min'], mapping['osc_max'])
                        self.send_dmx(mapping['sacn_universe'], mapping['sacn_addr'], scaled_value)
                        self.send_osc(mapping['osc_ip'], self.x ,mapping['axis'])
                        self.send_osc(mapping['osc_ip'], self.y,mapping['axis'] )
                        self.send_osc(mapping['osc_ip'], self.z,mapping['axis'] )
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
        dmx_data = [0] * 512
        if 0 <= address < 512:
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
            outputx = self.scale_value(self.x, self.minpsn, self.maxpsn, self.mindmx,self.maxdmx)
            outputy = self.scale_value(self.y, self.minpsn, self.maxpsn, self.mindmx,self.maxdmx)
            outputz = self.scale_value(self.z, self.minpsn, self.maxpsn, self.mindmx,self.maxdmx)
            sender[universe].dmx_data = (int(outputx), int(outputy), int(outputz), 4)  # some test DMX data


    def send_osc(self,  address, value,ip):
        client = udp_client.SimpleUDPClient("192.168.0.202", 5005) 
        print("ip : ",ip)
        client.send_message(address, value)
        print("address : ",address)
        #if ip in self.osc_clients:
            #self.osc_clients[ip].send_message(address, value)

    def stop(self):
        self.sender.stop()
