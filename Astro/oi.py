import wpilib

from wpilib.joystick import Joystick
from wpilib.buttons.joystickbutton import JoystickButton
from wpilib.buttons import Button
from wpilib.buttons import Trigger
from wpilib import SmartDashboard


from wpilib import XboxController as Xbox

from commands.crash import Crash

from commands.drive.bump import Bump

class axisButton(Trigger):

    def __init__(self, f, num, Threshold):
        self.f = f
        self.num = num
        self.Threshold = Threshold

    def get(self):
        return abs(self.f(self.num)) > self.Threshold

def getJoystick(num):
    '''
    Assign commands to button actions, and publish your joysticks so you
    can read values from them later.
    '''
    #CHANGE
    if wpilib.robotBase.isSimulation():
        joystick0 = Joystick(1)
        joystick1 = Joystick(2)
        xbox = Xbox(0)
    else:
        joystick0 = Joystick(0)
        joystick1 = Joystick(1)
        xbox = Xbox(2)

    if num == 0: return joystick0
    elif num == 1: return joystick1
    else: return xbox

def commands():
    #SmartDashboard.putData("bumpDrive", Bump())

    joystick0 = getJoystick(0)
    joystick1 = getJoystick(1)
    xbox = getJoystick(2)
    return [joystick0, joystick1, xbox]
