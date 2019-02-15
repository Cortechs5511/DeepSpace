from wpilib.command import Command

class BackClimb(Command):
    def __init__(self, up):
        super().__init__('setSpeedWheel')
        self.robot = self.getRobot()
        self.climber = self.robot.climber
        self.requires(self.climber)
        self.up = up

    def initialize(self): pass

    def execute(self):
        if self.up == True: self.climber.liftBack(self.climber.returnClimbSpeed(), False)
        elif self.up == False: self.climber.liftBack(-1 * self.climber.returnClimbSpeed(), False)

    def interrupted(self): self.climber.stopBack()

    def end(self): self.climber.stopBack()

    def isFinished(self): return self.climber.isFullyExtendedBoth()