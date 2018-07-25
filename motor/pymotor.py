import ctypes
from ctypes import *
import time
import os
import sys
import re
import platform
#from VitualDevice import *
import tempfile

cur_dir = os.path.abspath(os.path.dirname(__file__))
ximc_dir = os.path.join(cur_dir, "..", "ximc")
ximc_package_dir = os.path.join(ximc_dir, "crossplatform", "wrappers", "python")
sys.path.append(ximc_package_dir)  # add ximc.py wrapper to python path

print(ximc_package_dir)

if platform.system()  == "Windows":
    print("windows#################")
    if platform.architecture() == ('64bit', 'WindowsPE') :
        libdir = os.path.join(ximc_dir, "win64")
        #print(platform.architecture())
    else:
        libdir = os.path.join(ximc_dir,"win32")
        #print(platform.architecture())

    #print(libdir)
    os.environ["Path"] = libdir + ";" + os.environ["Path"]  # add dll

if sys.version_info >= (3,0):

    try:
        from pyximc import *
    except ImportError as err:
        print ("Can't import pyximc module.\
               The most probable reason is that \
               you haven't copied pyximc.py to the working directory.\
               See developers' documentation for details.")
        exit()
    except OSError as err:
        print ("Can't load libximc library.\
               Please add all shared libraries to the appropriate places \
               (next to pyximc.py on Windows). \
               It is decribed in detailes in developers' documentation.")
        exit()

# variable 'lib' points to a loaded library
# note that ximc uses stdcall on win
print("Library loaded")
sbuf = create_string_buffer(64)
lib.ximc_version(sbuf)
print("Library version: " + sbuf.raw.decode())

DEBUG = True
def log(s):
    if DEBUG:
        print(s)

def enum_device():
    devenum = lib.enumerate_devices(EnumerateFlags.ENUMERATE_PROBE, None)
    print("Device enum handle: " + repr(devenum))
    print("Device enum handle type: " + repr(type(devenum)))

    dev_count = lib.get_device_count(devenum)
    print("Device count: " + repr(dev_count))

    controller_name = controller_name_t()
    enum_name = ['','','']
    for dev_ind in range(0, dev_count):
        enum_name[dev_ind] = lib.get_device_name(devenum, dev_ind)
        result = lib.get_enumerate_device_controller_name(devenum, dev_ind,
                                                                   byref(controller_name))
        if result == Result.Ok:
            print("Enumerated device #{} name (port name): ".format(dev_ind) \
                    + repr(enum_name[dev_ind]) \
                    + ". Friendly name: " \
                    + repr(controller_name.ControllerName) \
                    + ".")

    return enum_name, dev_count

class Motor():
    def __init__(self, device_name = None):
        self.lib = lib
        self.device_id = self.open_device(device_name)


    def set_speed(self,step,speed):
        log("\nset speed\n")
        speed_settings = move_settings_t()
        speed_settings.Speed = speed
        speed_settings.uSpeed = step
        speed_settings.Accel = 1
        speed_settings.Decel = 1
        speed_settings.AntiplaySpeed = 1
        speed_settings.uAntiplaySpeed = 1
        result = self.lib.set_move_settings(self.device_id,speed_settings)
        print("move settings Result:" + repr(result))
        move_settings = move_settings_t()
        result = self.lib.get_move_settings(self.device_id,move_settings)
        if result == 0:
            print("move settings:",move_settings.Speed,move_settings.uSpeed,move_settings.Accel,move_settings.Decel)


    def home(self):
        log("\nMoving home")
        result = self.lib.command_homezero(self.device_id)
        log("Result: " + repr(result))

    def forward(self, distance):      # move forward Deltaposition
        log("\nShifting")
        log(distance)
        dis = ctypes.c_int()
        dis.value = int(distance)
        #move_settings = move_settings_t()
        #result = self.lib.get_move_settings(self.device_id,move_settings)
        #if result == 0 and platform.system() != "Linux":
        #    print("move settings:",move_settings.Speed,move_settings.uSpeed,move_settings.Accel,move_settings.Decel)
        result = self.lib.command_movr(self.device_id, dis, 0)
        log("Result: " + repr(result))

    def backward(self, distance):    # move backward Deltaposition
        log("\nShifting")
        shift = ctypes.c_int()
        shift.value = 0 - int(distance) # in oppsite direction
        result = self.lib.command_movr(self.device_id, shift, 0)
        log("Result: " + repr(result))

    def moveforward(self):
        log("\nMoving forward")
        result = self.lib.command_right(self.device_id)
        log("Result: " + repr(result))

    def movebackward(self):
        log("\nMoving backward")
        result = self.lib.command_left(self.device_id)
        log("Result: " + repr(result))

    def move(self, position):        # move to the Setposition
        log("\nMoving position")
        pos = ctypes.c_int()
        pos.value = int(position)
        result = self.lib.command_move(self.device_id, pos, 0)
        print("Result: " + repr(result))

    def stop(self):
        log("\nStopping")
        result = self.lib.command_stop(self.device_id)
        log("Result: " + repr(result))

    def get_position(self):
        print("\nRead position")
        pos = get_position_t()
        result = self.lib.get_position(self.device_id, byref(pos))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Position: " + repr(pos.Position))
            return pos.Position

    def set_position(self, position):
        print("\nSet position")
        pos = set_position_t()
        pos.Position = position
        result = self.lib.set_position(self.device_id, byref(pos))
        print("Result: " + repr(result))
        if result == Result.Ok:
            print("Setting Position Done")

    def get_status_position(self):
        log("\nGet status")
        status = status_t()
        result = self.lib.get_status(self.device_id, byref(status))
        log("Result: " + repr(result))
        if result == Result.Ok:
            log("Status.CurPosition: " + repr(status.CurPosition))
        return status.CurPosition

    def get_status(self):
        log("\nGet status")
        status = status_t()
        result = self.lib.get_status(self.device_id, byref(status))
        log("Result: " + repr(result))
        if result == Result.Ok:
            log("Status.CurPosition: " + repr(status.CurPosition))

    def get_name(self,devenum,dev_index):
        return self.lib.get_device_name(devenum,dev_index)


    def open_device(self, open_name):
        device_id = ctypes.c_int()
        print("\nOpen device " + repr(open_name))
        device_id = self.lib.open_device(open_name)

        print("\ndevice id:" + repr(device_id))
        return device_id

    def close_device(self):
        result = self.lib.close_device(byref(cast(self.device_id, POINTER(c_int))))
        if result == Result.Ok:
            print("Close device " + repr(self.device_id))


class MultiMotor():
    def __init__(self, device_name=None):
        self.lib = lib
        self.device_id = self.open_multidevice(device_name)

    def open_multidevice(self, device_name):
        device_id = []
        self.motor1 = Motor(str(device_name[0]))
        device_id.append(self.motor1.device_id)

        self.motor2 = Motor(str(device_name[1]))
        device_id.append(self.motor2.device_id)

        self.motor3 = Motor(str(device_name[2]))
        device_id.append(self.motor3.device_id)

        return device_id

    def move_multidevice(self, multiconfig, time):
        # i,j,k -> x,y,z
        # multiconfig[3][3]
        #  x0  dx  nx
        #  y0  dy  ny
        #  z0  dz  nz
        x0 = multiconfig[0][0]
        dx = multiconfig[0][1]
        nx = multiconfig[0][2]
        xe = x0+dx*(nx+1)
        y0 = multiconfig[1][0]
        dy = multiconfig[1][1]
        ny = multiconfig[1][2]
        ye = y0+dy*(ny+1)
        z0 = multiconfig[2][0]
        dz = multiconfig[2][1]
        nz = multiconfig[2][2]
        ze = z0+dz*(nz+1)

        print("position:" + str(self.get_status_position()))
        for i in range(x0,xe,dx):
            self.motor1.move(i)
            self.timesleep(time)
            for j in range(y0,ye,dy):
                self.motor2.move(j)
                self.timesleep(time)
                for k in range(z0,ze,dz):
                    self.motor3.move(k)
                    self.timesleep(time)
        print("position: " + str(self.get_status_position()))

    def timesleep(self, dt):
        time.sleep(dt)

    def get_status_position(self):
        x = self.motor1.get_status_position()
        y = self.motor2.get_status_position()
        z = self.motor3.get_status_position()
        pos = [x,y,z]
        return pos

    def close_multidevices(self):
        self.motor1.close_device()
        self.motor2.close_device()
        self.motor3.close_device()

def test_singlemotor():
    # This is device search and enumeration with probing.
    # It gives more information about devices.
    devenum, dev_count = enum_device()
    if dev_count == 0:
        print("\nNo finding of device.")
        print("Use the vitual device:")
        open_name = "testdevice2"
        device_pytct = VitualDevice(open_name)
    else:
        open_name=lib.get_device_name(devenum, 0)
    #open_name = "xi-com:///dev/tty.usbmodem00000D81"
        device_pytct = Motor(open_name)

    print("---------------")
    print("Device id: " + repr(device_pytct.device_id))

    device_pytct.home()
    time.sleep(1)
    print("position: " + str(device_pytct.get_position()))

    device_pytct.set_position(100)
    time.sleep(1)

    device_pytct.move(100)
    time.sleep(2)

    device_pytct.forward(100)
    time.sleep(1)
    print("position: " + str(device_pytct.get_status_position()))

    print("---------------")
    device_pytct.backward(200)
    time.sleep(1)
    print("position: " + str(device_pytct.get_status_position()))

    device_pytct.close_device()
    print("Done")

def test_multimotor():
    open_name1 = "testdevice1"
    open_name2 = "testdevice2"
    open_name3 = "testdevice3"
    open_name = [open_name1,open_name2,open_name3]
    multidevice = MultiMotor(open_name)
    config = [[1, 10, 10],[2, 20, 15],[10, 1, 0]]
    time = 0.002
    multidevice.move_multidevice(config,time)


#if __name__ == '__main__':
    #test_singlemotor()
    #test_multimotor()
