from wpilib.command import CommandGroup

from commands.drive import driveStraightCombined
from commands.drive import driveStraightDistance
from commands.drive import turnAngle
from commands.drive import setFixedDT

from subsystems import HatchMech

class DriveStraight(CommandGroup):
    def __init__(self):
        super().__init__('DriveStraight')
        DriveStraightDistance = driveStraightDistance.DriveStraightDistance
        self.addSequential(DriveStraightDistance(distance=90, timeout=100)) #just off hab platformclass LeftCargo(CommandGroup):

class LeftCargo(CommandGroup):
    def __init__(self):
        super().__init__('LeftCargo')
        TurnAngle = turnAngle.TurnAngle

        DriveStraightCombined = driveStraightCombined.DriveStraightCombined
        EjectHatch = HatchMech.EjectHatch
        SetFixedDT = setFixedDT.SetFixedDT

        self.addSequential(DriveStraightCombined(distance=194.5, angle=0, timeout=5))
        self.addSequential(TurnAngle(angle=90, timeout=2.5))
        self.addSequential(SetFixedDT(0.3,0.3, timeout=3))
        self.addSequential(EjectHatch())

class DriveStraightSide(CommandGroup):
    def __init__(self):
        super().__init__('DriveStraightSide')
        DriveStraightCombined = driveStraightCombined.DriveStraightCombined

        self.addSequential(DriveStraightCombined(distance=194, angle=0, timeout=10)) #just off hab platform


class RightCargo(CommandGroup):
    def __init__(self):
        super().__init__('RightCargo')
        DriveStraightCombined = driveStraightCombined.DriveStraightCombined
        TurnAngle = turnAngle.TurnAngle
        EjectHatch = HatchMech.EjectHatch
        SetFixedDT = setFixedDT.SetFixedDT

        self.addSequential(DriveStraightCombined(distance=194.5, angle=0, timeout=5))
        self.addSequential(TurnAngle(angle=-90, timeout=2.5))
        self.addSequential(SetFixedDT(0.3,0.3, timeout=3))
        self.addSequential(EjectHatch())

class CenterCargo(CommandGroup):
    def __init__(self):
        super().__init__('CenterCargo')
        DriveStraightCombined = driveStraightCombined.DriveStraightCombined
        EjectHatch = HatchMech.EjectHatch

        self.addSequential(DriveStraightCombined(distance=173.25, angle=0, timeout=.75))
        #self.addSequential(EjectHatch())
