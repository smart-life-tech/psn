import sacn
import time
def scale_value( value, input_min, input_max, output_min, output_max):
    input_range = input_max - input_min
    output_range = output_max - output_min
    scaled_value = (((value - input_min) * output_range) / input_range) + output_min
    return scaled_value
input1=100
input2 =200
outputmin=0
outputmax=10
for i in range (100,200):
    
    print("mapped : ",scale_value(i,input1,input2,outputmin,outputmax), "number :",i)
    time.sleep(1)
sender = sacn.sACNsender()  # provide an IP-Address to bind to if you want to send multicast packets from a specific interface
sender.start()  # start the sending thread
sender.activate_output(1)  # start sending out data in the 1st universe
sender[1].multicast = True  # set multicast to True
# sender[1].destination = "192.168.1.20"  # or provide unicast information.
# Keep in mind that if multicast is on, unicast is not used
sender[1].dmx_data = (1, 2, 3, 4)  # some test DMX data

time.sleep(10)  # send the data for 10 seconds
sender.stop()  # do not forget to stop the sender