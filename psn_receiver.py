# psn_receiver.py
import socket
import struct

class PSNReceiver:
    def __init__(self, ip='0.0.0.0', port=56565):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
    
    def receive_data(self):
        data, _ = self.sock.recvfrom(1024)
        tracker_id, pos_x, pos_y, pos_z = struct.unpack('!Ifff', data[:16])
        speed_x, speed_y, speed_z = struct.unpack('!fff', data[16:28])
        orient_x, orient_y, orient_z = struct.unpack('!fff', data[28:40])
        
        position_data = [pos_x, pos_y, pos_z]
        speed_data = [speed_x, speed_y, speed_z]
        orientation_data = [orient_x, orient_y, orient_z]
        
        return tracker_id, position_data, speed_data, orientation_data
