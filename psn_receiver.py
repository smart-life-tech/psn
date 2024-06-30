import socket
import struct
 

class PSNPacket:
    def __init__(self, data):
        # Parse the packet according to the PSN protocol
        # Assuming the packet structure is known and the data format is:
        # Tracker ID (int), Position (3 floats), Speed (3 floats), Orientation (3 floats)
        
        self.tracker_id, self.position, self.speed, self.orientation = self.parse_packet(data)
    
    def parse_packet(self, data):
        # Example parsing logic (replace with actual packet structure)
        tracker_id = struct.unpack_from('!I', data, 0)[0]
        position = struct.unpack_from('!fff', data, 4)
        speed = struct.unpack_from('!fff', data, 16)
        orientation = struct.unpack_from('!fff', data, 28)
        
        return tracker_id, position, speed, orientation
class PSNReceiver:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))

    def receive_data(self):
        data, addr = self.sock.recvfrom(1024)  # Buffer size is 1024 bytes
        psn_packet = PSNPacket(data)

        # Extract the necessary data from the PSN packet
        tracker_id = psn_packet.tracker_id
        position_data = psn_packet.position
        speed_data = psn_packet.speed
        orientation_data = psn_packet.orientation

        return tracker_id, position_data, speed_data, orientation_data

    def parse_psn_data(self, data):
        # Parse the data according to the provided PSN data structure
        chunk_id, data_length = struct.unpack_from('!HH', data, 0)
        if chunk_id == 0x6755:  # PSN_V2_DATA_PACKET
            header_id, header_length = struct.unpack_from('!HH', data, 4)
            timestamp, version_high, version_low, frame_id, frame_packet_count = struct.unpack_from('!IHHHH', data, 8)

            offset = 20
            tracker_list_id, tracker_list_length = struct.unpack_from('!HH', data, offset)
            offset += 4

            trackers = []
            while offset < len(data):
                tracker_id, tracker_data_length = struct.unpack_from('!HH', data, offset)
                offset += 4

                tracker_data = {}
                tracker_data['id'] = tracker_id

                while tracker_data_length > 0:
                    sub_chunk_id, sub_chunk_length = struct.unpack_from('!HH', data, offset)
                    offset += 4

                    if sub_chunk_id == 0x0000:  # PSN_DATA_TRACKER_POS
                        x, y, z = struct.unpack_from('!fff', data, offset)
                        tracker_data['position'] = [x, y, z]
                    elif sub_chunk_id == 0x0001:  # PSN_DATA_TRACKER_SPEED
                        x, y, z = struct.unpack_from('!fff', data, offset)
                        tracker_data['speed'] = [x, y, z]
                    elif sub_chunk_id == 0x0002:  # PSN_DATA_TRACKER_ORI
                        x, y, z = struct.unpack_from('!fff', data, offset)
                        tracker_data['orientation'] = [x, y, z]
                    else:
                        tracker_data['unknown'] = data[offset:offset+sub_chunk_length]

                    offset += sub_chunk_length
                    tracker_data_length -= sub_chunk_length + 4

                trackers.append(tracker_data)

            return trackers
        else:
            return None
