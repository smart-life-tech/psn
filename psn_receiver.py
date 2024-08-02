import sacn
import pypsn
import os
import json
from data_converter import DataConverter
CONFIG_FILE = 'config.json'
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'psn_ip': '0.0.0.0',
        'psn_port': 56565,
        'psn_multicast_ip': '236.10.10.10',
        'mappings': []
    }
config = load_config()
data_converter = DataConverter(CONFIG_FILE)
toggle = False
# Simple forwarder of PSN to DMX. Turns all coordinates to positive ints...
class PSNReceiver:
    def __init__(self):
        self.sender = sacn.sACNsender()
        self.x=0
        self.y=0
        self.z=0
        self.id=1

    def start_dmx(self):
        self.sender.start()  # start the sending thread
        self.sender.activate_output(1)  # start sending out data in the 1st universe
        self.sender[1].multicast = True  # set multicast to True

    def stop_dmx(self):
        self.sender.stop()  # do not forget to stop the sender

    def start_psn(self):
        pypsn.receiver(self.fill_dmx, "0.0.0.0").start()
    def stop_psn(self):
        pypsn.receiver(self.fill_dmx).stop()

    def receive_data(self):
        # Here you would implement the logic to receive and parse the PSN data to be tested
        # This is a placeholder implementation and should be replaced with actual logic
        #return self.id,self.x, self.y, self.z i already removed the x y and z data from the tracker postions
        tracker_id = 1  # replace with actual tracker_id extraction logic
        position_data = self.x
        speed_data = self.y
        orientation_data = self.z
        return tracker_id, {'position': position_data, 'speed': speed_data, 'orientation': orientation_data}
        
    
    def fill_dmx(self, psn_data):
        global toggle
        pos=[0]*512
        if isinstance(psn_data, pypsn.psn_data_packet):
            position = psn_data.trackers[0].pos
            
            #position3 = psn_data.trackers[2].pos
            dmx_data = [0] * 512
            dmx_data[0] = int(abs(position.x))
            dmx_data[1] = int(abs(position.y))
            dmx_data[2] = int(abs(position.z))
            print(position)
            speed = psn_data.trackers[0].speed
            status = psn_data.trackers[0].status
            timestamp = psn_data.trackers[0].timestamp
            trgpos = psn_data.trackers[0].info
            if position.x > 0:
                dmx_data[0] = 512 - int(abs(position.x))
                #print("x position", position.x)
                self.x = position.x
                print("x position : ",position.x)
                print("y position : ",position.y)
                print("z position : ",position.z)
                
                # print("x position data3====== : ", position3.x)
                # print("y position data3====== : ", position3.y)
                # print("z position data3====== : ", position3.z)
            toggle=False
            position2 = psn_data.trackers[1].pos
            if position2.y > 0:
                dmx_data[1] = 512 - int(abs(position.y))
                #print("y postion data====== : ", position2.y)
                self.y = position2.y
                print("x position data2====== : ", position2.x)
                print("y position data2====== : ", position2.y)
                print("z position data2====== : ", position2.z)
                toggle=True
                # print("x postion data====== : ",position2.x)
            position3 = psn_data.trackers[2].pos
            if position3.z >= 0:
                dmx_data[2] = 512 - int(abs(position.z))
                print(position3.z)
                print("x position data3====== : ", position3.x)
                print("y position data3====== : ", position3.y)
                print("z position data3====== : ", position3.z)
                self.z = position3.z
                print("postion1 : ",position)
                print("postion2 : ",position2)
                print("postion3 : ",position3)
                print("speed :" ,speed)
                print("status :" ,status)
                print("timestamp :" ,timestamp)
                print("trgpos :" ,trgpos)
            # sender[1].dmx_data = dmx_data
        # except Exception as e:
        #     print(e)
        #     print("Error in fill_dmx")
            #pass
            

if __name__ == "__main__":
    psn_receiver = PSNReceiver()
    print("Starting...")
    psn_receiver.start_dmx()
    psn_receiver.start_psn()
