import socket
import time
import struct

PSN_IP = '127.0.0.1'  # Use the IP address of your Raspberry Pi
PSN_PORT = 56565

def create_psn_packet(tracker_id, position, speed, orientation):
    # Construct a PSN packet (this is a simplified example, adjust according to the PSN spec)
    packet = struct.pack('!Ifff', tracker_id, *position)
    packet += struct.pack('!fff', *speed)
    packet += struct.pack('!fff', *orientation)
    return packet

def send_psn_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    tracker_id = 1
    position = [1.0, 2.0, 3.0]  # Example position data
    speed = [0.1, 0.2, 0.3]  # Example speed data
    orientation = [10.0, 20.0, 30.0]  # Example orientation data
    
    while True:
        packet = create_psn_packet(tracker_id, position, speed, orientation)
        sock.sendto(packet, (PSN_IP, PSN_PORT))
        time.sleep(0.016)  # Send data at approximately 60Hz

if __name__ == '__main__':
    send_psn_data()
