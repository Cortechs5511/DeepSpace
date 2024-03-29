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
        self.simpleGain = 0.1
        self.wristUpVolts = 5
        self.wristDownVolts = 2
        self.simpleGainGravity = 0.05
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
        #choose sensor
        self.wrist.configSelectedFeedbackSensor(
            Talon.FeedbackDevice.CTRE_MagEncoder_Relative,
            self.kPIDLoopIdx,
            self.kTimeoutMs,)
        self.wrist.setSensorPhase(False) #!!!!!

        # Set relevant frame periods to be at least as fast as periodic rate
        self.wrist.setStatusFramePeriod(
            Talon.StatusFrameEnhanced.Status_13_Base_PIDF0, 10, self.kTimeoutMs)
        self.wrist.setStatusFramePeriod(
            Talon.StatusFrameEnhanced.Status_10_MotionMagic, 10, self.kTimeoutMs)
        # set the peak and nominal outputs
        self.wrist.configNominalOutputForward(0, self.kTimeoutMs)
        self.wrist.configNominalOutputReverse(0, self.kTimeoutMs)
        self.wrist.configPeakOutputForward(0.6, self.kTimeoutMs)
        self.wrist.configPeakOutputReverse(-0.25, self.kTimeoutMs)

        self.kF = self.getFeedForward(self.getNumber("Wrist F Gain" , 0))
        self.kP = self.getNumber("Wrist kP" , 0)
        self.kI = self.getNumber("Wrist kI" , 0)
        self.kD = self.getNumber("Wrist kD" , 0)

        # set closed loop gains in slot0 - see documentation */
        self.wrist.selectProfileSlot(self.kSlotIdx, self.kPIDLoopIdx)
        self.wrist.config_kF(0, self.kF, self.kTimeoutMs)
        self.wrist.config_kP(0, self.kP, self.kTimeoutMs)
        self.wrist.config_kI(0, 0, self.kTimeoutMs)
        self.wrist.config_kD(0, 0, self.kTimeoutMs)
        # set acceleration and vcruise velocity - see documentation
        self.wrist.configMotionCruiseVelocity(400, self.kTimeoutMs) #!!!!!
        self.wrist.configMotionAcceleration(500, self.kTimeoutMs) #!!!!!
        # zero the sensor
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
        elif mode == "upMagic":

            if self.lastMode != mode:
                self.wrist.config_kF(0, self.kF, self.kTimeoutMs)
                self.wrist.config_kP(0, self.kP, self.kTimeoutMs)
                self.wrist.config_kI(0, 0, self.kTimeoutMs)
                self.wrist.config_kD(0, 0, self.kTimeoutMs)
            # Motion Magic - 4096 ticks/rev * 10 Rotations in either direction
            self.wrist.set(Talon.ControlMode.MotionMagic, self.targetPosUp)

            # append more signals to print when in speed mode.
            self.sb.append("\terr: %s" % self.wrist.getClosedLoopError(self.kPIDLoopIdx))
            self.sb.append("\ttrg: %.3f" % self.targetPosUp)

        elif mode == "downMagic":

            if self.lastMode != mode:
                self.wrist.config_kF(0, self.kF, self.kTimeoutMs)
                self.wrist.config_kP(0, self.kP, self.kTimeoutMs)
                self.wrist.config_kI(0, 0, self.kTimeoutMs)
                self.wrist.config_kD(0, 0, self.kTimeoutMs)
            # Motion Magic - 4096 ticks/rev * 10 Rotations in either direction
            self.wrist.set(Talon.ControlMode.MotionMagic, self.targetPosDown)

            # append more signals to print when in speed mode.
            self.sb.append("\terr: %s" % self.wrist.getClosedLoopError(self.kPIDLoopIdx))
            self.sb.append("\ttrg: %.3f" % self.targetPosDown)
        elif mode == "stop":
            self.wrist.set(0)
        else:
            self.wrist.set(self.getGravitySimple())

        self.lastMode = mode


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
        elif self.joystick0.getRawButton(map.wristUpMagic): self.moveWrist("upMagic")
        elif self.joystick0.getRawButton(map.wristDownMagic): self.moveWrist("downMagic")
        else:
            self.moveWrist("gravity")

        # calculate the percent motor output
        motorOutput = self.wrist.getMotorOutputPercent()

        self.sb = []
        # prepare line to print
        self.sb.append("\tOut%%: %.3f" % motorOutput)
        self.sb.append("\tVel: %.3f" % self.wrist.getSelectedSensorVelocity(self.kPIDLoopIdx))

        # instrumentation
        self.processInstrumentation(self.wrist, self.sb)

    def disable(self): self.intake("stop")

    def processInstrumentation(self, tal, sb):
        # smart dash plots
        wpilib.SmartDashboard.putNumber("SensorVel", tal.getSelectedSensorVelocity(self.kPIDLoopIdx))
        wpilib.SmartDashboard.putNumber("SensorPos", tal.getSelectedSensorPosition(self.kPIDLoopIdx))
        wpilib.SmartDashboard.putNumber("MotorOutputPercent", tal.getMotorOutputPercent())
        wpilib.SmartDashboard.putNumber("ClosedLoopError", tal.getClosedLoopError(self.kPIDLoopIdx))

        # check if we are motion-magic-ing
        if tal.getControlMode() == Talon.ControlMode.MotionMagic:
            self.timesInMotionMagic += 1
        else:
            self.timesInMotionMagic = 0

        if self.timesInMotionMagic > 10:
            # print the Active Trajectory Point Motion Magic is servoing towards
            wpilib.SmartDashboard.putNumber(
                "ClosedLoopTarget", tal.getClosedLoopTarget(self.kPIDLoopIdx)
            )

        if not wpilib.RobotBase.isSimulation():
            wpilib.SmartDashboard.putNumber(
                "ActTrajVelocity", tal.getActiveTrajectoryVelocity()
            )
            wpilib.SmartDashboard.putNumber(
                "ActTrajPosition", tal.getActiveTrajectoryPosition()
            )
            wpilib.SmartDashboard.putNumber(
                "ActTrajHeading", tal.getActiveTrajectoryHeading()
            )

        # periodically print to console
        self.loops += 1
        if self.loops >= 10:
            self.loops = 0
            print(" ".join(self.sb))

        # clear line cache
        self.sb.clear()

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
        self.kF = self.getFeedForward(self.getNumber("Wrist F Gain" , 0))
        self.kP = self.getNumber("Wrist kP" , 0)
        self.kI = self.getNumber("Wrist kI" , 0)
        self.kD = self.getNumber("Wrist kD" , 0)
        self.simpleGain = self.getNumber("Wrist Simple Gain", 0.5)
        self.simpleGainGravity = self.getNumber("Wrist Simple Gain Gravity", 0.07)
        SmartDashboard.putNumber("Wrist Position", self.wrist.getQuadraturePosition())
        SmartDashboard.putNumber("Wrist Angle" , self.getAngle())
        SmartDashboard.putNumber("Wrist Power Up" , self.getPowerSimple("up"))
        SmartDashboard.putNumber("Wrist Power Down" , self.getPowerSimple("down"))
