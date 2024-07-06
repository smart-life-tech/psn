#! /bin/env python
import sacn
import pypsn

# Simple forwarder of PSN to DMX. Turns all coordinates to positive ints...

sender = sacn.sACNsender()


def start_dmx():
    sender.start()  # start the sending thread
    sender.activate_output(1)  # start sending out data in the 1st universe
    sender[1].multicast = True  # set multicast to True


def stop_dmx():
    sender.stop()  # do not forget to stop the sender


def start_psn():
    pypsn.receiver(fill_dmx, "0.0.0.0").start()


def fill_dmx(psn_data):
    if isinstance(psn_data, pypsn.psn_data_packet):
        position = psn_data.trackers[0].pos
        dmx_data = [0] * 512
        dmx_data[0] = int(abs(position.x))
        dmx_data[1] = int(abs(position.y))
        dmx_data[2] = int(abs(position.z))
        #print(position)
        speed=psn_data.trackers[0].speed
        status= psn_data.trackers[0].status
        timestamp= psn_data.trackers[0].timestamp
        trgpos=psn_data.trackers[0].info
        if(position.x>0):
            dmx_data[0]=512-int(abs(position.x))
            #print(position.x)
        if(position.y>0):
            dmx_data[1]=512-int(abs(position.y))
            print(position.y)
        if(position.z>0):
            dmx_data[2]=512-int(abs(position.z))
            print(position.z)
        # print("postion : ",position)
        # print("speed :" ,speed)
        # print("status :" ,status)
        # print("timestamp :" ,timestamp)
        # print("trgpos :" ,trgpos)
        #sender[1].dmx_data = dmx_data


if __name__ == "__main__":
    start_dmx()
    start_psn()