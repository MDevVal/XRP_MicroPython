from XRPLib.drivetrain import Drivetrain
from XRPLib.motor import Motor
from XRPLib.encoder import Encoder
from XRPLib.encoded_motor import EncodedMotor
from XRPLib.hcsr04 import HCSR04
from XRPLib.imu import IMU
from XRPLib.led import LED
from XRPLib.reflectance import Reflectance
from XRPLib.servo import Servo
import math
import time

class XRPBot:
    def __init__(self):
        # Default Robot Configuration
        self.left_motor = EncodedMotor(Motor(6,7, flip_dir=True),4,5)
        self.right_motor = EncodedMotor(Motor(14,15),12,13)
        self.drivetrain = Drivetrain(self.left_motor, self.right_motor)
        self.servo = Servo(16)
        self.imu = IMU()
        self.reflectance = Reflectance(26,27)
        self.sonar = HCSR04(22,28)
        self.led = LED()

xrp = XRPBot()
xrp.imu.calibrate()

# print out x, y, z, accelerometer readings
def logAccelerometer():
    while True:
        accReadings = xrp.imu.get_acc()
        print(accReadings)
        time.sleep(0.1)

# value is a lambda. threshold is a constant value
# wait until value is [GREATER/LESS] than threshold
GREATER_THAN = 1
LESS_THAN = 2
def wait_until(value, comparator, threshold):
    def compare(a, b, comparator):
        if comparator == GREATER_THAN:
            return a > b
        elif comparator == LESS_THAN:
            return a < b
        else:
            return False
        
    while not compare(value(), threshold, comparator):
        time.sleep(0.01)

def ramp_demo():

    SPEED = 0.7

    Z_PARALLEL = 990 # z acceleration when parallel to ground
    Z_CLIMBING = 970

    z = lambda: xrp.imu.get_acc()[2] # get z acceleration

    direction = 1 # 1 for forward, -1 for backward

    # start flat on the ground aimed at ramp
    while True:

        speed = SPEED * direction

        xrp.drivetrain.set_effort(speed, speed)
        
        # wait until going up ramp
        wait_until(z, LESS_THAN, Z_CLIMBING)

        # wait until on ramp
        wait_until(z, GREATER_THAN, Z_PARALLEL)
        
        # go forward a little longer to get to center of ramp
        time.sleep(0.2)

        # stop on center of ramp and stay there for a few seconds
        xrp.drivetrain.stop()
        time.sleep(2)

        # get off ramp
        xrp.drivetrain.set_effort(speed, speed)
        wait_until(z, LESS_THAN, Z_CLIMBING)

        # get back to flat ground
        wait_until(z, GREATER_THAN, Z_PARALLEL)
        time.sleep(0.5) # wait a little longer to get some distance between robot and ramp

        # stop for a few seconds
        xrp.drivetrain.stop()
        time.sleep(2)

        # switch direction
        direction *= -1


