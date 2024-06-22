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
        # Example: Extracting position, speed, and orientation data
        tracker_id = struct.unpack('!H', data[10:12])[0]
        position_data = struct.unpack('!3f', data[20:32])  # X, Y, Z positions
        speed_data = struct.unpack('!3f', data[32:44])  # X, Y, Z speeds
        orientation_data = struct.unpack('!3f', data[44:56])  # Pitch, Yaw, Roll
        return tracker_id, position_data, speed_data, orientation_data
