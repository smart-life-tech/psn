from pythonosc import udp_client
from pythonosc import osc_message_builder
import time

# Define the OSC client
ip = "192.168.0.202"  # Change this to the IP address of the OSC server
port = 5005  # Change this to the port the OSC server is listening on

client = udp_client.SimpleUDPClient(ip, port)

# Define the OSC address and the message
osc_address = "/example/address"
message = "Hello, OSC!"

# Send the OSC message
client.send_message(osc_address, message)
print(f"Sent '{message}' to {osc_address}")

# Sending multiple messages
for i in range(5):
    message = f"Message {i}"
    client.send_message(osc_address, message)
    print(f"Sent '{message}' to {osc_address}")
    time.sleep(1)
