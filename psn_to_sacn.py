#! /bin/env python
import sacn
import pypsn
prints=True
# Simple forwarder of PSN to DMX. Turns all coordinates to positive ints...
import time
sender = sacn.sACNsender()


def start_dmx():
    sender.start()  # start the sending thread
    sender.activate_output(1)  # start sending out data in the 1st universe
    sender[1].multicast = True  # set multicast to True


def stop_dmx():
    sender.stop()  # do not forget to stop the sender


def start_psn():
    pypsn.receiver(fill_dmx, "0.0.0.0").start()
def stop_psn():
    pypsn.receiver().stop()


def fill_dmx(psn_data):
    global prints
    time.sleep(5)
    try:
        if isinstance(psn_data, pypsn.psn_data_packet):
                
            position = psn_data.trackers[0].pos
            position = psn_data.trackers[1].pos
            info=psn_data.trackers[0].info
            
            position2 = psn_data.trackers[0].accel
            dmx_data = [0] * 512
            dmx_data[0] = int(abs(position.x))
            dmx_data[1] = int(abs(position.y))
            dmx_data[2] = int(abs(position.z))
            #print(position)
            speed=psn_data.trackers[0].speed
            status= psn_data.trackers[0].status
            timestamp= psn_data.trackers[0].timestamp
            trgpos=psn_data.trackers[0].info
            print("position2 : ",position2)
            print("speed : ",speed)
            print("status : ",status)
            print("timestamp : ",timestamp)
            print("trgpos : ",trgpos)
            print("position2 : ",position2)
            print("info : ",info)
            if(position.x>0):
                dmx_data[0]=512-int(abs(position.x))
                print("x position",position.x)
                print("y position : ",position.y)
                print("z position : ",position.z)
            if(position2.y>0 ):
                dmx_data[1]=512-int(abs(position.y))
                print("y postion data====== : ",position2.y)
                #print("x postion data====== : ",position2.x)
            if(position.z>0):
                dmx_data[2]=512-int(abs(position.z))
                print(position.z)
            # print("postion : ",position)
            # print("speed :" ,speed)
            # print("status :" ,status)
            # print("timestamp :" ,timestamp)
            # print("trgpos :" ,trgpos)
            #sender[1].dmx_data = dmx_data
    except Exception as e:
        print("error",e)
        pass

if __name__ == "__main__":
    print("Starting...")
    start_dmx()
    start_psn()