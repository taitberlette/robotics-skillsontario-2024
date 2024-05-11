# import the vex stuff 🤖
from vex import *

# main computer 🧠
brain = Brain()

# radio controller (automatically set up by the brain) 🎮
controller = Controller()

# wheels
left_drive = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_drive = Motor(Ports.PORT3, GearSetting.RATIO_18_1, True)

# auxiliary motors
claw_motor = Motor(Ports.PORT12, GearSetting.RATIO_18_1, False)
rack_motor = Motor(Ports.PORT5, GearSetting.RATIO_18_1, False)
tray_motor = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
gate_motor = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)

# keep track of speed mode settings
speed = False
# keep track of whether the gate was open or not
open = False

# toggle between speed and regular mode 
def toggle_speed():
  global speed
  speed = (False if speed else True)
  
# reset the tray gate motor
def recalibrate():
    gate_motor.reset_position() 

# move a motor (see event description below!)
def control_motor(direction, motor, percent):
  motor.spin(FORWARD, direction * percent, PERCENT)


# main driving/controlling thread
def drive_task():
    # loop forever until the end of time ⌛
    while True:
				# get the value of the two joysticks
        left_joystick_y = controller.axis3.position()
        right_joystick_x = controller.axis1.position()

        # remap the controller values
        steer = abs(right_joystick_x) / 5
        speed = (10 + abs(left_joystick_y/2.5)) / (0.55 if speed else 1)
        turningSpeed = (4 if speed else 3)

        # get the angle of the gate
        angle = gate_motor.position(DEGREES) % 360

        # make sure to only update when it changes, otherwise we spam the controller with messages with lags the robot 💀
        global open
        if(angle < 30 or angle > 330) and open == True:
            controller.screen.clear_screen()
            controller.screen.set_cursor(1, 0)
            controller.screen.print("Closed")
            open = False
        elif(angle >= 30 and angle <= 330) and open == False:
            controller.screen.clear_screen()
            controller.screen.set_cursor(1, 0)
            controller.screen.print("Open")
            open = True

        # use a little buffer room to account for wonky controller drift

        # forwards ⬆️
        if left_joystick_y > 5:
          # turn while going forwards
          if right_joystick_x > 5:
              left_drive.spin(FORWARD, speed + steer, PERCENT)
              right_drive.spin(FORWARD, speed - steer, PERCENT)
          elif right_joystick_x < -5:
              left_drive.spin(FORWARD, speed - steer, PERCENT)
              right_drive.spin(FORWARD, speed + steer, PERCENT)
          
          # forwards in a straight line
          else:
              left_drive.spin(FORWARD, speed, PERCENT)
              right_drive.spin(FORWARD, speed, PERCENT)
          
        # backwards ⬇️
        elif left_joystick_y < -5:
            # turn while going backwards
            if right_joystick_x > 5:
                left_drive.spin(REVERSE, speed - steer, PERCENT)
                right_drive.spin(REVERSE, speed + steer, PERCENT)
            elif right_joystick_x < -5:
                left_drive.spin(REVERSE, speed + steer, PERCENT)
                right_drive.spin(REVERSE, speed - steer, PERCENT)
            
            # backwards in a straight line
            else:
                left_drive.spin(REVERSE, speed, PERCENT)
                right_drive.spin(REVERSE, speed, PERCENT)
            
        # spin in place 💫
        elif right_joystick_x > 15:
            left_drive.spin(FORWARD, speed * turningSpeed, PERCENT)
            right_drive.spin(REVERSE, speed * turningSpeed, PERCENT)
        elif right_joystick_x < -15: 
            left_drive.spin(REVERSE, speed * turningSpeed, PERCENT)
            right_drive.spin(FORWARD, speed * turningSpeed, PERCENT)
        
        # no inputs, stop 🛑
        else:
            left_drive.stop() 
            right_drive.stop()


        # a little delay just for fun 😇
        sleep(10)


# Run the drive code
drive = Thread(drive_task)

# setup the claw motor
claw_motor.set_stopping(HOLD)

# when the a button is pressed, toggle speed mode
controller.buttonA.pressed(toggle_speed)

# when the b button is pressed, reset the position of the gate (do this when the gate is down/closed)
controller.buttonB.pressed(recalibrate)

# move the different motors
# left buttons, the rack and pinion
controller.buttonL1.pressed(control_motor, (1, rack_motor, 100))
controller.buttonL1.released(control_motor, (0, rack_motor, 100))
controller.buttonL2.pressed(control_motor, (-1, rack_motor, 100))
controller.buttonL2.released(control_motor, (0, rack_motor, 100))
# right buttons, tray
controller.buttonR1.pressed(control_motor, (1, tray_motor, 100))
controller.buttonR1.released(control_motor, (0, tray_motor, 100))
controller.buttonR2.pressed(control_motor, (-1, tray_motor, 100))
controller.buttonR2.released(control_motor, (0, tray_motor, 100))
# claw 🦞
controller.buttonUp.pressed(control_motor, (1, claw_motor, 100))
controller.buttonUp.released(control_motor, (0, claw_motor, 100))
controller.buttonDown.pressed(control_motor, (-1, claw_motor, 100))
controller.buttonDown.released(control_motor, (0, claw_motor, 100))
# tray gate ⛔
controller.buttonLeft.pressed(control_motor, (1, gate_motor, 25))
controller.buttonLeft.released(control_motor, (0, gate_motor, 25))
controller.buttonRight.pressed(control_motor, (-1, gate_motor, 25))
controller.buttonRight.released(control_motor, (0, gate_motor, 25))