import socket
import sys
from _thread import *
import threading
import datetime
import csv
from multiprocessing import Lock
from statistics import *

print_lock = threading.Lock()
carla_lock = Lock()
state = "normal"

def algorithm_thread(filename, buffer):
    with open(filename, 'a', newline='') as f:
        hello = [mean(buffer), stdev(buffer), variance(buffer),str(datetime.datetime.now().time())]
        writer = csv.writer(f)
        writer.writerow(hello)

def writing_thread(filename, buffer):
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        for data in buffer:
            writer.writerow(data)

def state_calc(value):
    global state
    if value > 7 :
        state = "angry"
    elif value < 5 :
        state = "drowsy"
    else:
        state = "normal"

def threaded(c):
    global state
    heartrate_queue = [None] * 30
    speed_queue = [None] * 30
    force_queue = [None] * 30

    speedvals = [None] * 30
    forcevals = [None] * 30
    distancevals = [None] * 10

    heartrate_pointer = 0
    speed_pointer = 0
    force_pointer = 0
    distance_pointer = 0

    heartrate_sum = 0
    speed_sum = 0
    force_sum = 0
    while True:

        data = c.recv(1024)
        if not data:
            print('Bye')
            sys.exit(0)
        message = str(data.decode('ascii'))

        # Speed Sensor is flag 1
        if message[0] == "1":
            # start_new_thread(speed_thread,(c,))

            message = message.replace('1:', '')
            ##print("Received at: " + str(datetime.datetime.now()))
            message = message.split("\n")  ## message[0] refers to speed 2 is time
            speed = int(message[0])
            ##print(speed)

            # if (speed<=10):
            #    c.send(("None").encode())
            # carla_lock.acquire()
            if (speed > 10 and speed < 60):
                c.send(("Slow Down").encode())
                ##print('slow')
            elif (speed >= 60):
                c.send(("Thats fast").encode())
            elif (speed <= 10):
                c.send(("None").encode())
                ##print('sent none')
            # carla_lock.release()

            steering_angle = message[1]

            print("Driver is:" + str(state))
            if state == "normal":
                if(float(steering_angle) > .59 ):
                    c.send(("Steering too fast to the right").encode())
                    print(steering_angle)
                if(float(steering_angle) < -.59):
                    c.send(("Steering too fast to the left").encode())
                    print(steering_angle)

            if state == "angry":
                if(float(steering_angle) > .49 ):
                    c.send(("Steering too fast to the right").encode())
                    print(steering_angle)
                if(float(steering_angle) < -.49):
                    c.send(("Steering too fast to the left").encode())
                    print(steering_angle)

            if state == "drowsy":
                print("ello")

            ##if message[2] != "None":
                ##print(message[2])

                ##if distance_pointer == 9:
                    ##distancevals[distance_pointer] = [float(message[2]), str(datetime.datetime.now().time()), message[3]]
                    ##distance_buffer = distancevals.copy()
                    ##start_new_thread(writing_thread, ("distance_values.csv", distance_buffer))
                    ##distance_pointer = 0
                ##distancevals[distance_pointer] = [float(message[2]), str(datetime.datetime.now().time()), message[3]]
                ##distance_pointer += 1


            if speed_pointer == 29:
                ##print("Writing to CSV file")
                speed_queue[speed_pointer] = [message[0], str(datetime.datetime.now().time()),
                                              message[2]]  # [0] - msg string, [1] - speed, [2] - date
                speedvals[speed_pointer] = int(message[0])
                speed_buffer = speed_queue.copy()
                start_new_thread(algorithm_thread, ("average_speed.csv", speedvals))
                start_new_thread(writing_thread, ("speed_rate.csv", speed_buffer))
                speed_pointer = 0
            speed_queue[speed_pointer] = [message[0], str(datetime.datetime.now().time()), message[2]]
            speedvals[speed_pointer] = int(message[0])
            speed_pointer += 1
            ##print("speed pointer did pass and it was : " + str(speed_pointer))

        # Force Sensor is flag 2
        elif message[0] == "2":  # message[0] = to value
            message = message.replace("2:", '')
            message = message.split("\n")
            state_calc(int(message[0]))
            if force_pointer == 29:
                # print("Writing to CSV file")
                force_queue[force_pointer] = [message[0], str(datetime.datetime.now().time()), message[1]]
                forcevals[force_pointer] = int(message[0])
                force_buffer = force_queue.copy()
                start_new_thread(algorithm_thread, ("average_force.csv", forcevals))
                start_new_thread(writing_thread, ("force_rate.csv", force_buffer))
                force_pointer = 0
            force_queue[force_pointer] = [message[0], str(datetime.datetime.now().time()), message[1]]
            forcevals[force_pointer] = int(message[0])
            force_pointer = force_pointer + 1

        '''
        elif message[0]=="3":
            physics = message.replace("3:",'')
            physics = physics.split("\n")
            #print(physics[0])
            car_data = physics[0].split(',')
            #print (car_data)
            #print('')
            print (car_data[27])
            tire_friction=car_data[27].split('=')
            tire_friction=tire_friction[2]
            print(tire_friction)
            carla_lock.acquire()
            if (float(tire_friction)==1.5):
                #print('tire friction is 1.5')
                c.send(("Tire friction is 1.5").encode())
            carla_lock.release()
        '''

        # if message[0] == "3":
        #   message = "Heart Rate Sensor Data Received heart rate(BPM) rate: " + message.replace("3:", '')
        #  print("Received at: " + str(datetime.datetime.now()))
        # print(message)
        # c.send(message.encode('ascii'))
        # message = message.replace("3:", '')
        # print("Received at: " + str(datetime.datetime.now().time()))
        # message = message.split("\n")
        # if heartrate_pointer == 29:
        #    print("Writing to CSV file")
        #   heartrate_queue[heartrate_pointer] = [message[0], str(datetime.datetime.now().time()), message[1]]

    #                with open('heart_rate.csv', 'a', newline='') as f:
    #                   writer = csv.writer(f)
    #                  for data in heartrate_queue:
    #                     heartrate_sum = heartrate_sum + int(data[0])
    #                    writer.writerow(data)
    #
    #               with open('average_heartrate.csv', 'a', newline='') as f:
    #                  hello = [float(heartrate_sum/30),str(datetime.datetime.now().time())]
    #                 writer = csv.writer(f)
    #                writer.writerow(hello)
    #           heartrate_sum = 0
    #          heartrate_pointer = 0
    #     heartrate_queue[heartrate_pointer] = [message[0],str(datetime.datetime.now().time()),message[1]]
    #    heartrate_pointer = heartrate_pointer + 1

    # c.send("Server Received at".encode('ascii'))
    #    print("Sent to client at: " + str(datetime.datetime.now()))

    c.close()


def Main():
    try:
        hostname = socket.gethostname()
        print(hostname)
        ipaddr = socket.gethostbyname(hostname)
        print(ipaddr)

        ip_addr = input("Enter an IP address: ")

        host = ip_addr
        # host = "174.77.60.109"
        port = 12345
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        # host = "100.67.113.183"
        # port = 12345
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.bind(('100.67.113.183', port))
        print("socket binded to port", port)

        s.listen(5)
        print("socket is listening")

        while True:
            c, addr = s.accept()

            print('Connected to :', addr[0], ':', addr[1])

            start_new_thread(threaded, (c,))
        s.close()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    Main()