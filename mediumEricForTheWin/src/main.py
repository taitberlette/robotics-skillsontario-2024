# import the vex stuff 🤖
from vex import *

# main computer 🧠
brain = Brain()

# radio controller (automatically set up by the brain) 🎮
controller = Controller()

# wheels
left_drive = Motor(Ports.PORT20, GearSetting.RATIO_18_1, False)
right_drive = Motor(Ports.PORT19, GearSetting.RATIO_18_1, True)

# auxiliary motors
claw_motor = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)
arm_base_motor = Motor(Ports.PORT9, GearSetting.RATIO_18_1, True)
arm_joint_motor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, False)
tray_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
snow_motor = Motor(Ports.PORT18, GearSetting.RATIO_18_1, False)

# presets for the tree height
# first the top dowel, then the lower one
# (angle base, angle joint)
PRESETS = ((456.8, 435.2), (427.6, 295.2 + 50))

# keep track of precision mode settings
precise = False

# toggle between precise and regular mode 
def toggle_precise():
  global precise
  precise = (False if precise else True)

  #print the position of the arms too to help debug presets
  print_position()

# reset all the angles of the motor to zero (do this when the arm is retracted fully to match with the presets)
def recalibrate():
  arm_base_motor.reset_position()
  arm_joint_motor.reset_position()

# move a motor (see event description below!)
def control_motor(direction, motor, percent):
  motor.spin(FORWARD, direction * percent)

# move the arm to a preset given by index 
def move_arm_to(i):
    arm_base_motor.spin_to_position(PRESETS[i][0], DEGREES, 60, RPM, True)
    arm_joint_motor.spin_to_position(PRESETS[i][1], DEGREES, 60, RPM, False)

# print the position of the arms for debugging purposes 🐛🪲🐞
def print_position():
   controller.screen.clear_screen()
   controller.screen.set_cursor(0, 0)
   controller.screen.print("BASE: " + str(arm_base_motor.position(DEGREES)))
   controller.screen.next_row()
   controller.screen.print("MID:  " + str(arm_joint_motor.position(DEGREES)))


# main driving/controlling thread
def drive_task():
    # loop forever until the end of time ⌛
    while True:
				# get the value of the two joysticks
        left_joystick_y = controller.axis3.position()
        right_joystick_x = controller.axis1.position()

        # remap the controller values
        steer = abs(right_joystick_x) / (4 if precise else 2)
        speed = abs(left_joystick_y) / (3 if precise else 1)

        # slow down going backwards (the steer should also probably be just to but idk 🤡)
        if left_joystick_y < 0 and not precise:
            speed = speed / 2

        # use a little buffer room to account for wonky controller drift

        # forwards ⬆️
        if left_joystick_y > 5:
          # turn while going forwards
          if right_joystick_x > 5:
              left_drive.spin(FORWARD, speed, PERCENT)
              right_drive.spin(FORWARD, speed - steer, PERCENT)
          elif right_joystick_x < -5:
              left_drive.spin(FORWARD, speed - steer, PERCENT)
              right_drive.spin(FORWARD, speed, PERCENT)
          
          # forwards in a straight line
          else:
              left_drive.spin(FORWARD, speed, PERCENT)
              right_drive.spin(FORWARD, speed, PERCENT)
          
        # backwards ⬇️
        elif left_joystick_y < -5:
            # turn while going backwards
            if right_joystick_x > 5:
                left_drive.spin(REVERSE, speed - steer, PERCENT)
                right_drive.spin(REVERSE, speed, PERCENT)
            elif right_joystick_x < -5:
                left_drive.spin(REVERSE, speed, PERCENT)
                right_drive.spin(REVERSE, speed - steer, PERCENT)

            # backwards in a straight line
            else:
                left_drive.spin(REVERSE, speed, PERCENT)
                right_drive.spin(REVERSE, speed, PERCENT)
            
        # spin in place 💫
        elif right_joystick_x > 15:
            left_drive.spin(FORWARD, steer, PERCENT)
            right_drive.spin(REVERSE, steer, PERCENT)
        elif right_joystick_x < -15: 
            left_drive.spin(REVERSE, steer, PERCENT)
            right_drive.spin(FORWARD, steer, PERCENT)

        # no inputs, stop 🛑
        else:
            left_drive.stop() 
            right_drive.stop()
      
        
        # a little delay just for fun 😇
        sleep(10)

# start running the controller code 🤖
drive = Thread(drive_task)

# setup the claw motor
claw_motor.set_stopping(HOLD)

# stop the robot when we want so it doesn't coast
left_drive.set_stopping(BRAKE)
right_drive.set_stopping(BRAKE)

# setup the arm motors
arm_base_motor.set_stopping(HOLD)
arm_joint_motor.set_stopping(HOLD)

# hold the snow pile up
snow_motor.set_stopping(HOLD)

# when the a button is pressed, toggle precise mode
controller.buttonA.pressed(toggle_precise)

# when the b button is pressed, recalibrate the arm (when the arm is retracted/fully down to not mess with presets)
# DO BEFORE YOU TRY TO USE PRESETS
controller.buttonB.pressed(recalibrate)

# when the x and y buttons are pressed move to the presets
controller.buttonX.pressed(move_arm_to, [0])
controller.buttonY.pressed(move_arm_to, [1])

# move the different motors
# left buttons, first segment
controller.buttonL1.pressed(control_motor, (1, arm_base_motor, 60))
controller.buttonL1.released(control_motor, (0, arm_base_motor, 60))
controller.buttonL2.pressed(control_motor, (-1, arm_base_motor, 60))
controller.buttonL2.released(control_motor, (0, arm_base_motor, 60))
# right buttons, second segment
controller.buttonR1.pressed(control_motor, (1, arm_joint_motor, 60))
controller.buttonR1.released(control_motor, (0, arm_joint_motor, 60))
controller.buttonR2.pressed(control_motor, (-1, arm_joint_motor, 60))
controller.buttonR2.released(control_motor, (0, arm_joint_motor, 60))
# claw 🦞
controller.buttonUp.pressed(control_motor, (1, claw_motor, 60))
controller.buttonUp.released(control_motor, (0, claw_motor, 60))
controller.buttonDown.pressed(control_motor, (-1, claw_motor, 60))
controller.buttonDown.released(control_motor, (0, claw_motor, 60))
# snow pile scooper ❄️
controller.buttonLeft.pressed(control_motor, (1, snow_motor, 50))
controller.buttonLeft.released(control_motor, (0, snow_motor, 50))
controller.buttonRight.pressed(control_motor, (-1, snow_motor, 50))
controller.buttonRight.released(control_motor, (0, snow_motor, 50))