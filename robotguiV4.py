
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\logno\Desktop\LOGAN\Research\Python\robotguiV2.ui'
#
# Created by: PyQt4 UI code generator 5.11.3
# Written By: Logan Norman
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QSlider, QRadioButton
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
							 QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QSlider)
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import serial
import math
import time
from datetime import datetime
import threading
from serial.tools.list_ports import comports
from serial.tools import hexlify_codec
import sys

# ports
# /dev/ttyACM1
# /dev/ttyACM0


global x1, x2, x3, x4, myUI, angle_rel, last_reading, line_rel, last_line_reading
x1,x2,x3,x4,myUI,angle_rel,last_reading,line_rel,last_line_reading=0,0,0,0,None,0,0,0,0

# option for input steering file
doSteering = False
steeringSteps = list()

# Stepper motor and disk information
disk_r   = 0.5*90 #cm
center   = (0,0)
#ball_inc = 0.2 #inches / rev
ball_inc = 0.508 # cm / rev
rot_inc = 1000./360 # step / deg

'''
@hunter
creating encoder emulator 
'''
#import Emulator as emu
#emulator = emu.Emulator()
def ask_for_port():
    """\
    Show a list of ports and ask the user for a choice. To make selection
    easier on systems with long device names, also allow the input of an
    index.
    """
    
    print("\n\033[1;31;47m ---  Currently available devices to readout:\033[0m \n")
    ports = []
    global index
    for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
        sys.stderr.write('    {:7}      {:20} {}\n'.format("index","Port","Device"))
        sys.stderr.write('--- {:2}      {:20} {}\n\n\n\n\n'.format(n, port, desc))
        ports.append(port)
    if(len(ports)==0):
       print("\n\033[1;31;47m --- There are no ports available ---\033[0m \n") 
    while True:
        pr = input('--- Enter port index: ')
        try:
            index = int(pr) - 1
            if not 0 <= index < len(ports):
                sys.stderr.write('--- Invalid index!\n')
                continue
            
        except ValueError:
           ask_for_port()
            
        port=ports[index]
        return port

print("Choose Arduino UNO")
port1=ask_for_port()
print("Choose Second Device")
port2=ask_for_port()

#ArduinoSerial = serial.Serial('/dev/ttyACM0', 115200) 
#EncSerial = serial.Serial('/dev/ttyACM1', 115200)

ArduinoSerial = serial.Serial(port1, 115200) 
EncSerial = serial.Serial(port2, 115200)
lock = threading.Lock()

class Ui_Dialog(QtCore.QObject):
	updatePosition = pyqtSignal()
	moveIt = pyqtSignal()
	stepperThread = None 
	currentStep = 0
	stepping = False

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.myCanvas = None
		self.position = {'x':0.0, 'y':0.0}
		self.target = None
		self.updatePosition.connect(self.update)
		self.moveIt.connect(self.doMove)

		#Linear Motion
		self.PositionTrack=0 # Linear Position Counter
		self.fPosFile="files/Position.txt" # Position of the Linear Portion
		self.fLogFile="files/LogFile.txt" # Each Move is Recorded here
		self.ArmLength=80 # length of the robot arm in cm
		self.Limit=40 # This is the limit prevents the collision to one side in cm

	#Bringing the Linear motion to zero
	def ZeroLinearPart(self):
		"Centering the source ..."
		#Forward
		if self.PositionTrack>0 and self.PositionTrack<=self.Limit:
			if self.PositionTrack<=15:
				print("Moving " + self.PositionTrack + " cm Backward")
				self.doBackward(self.PositionTrack)
				self.KeepTrackLinearPosition("e",self.PositionTrack)
			else:

				Reminder=self.PositionTrack%10
				for i in range(10,self.PositionTrack,10):
					print("Moving " + i + " cm Backward")
					self.doBackward(i)
					self.KeepTrackLinearPosition("e", i)
				if Reminder!=0:
					print("Moving " + Reminder + " cm Backward")
					self.doBackward(Reminder)
					self.KeepTrackLinearPosition("e", Reminder)
		elif self.PositionTrack>=-self.Limit and self.PositionTrack<0:
			self.PositionTrack=self.PositionTrack*-1
			if self.PositionTrack<=15:
				print("Moving " + self.PositionTrack + " cm Forward")
				self.doForward(self.PositionTrack)
				self.KeepTrackLinearPosition("f",self.PositionTrack)
			else:

				Reminder=self.PositionTrack%10
				for i in range(10,self.PositionTrack,10):
					print("Moving " + i + " cm Forward")
					self.doForward(i)
					self.KeepTrackLinearPosition("f", i)
				if Reminder!=0:
					print("Moving " + Reminder + " cm Forward")
					self.doForward(Reminder)
					self.KeepTrackLinearPosition("f", Reminder)





	#Gets CurrentPosition in cm
	def getCurrentPosition(self):
		fPosition=open(self.fPosFile,"r")
		Line=fPosition.readline()
		if Line!="":
			Breakit=Line.split(" ") 
			if self.PositionTrack==0:
				if Breakit[2]=="Forward":
					self.PositionTrack+=float(Breakit[1])
				elif Breakit[2]=="Backward":
					self.PositionTrack-=float(Breakit[1])

		else:
			self.PositionTrack=0
	#logs the Positions
	def KeepTrackLinearPosition(self,String,Value):
		fLogFile=open(self.fLogFile,"a+")
		fPosition=open(self.fPosFile,"w+")

		#Keeps Track of forward and backward positions

		if String=="e":
			fLogFile.write("Backward: " + str(Value) + " " + str(datetime.today()) + "\n")
			self.PositionTrack-=Value
		elif String=="f":
			fLogFile.write("Forward: " + str(Value) + " " + str(datetime.today()) + "\n")
			self.PositionTrack+=Value

		#Logs How far we are from the distance
		if(self.PositionTrack>0):
			fLogFile.write("DistanceToCenter: " + str(self.PositionTrack) + " Forward " + str(datetime) +"\n")
			fPosition.write("DistanceToCenter: " + str(self.PositionTrack) + " Forward " + str(datetime) +"\n")

		elif(self.PositionTrack<0):
			fLogFile.write("DistanceToCenter: " + str(-1*self.PositionTrack) + " Backward " + str(datetime) +"\n")
			fPosition.write("DistanceToCenter: " + str(-1*self.PositionTrack) + " Backward " + str(datetime) +"\n")
		fLogFile.close()
		fPosition.close()
	def getCanvas(self):
		return self.myCanvas

	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(903, 506)

		self.makeManualSteer(Dialog)
		self.makeLabels(Dialog)
		self.makeManualInput(Dialog)
		
		self.figure = plt.figure() # @hunter figsize=(350,350)
		self.myCanvas = PlotCanvas(Dialog, width=3.5, height=3.5)
		self.myCanvas.move(40,60)
		
		self.retranslateUi(Dialog)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

		self.connectThem()
		self.getCurrentPosition()

	def makeManualSteer(self, Dialog):
		self.butClockwise = QtWidgets.QPushButton(Dialog)
		self.butClockwise.setGeometry(QtCore.QRect(400, 50, 130, 50))
		self.butClockwise.setObjectName("butClockwise")
		self.butCounterbutClockwise = QtWidgets.QPushButton(Dialog)
		self.butCounterbutClockwise.setGeometry(QtCore.QRect(540, 50, 130, 50))
		self.butCounterbutClockwise.setObjectName("butCounterbutClockwise")
		self.butForward = QtWidgets.QPushButton(Dialog)
		self.butForward.setGeometry(QtCore.QRect(400, 140, 130, 50))
		self.butForward.setObjectName("butForward")
		self.butBackward = QtWidgets.QPushButton(Dialog)
		self.butBackward.setGeometry(QtCore.QRect(540, 140, 130, 50))
		self.butBackward.setObjectName("butBackward")
		self.butSetPosition = QtWidgets.QPushButton(Dialog)
		self.butSetPosition.setGeometry(QtCore.QRect(540, 220, 130, 50))
		self.butSetPosition.setObjectName("butSetPosition")
		self.butZero = QtWidgets.QPushButton(Dialog)
		self.butZero.setGeometry(QtCore.QRect(100, 420, 100, 50))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.butZero.setFont(font)
		self.butZero.setObjectName("butZero")
		self.butReset = QtWidgets.QPushButton(Dialog)
		self.butReset.setGeometry(QtCore.QRect(220, 420, 100, 50))
		font = QtGui.QFont()
		font.setPointSize(8)
		self.butReset.setFont(font)
		self.butReset.setObjectName("butReset")
		self.butQuit = QtWidgets.QPushButton(Dialog)
		self.butQuit.setGeometry(QtCore.QRect(450, 420, 120, 50))
		self.butQuit.setObjectName("butQuit")

		self.stepsForRotation = QtWidgets.QPlainTextEdit(Dialog)
		self.stepsForRotation.setGeometry(QtCore.QRect(700, 50, 120, 50))
		self.stepsForRotation.setObjectName("stepsForRotation")
		self.stepsForLinear = QtWidgets.QPlainTextEdit(Dialog)
		self.stepsForLinear.setGeometry(QtCore.QRect(700, 140, 120, 50))
		self.stepsForLinear.setObjectName("stepsForLinear")

		self.positionInputX = QtWidgets.QPlainTextEdit(Dialog)
		self.positionInputX.setGeometry(QtCore.QRect(420, 220, 110, 25))
		self.positionInputX.setObjectName("positionInputX")
		self.positionInputY = QtWidgets.QPlainTextEdit(Dialog)
		self.positionInputY.setGeometry(QtCore.QRect(420, 250, 110, 25))
		self.positionInputY.setObjectName("positionInputY")

		self.ledon = QtWidgets.QPushButton(Dialog)
		self.ledon.setGeometry(QtCore.QRect(700, 220, 130, 50))
		self.ledon.setObjectName("ledon")
		self.ledoff = QtWidgets.QPushButton(Dialog)
		self.ledoff.setGeometry(QtCore.QRect(700, 300, 130, 50))
		self.ledoff.setObjectName("ledoff")

	def makeLabels(self, Dialog):
		self.label = QtWidgets.QLabel(Dialog)
		self.label.setGeometry(QtCore.QRect(480, 20, 121, 31))
		font = QtGui.QFont()
		font.setPointSize(20)
		font.setBold(False)
		font.setWeight(50)
		self.label.setFont(font)
		self.label.setObjectName("label")
		self.label_2 = QtWidgets.QLabel(Dialog)
		self.label_2.setGeometry(QtCore.QRect(495, 110, 91, 31))
		font = QtGui.QFont()
		font.setPointSize(20)
		font.setBold(False)
		font.setWeight(50)
		self.label_2.setFont(font)
		self.label_2.setObjectName("label_2")
		self.label_3 = QtWidgets.QLabel(Dialog)
		self.label_3.setGeometry(QtCore.QRect(720, 20, 100, 31))
		font = QtGui.QFont()
		font.setPointSize(20)
		font.setBold(False)
		font.setWeight(50)
		self.label_3.setFont(font)
		self.label_3.setObjectName("label_3")
		self.label_4 = QtWidgets.QLabel(Dialog)
		self.label_4.setGeometry(QtCore.QRect(720, 110, 81, 31))
		font = QtGui.QFont()
		font.setPointSize(20)
		font.setBold(False)
		font.setWeight(50)
		self.label_4.setFont(font)
		self.label_4.setObjectName("label_4")
		self.label_5 = QtWidgets.QLabel(Dialog)
		#self.label_5.setGeometry(QtCore.QRect(485, 330, 100, 31))
		#font = QtGui.QFont()
		#font.setPointSize(20)
		#font.setBold(False)
		#font.setWeight(50)
		#self.label_5.setFont(font)
		#self.label_5.setObjectName("label_5")
		self.label_6 = QtWidgets.QLabel(Dialog)
		self.label_6.setGeometry(QtCore.QRect(400, 220, 20, 20))
		self.label_6.setObjectName("label_6")
		self.label_7 = QtWidgets.QLabel(Dialog)
		self.label_7.setGeometry(QtCore.QRect(400, 250, 20, 20))
		self.label_7.setObjectName("label_7")
		self.label_8 = QtWidgets.QLabel(Dialog)
		self.label_8.setGeometry(QtCore.QRect(650, 450, 120, 20))
		self.label_8.setObjectName("label_8")
		self.currentPositionLabel = QtWidgets.QLabel(Dialog)
		self.currentPositionLabel.setGeometry(QtCore.QRect(770, 450, 120, 20))
		self.currentPositionLabel.setObjectName("currentPositionLabel")

	def makeManualInput(self, Dialog):
		self.butRunStepper = QtWidgets.QPushButton(Dialog)
		self.butRunStepper.setGeometry(QtCore.QRect(400, 300, 130, 50))
		self.butRunStepper.setObjectName("butRunStepper")
		self.butResetStepper = QtWidgets.QPushButton(Dialog)
		self.butResetStepper.setGeometry(QtCore.QRect(540, 300, 130, 50))
		self.butResetStepper.setObjectName("butResetStepper")

	def retranslateUi(self, Dialog):
		global x1

		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
		self.butClockwise.setText(_translate("Dialog", "Clockwise"))
		self.butCounterbutClockwise.setText(_translate("Dialog", "CounterClockwise"))
		self.butForward.setText(_translate("Dialog", "Forward"))
		self.butBackward.setText(_translate("Dialog", "Backward"))
		self.label.setText(_translate("Dialog", "Rotation"))
		self.label_2.setText(_translate("Dialog", "Linear"))
		self.label_3.setText(_translate("Dialog", "degrees"))
		self.label_4.setText(_translate("Dialog", "cm"))
		#self.label_5.setText(_translate("Dialog", "Position"))
		self.label_6.setText(_translate("Dialog", "X :"))
		self.label_7.setText(_translate("Dialog", "Y :"))
		self.butZero.setText(_translate("Dialog", "zero"))
		self.butReset.setText(_translate("Dialog", "reset"))
		self.stepsForRotation.setPlainText(_translate("Dialog", "0"))
		self.stepsForLinear.setPlainText('0')
		self.butQuit.setText(_translate("Dialog", "quit"))
		self.positionInputX.setPlainText('0')
		self.positionInputY.setPlainText('0')
		self.butSetPosition.setText(_translate("Dialog", "Set position"))
		self.label_8.setText(_translate("Dialog", "Current position: "))
		temp = '('+str(self.position['x'])+','+str(self.position['y'])+','+str(x1)+')'
		self.currentPositionLabel.setText(_translate("Dialog", temp))
		self.butRunStepper.setText(_translate("Dialog", "Start Stepper"))
		self.butResetStepper.setText(_translate("Dialog", "Reset Stepper"))
		self.ledon.setText(_translate("Dialog", "LED On"))
		self.ledoff.setText(_translate("Dialog", "LED Off"))
		
	def update(self):
		global x1

		_translate = QtCore.QCoreApplication.translate
		temp = "({:.2f}, {:.2f}, {:.2f})".format(self.position['x'], self.position['y'], x1)
		self.currentPositionLabel.setText(_translate("Dialog", temp))
		# update the file
		with open('currentPosition.txt', 'w') as f:
			f.write(str(self.position['x'])+' '+str(self.position['y']))
	
	def doResetStepper(self):
		self.currentStep = 0
	
	def doStartStepper(self):
		_translate = QtCore.QCoreApplication.translate
		if not self.stepping:
			self.butRunStepper.setText(_translate("Dialog", "Stop Stepper"))
			self.stepping = True
			self.stepperThread = threading.Thread(target=self.doStep)
			self.stepperThread.daemon = True
			self.stepperThread.start()
		else:
			self.stepping = False
			self.butRunStepper.setText(_translate("Dialog", "Start Stepper"))

	def doStep(self):
		while self.stepping and self.currentStep < len(steeringSteps):
			x,y = steeringSteps[self.currentStep]
			self.target = {'x':x, 'y':y}
			self.moveIt.emit()
			time.sleep(2) # we need time to get there
			self.currentStep += 1

	def doQuit(self):
		self.ZeroLinearPart()
		QtCore.QCoreApplication.instance().quit()
	
	def doSetPosition(self):
		'''
		Set the position manually.
		'''
		x,y = float(self.positionInputX.toPlainText()), float(self.positionInputY.toPlainText())
		self.target = {'x':x, 'y':y}
		self.moveIt.emit()

	def doMove(self):
		currentX, currentY = self.position['x'], self.position['y']
		targetX, targetY   = self.target['x'], self.target['y']

		# compute the angle
		import numpy as np
		currentAngle = np.angle(currentX + currentY * 1j, deg = True)
		targetAngle  = np.angle(targetX + targetY * 1j, deg = True)
		
		deltaTheta = targetAngle - currentAngle
		deltaDist  = (targetX**2+targetY**2)**0.5 - (currentX**2+currentY**2)**0.5

		# how many steps?
		angleSteps = deltaTheta
		distSteps  = deltaDist

		print("Moving to X = {} Y = {} in {} angle steps and {} linear steps".format(targetX, targetY, angleSteps, distSteps))
		_translate = QtCore.QCoreApplication.translate
		self.stepsForRotation.setPlainText(_translate("Dialog", str(abs(angleSteps))))
		self.stepsForLinear.setPlainText(_translate("Dialog", str(abs(distSteps))))
		print(deltaDist, deltaTheta)
		if angleSteps < 0:
			self.doCounterClockwise()
		else:
			self.doClockwise()
		if distSteps < 0:
			self.doBackward()
		else:
			self.doForward()
		self.position = {'x':targetX, 'y':targetY}
		self.update()

	def doSerialWrite(self, var, value, sleep=0.1):
		# convert linear steps to units of distance
		# was n x 1000 for n revolutions
		passThis = str(value) #textEdit.toPlainText())
		Stop=0
		# linear/radial change
		if var == 'e' or var == 'f':
			dist = float(self.stepsForLinear.toPlainText())
			rev = dist/ball_inc
			steps = rev*1000
			passThis = str(steps)

			if (dist>=self.Limit or self.PositionTrack>=self.Limit or self.PositionTrack<=(-self.Limit)):
				print("You may have reached the limit!")
				print("You are " + str(self.PositionTrack) + " cm away from center. Limit is + and - " + str(self.Limit) + " cm")
				Stop=1
			else:
				self.KeepTrackLinearPosition(var,value)
				Stop=0



		elif var == 'a' or var == 'b':
			steps = rot_inc * value
			passThis = str(steps)
			Stop=0

		if Stop!=1:
			print('writing', var, passThis)
			ArduinoSerial.write(var.encode())
			time.sleep(sleep)
			ArduinoSerial.write(passThis.encode())
		else:
			print("You have Reached the Linear Limit!!!")
	def doClockwise(self, value=False):
		print("Clockwise")
		# default to option in text box
		if not value:
			value = float(self.stepsForRotation.toPlainText())
		self.doSerialWrite('b', value, sleep=0.1)

	def doCounterClockwise(self, value=False):
		print("CounterClockwise")
		# default to option in text box
		if not value:
			value = float(self.stepsForRotation.toPlainText())
		self.doSerialWrite('a', value, sleep=0.1)
		
	def doBackward(self, value=False):
		print("Backward")
		# default to option in text box
		if not value:
			value = float(self.stepsForLinear.toPlainText())
		self.doSerialWrite('e', value, sleep=0.1)
		self.shiftPosition(lin=value) #float(self.stepsForLinear.toPlainText()))

	def doForward(self, value=False):
		print("Forward")
		# default to option in text box
		if not value:
			value = float(self.stepsForLinear.toPlainText())
		self.doSerialWrite('f', value, sleep=0.1)
		self.shiftPosition(lin=value)
		
	def shiftPosition(self, rot=None, lin=None):
		import numpy as np
		currentX, currentY = self.position['x'], self.position['y']
		currentR = (currentX**2+currentY**2)**0.5
		currentAngle = np.angle(currentX + currentY * 1j, deg = True)

		# rotation 
		if rot is not None:
			targetAngle  = currentAngle+rot
			self.position['x'] = currentR*np.cos(targetAngle*np.pi/180.)
			self.position['y'] = currentR*np.sin(targetAngle*np.pi/180.)
			currentAngle = targetAngle

		# linear
		if lin is not None:
			targetR = currentR+lin
			self.position['x'] = targetR*np.cos(currentAngle*np.pi/180.)
			self.position['y'] = targetR*np.sin(currentAngle*np.pi/180.)
		print(currentX,currentY,self.position)
		self.updatePosition.emit()
	
	def doZero(self):
		print("zero")

		# do large angle rotation
		self.doCounterClockwise(200.) 

	def doReset(self):
		global x1, x2, x3, x4, last_reading, angle_rel, line_rel, last_line_reading

		print("reset")

		angle_rel = last_reading
		line_rel = last_line_reading
		print('Angle rel =', angle_rel)
		self.getCanvas().plot(0, 0, 0, 0)

	def doledon(self):
		self.doSerialWrite('k', 1, sleep=0.1)

	def doledoff(self):
		self.doSerialWrite('k', 2, sleep=0.1)
	
	def connectThem(self):
		self.butClockwise.clicked.connect(self.doClockwise)
		self.butCounterbutClockwise.clicked.connect(self.doCounterClockwise)
		self.butForward.clicked.connect(self.doForward)
		self.butZero.clicked.connect(self.doZero)
		self.butReset.clicked.connect(self.doReset)
		self.butBackward.clicked.connect(self.doBackward)
		self.butQuit.clicked.connect(self.doQuit)
		self.butSetPosition.clicked.connect(self.doSetPosition)
		self.butRunStepper.clicked.connect(self.doStartStepper)
		self.butResetStepper.clicked.connect(self.doResetStepper)
		self.ledon.clicked.connect(self.doledon)
		self.ledoff.clicked.connect(self.doledoff)		
				

class PlotCanvas(FigureCanvas):

	def __init__(self, parent=None, width=3.2, height=3.2, dpi=100):
		
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
 
		FigureCanvas.__init__(self, fig)
		self.setParent(parent)
	
		FigureCanvas.setSizePolicy(self,
								   QSizePolicy.Expanding,
								   QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		self.plot(x1, x2, x3, x4)
 
	def plot(self, x1, x2, x3, x4):
		'''
		Plotting information from arduino.
		xi: encoder counts, translates to degrees
		Units will be in cm
		Disk diameter ~ 100 cm
		'''
		
		assert type(x1) == int, 'x1 is not a int!'
		print(x1, x2, x3, x4)

		ax = self.figure.add_subplot(111)
		ax.cla()
		circle = plt.Circle((0, 0), disk_r, color='b', fill=False)
		ax.set_xlim((-disk_r, disk_r))
		ax.set_ylim((-disk_r, disk_r))
		ax.add_artist(circle)
		
		def limits(ang):
			xh, xl = center[0] + disk_r * math.cos(ang), center[0] - disk_r * math.cos(ang)
			yh, yl = center[1] + disk_r * math.sin(ang), center[1] - disk_r * math.sin(ang)
			return [xl,xh],[yl,yh]
		
		linang1 = int(x1)
		linang1 = linang1 * math.pi / 180.
		xlim, ylim = limits(-1*linang1)
		ax.plot([xlim[0], xlim[1]], [ylim[0],ylim[1]], 'r')
		
		dist1 = ball_inc * int(x3) / 360.
		xl = center[0] + dist1 * math.cos(linang1)
		yl = center[1] - dist1 * math.sin(linang1)
		ax.plot(xl,yl, 'r*')
		
		self.draw()
		return xl,yl
		
if doSteering:
	with open('steering.txt') as f:
		while True:
			lineVec = f.readline().split()
			if len(lineVec) < 1:
				break
			x,y = float(lineVec[0]),float(lineVec[1])
			steeringSteps.append([x,y])

 
def reading():
	global myUI, x1, x2, x3, x4, angle_rel, last_reading, line_rel, last_line_reading

	while True:
		with lock:
			raw_reading = EncSerial.readline()

		DATASPLIT= raw_reading.decode('utf-8').split(' , ')
		if (len(DATASPLIT)==5):
			 
			_x1, _x2, _x3, _x4 = DATASPLIT[0], DATASPLIT[2], DATASPLIT[1], DATASPLIT[3]
		else:
			print(DATASPLIT)
			continue  
	
		try:
			_x1, _x2, _x3, _x4 = int(_x1), int(_x2), int(_x3), int(_x4)
		except:
			time.sleep(1)
			continue

		
		x1, x2, x3, x4 = _x1 - angle_rel, _x2, _x3 - line_rel, _x4
		print(_x1, x1, last_reading, angle_rel)
		last_reading = _x1
		last_line_reading = _x3

		if myUI is not None:
			if myUI.getCanvas() is not None:
				x,y = myUI.getCanvas().plot(x1, x2, x3, x4)
				myUI.position['x'] = x
				myUI.position['y'] = y
				myUI.updatePosition.emit()
		else:
			print('Warning: MyUI not initialized!')

reading_thread = threading.Thread(target=reading) # @hunter , daemon=True)
reading_thread.daemon = True
reading_thread.start()

def getPosition():
	global myUI
	return myUI.position



def run():
	global myUI
	import sys

	app = QtWidgets.QApplication(sys.argv)
	Dialog = QtWidgets.QDialog()
	myUI = Ui_Dialog()
	myUI.setupUi(Dialog)
	Dialog.show()
	sys.exit(app.exec_())

