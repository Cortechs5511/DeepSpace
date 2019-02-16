import wpilib
from wpilib.command import Command
from wpilib.command import TimedCommand
from commands.climber import liftRobot

class AutoClimb(CommandGroup):
    def __init__(self):
        self.addSequential(self.LiftRobot("both"))
        self.addSequential(self.DriveToEdge("front"))
        self.addSequential(self.LiftRobot("front")
        self.addSequential(self.DriveToEdge("back")
        self.addSequential(self.LiftRobot("back"))
        self.addSequential(self.commands.drive.setFixedDT.SetFixedDT(0.5,0.5))


        