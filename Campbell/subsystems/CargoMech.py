from wpilib import SmartDashboard
from ctre import WPI_TalonSRX as Talon
from wpilib import SmartDashboard
import wpilib
import map
import oi
from sim import simComms
import math

class CargoMech():
    kSlotIdx = 0
    kPIDLoopIdx = 0
    kTimeoutMs = 10

    def initialize(self):
        timeout = 15
        self.lastMode = "unknown"
        self.sb = []
        self.targetPosUp = -300 #!!!!!
        self.targetPosDown = -1500 #!!!!!
        self.maxVolts = 10
        self.simpleGain = 0.57
        self.wristUpVolts = 5
        self.wristDownVolts = 2
        self.simpleGainGravity = 0.07
        self.xbox = oi.getJoystick(2)
        self.joystick0 = oi.getJoystick(0)
        self.motor = Talon(map.intake)


        self.motor.configContinuousCurrentLimit(20,timeout) #15 Amps per motor
        self.motor.configPeakCurrentLimit(30,timeout) #20 Amps during Peak Duration
        self.motor.configPeakCurrentDuration(100,timeout) #Peak Current for max 100 ms
        self.motor.enableCurrentLimit(True)


        self.wrist = Talon(map.wrist)
        if not wpilib.RobotBase.isSimulation():
            self.wrist.configFactoryDefault()
        self.wrist.setInverted(True)
        self.wrist.setNeutralMode(2)
        self.motor.setNeutralMode(2)
        self.motor.configVoltageCompSaturation(self.maxVolts)
        self.intakeSpeed = 0.9

        self.wrist.configClearPositionOnLimitF(True)

        #MOTION MAGIC CONFIG
        self.loops = 0
        self.timesInMotionMagic = 0
      

        self.wrist.setSelectedSensorPosition(0, self.kPIDLoopIdx, self.kTimeoutMs)

    def intake(self, mode):
        ''' Intake/Outtake/Stop Intake the cargo (turn wheels inward)'''
        if mode == "intake": self.motor.set(self.intakeSpeed)
        elif mode == "outtake": self.motor.set(-1 * self.intakeSpeed)
        elif mode == "stop": self.motor.set(0)

    def moveWrist(self,mode):
        '''move wrist in and out of robot'''
        if mode == "up": self.wrist.set(self.getPowerSimple("up"))
        elif mode == "down": self.wrist.set(-1 * self.getPowerSimple("down"))
        elif mode == "upVolts": self.wrist.set(self.wristUpVolts/self.maxVolts)
        elif mode == "downVolts": self.wrist.set(-1 * self.wristDownVolts/ self.maxVolts)
        elif mode == "stop":
            self.wrist.set(0)
        else:
            self.wrist.set(self.getGravitySimple())

    def periodic(self):
        deadband = 0.4

        if self.xbox.getRawAxis(map.intakeCargo)>deadband: self.intake("intake")
        elif self.xbox.getRawAxis(map.outtakeCargo)>deadband: self.intake("outtake")
        else:
            self.intake("stop")

        if self.xbox.getRawButton(map.wristUp): self.moveWrist("up")
        elif self.xbox.getRawButton(map.wristDown): self.moveWrist("down")
        elif self.joystick0.getRawButton(map.wristUpVolts): self.moveWrist("upVolts")
        elif self.joystick0.getRawButton(map.wristDownVolts): self.moveWrist("downVolts")
        else:
            self.moveWrist("gravity")

    def disable(self): self.intake("stop")


    def getAngle(self):
        pos = self.getPosition()
        angle = abs(pos * 115/self.targetPosDown)
        return angle - 25

    def getPosition(self):
        return self.wrist.getQuadraturePosition()

    def getFeedForward(self, gain):
        angle = self.getAngle()
        return angle*gain

    def getPowerSimple(self, direction):
        '''true direction is up into robot
        false direction is down out of robot'''
        angle = self.getAngle()
        power = abs(self.simpleGainGravity * math.sin(math.radians(angle)) + self.simpleGain)
        if angle > 80:
            if direction == "down":
                power = 0
        if angle < -20:
            if direction == "up":
                power = 0
        return power

    def getGravitySimple(self):
        angle = self.getAngle()
        power =  self.simpleGainGravity * math.sin(math.radians(angle))
        return power

    def getNumber(self, key, defVal):
        val = SmartDashboard.getNumber(key, None)
        if val == None:
            val = defVal
            SmartDashboard.putNumber(key, val)
        return val

    def dashboardInit(self):
        pass

    def dashboardPeriodic(self):
        self.wristUp = self.getNumber("WristUpSpeed" , 0.5)
        self.wristDown = self.getNumber("WristDownSpeed" , 0.2)
        self.wristUpVolts = self.getNumber("WristUpVoltage" , 5)
        self.wristDownVolts = self.getNumber("WristDownVoltage" , 2)
        self.simpleGain = self.getNumber("Wrist Simple Gain", self.simpleGain)
        self.simpleGainGravity = self.getNumber("Wrist Simple Gain Gravity", self.simpleGainGravity)
        SmartDashboard.putNumber("Wrist Position", self.wrist.getQuadraturePosition())
        SmartDashboard.putNumber("Wrist Angle" , self.getAngle())
        SmartDashboard.putNumber("Wrist Power Up" , self.getPowerSimple("up"))
        SmartDashboard.putNumber("Wrist Power Down" , self.getPowerSimple("down"))
