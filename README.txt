Written By: Logan Norman
Date: 8/18/2021

HELLO! Thank you for volunteering to work with the robot, I (Logan) built it, she ain't perfect, but 
it was the first robot I built so hopefully it's not too frustrating. I began wrting the program and 
then it was improved by a member of another group named Hunter, hence you will see his name in the 
program as well. 

To Use the RobotguiV4.py program you will need python3 or above and the following modules:

	PyQt5
	matplotlib
	serial
	math
	time
	datetime
	sys

All of which can be installed using the pip install method and the above names.

To run the gui make sure to have the two Arduinos connected to your system,
then navigate to this folder titled "Robot" and run the command:

	~ python RUN_MOTOR.py

The system will prompt you to choose a comport from the list provided, this depends on which 
number comport your system assigned the arduinos. 

Once you have picked one of the arduinos it will prompt you to choose the second comport.

Since one arduino controls the motor and one controls the encoders the correct comports need to
be chosen.

To figure out which is which I would arbitrarily choose one and then once the gui opens I 
attempt to move one of the  motors and if nothing happens quit the program, restart and swap 
the comports. 

This is relatively arbitrary and a takes a maximum  of one round of trial and error to figure 
out, usually.

The program is relatively simple to use, just input the amount of degrees you would like the robot arm to
rotate through and select the direction you would like it to rotate through clicking the clockwise or 
counterclockwise buttons.

The linear portion is the exact same but using centimeters and the forward and backward buttons, with 
forward being the direction to the right if the arm is sitting at zero degrees. 

To zero the arm the function is not perfect, but you would press the zero button and the  arm will rotate
counterclockwise for a certain amount of steps which should exceed the rotation of the arm in general and
it will hit a stop that will locate it at zero, if you find it does not quite get to zero you could press 
the zero button again or perhaps change the amount of steps it rotates through in the program. 

Once you are sure the robot is located at the center you can press the reset button which resets the plot 
and stored location value. 

WARNING!! The reset button will also reset the location of the linear dot so be sure it is located in the 
center before pressing the reset button

Now the robot is not built absolutely perfectly so occasionally you may tell the robot to go to 45 degrees
or 60 and you will see the plot go forward and get there but then fall back a bit, now this should not be a
problem because the program tracks the position from the encoders which tell you the real position not the 
desired position.The only caveat is if you want it to be in a certain position you may have to nudge it little 
by little until you see the plot reflect the position you desire. 