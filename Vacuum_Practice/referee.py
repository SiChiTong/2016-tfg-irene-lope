import sys, math
from math import pi as pi
import numpy as np
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt5.QtGui import (QBrush, QConicalGradient, QLinearGradient, QPainter, QPainterPath, QPalette, QPen, QPixmap, QPolygon, QRadialGradient, QColor, QTransform, QPolygonF, QKeySequence, QIcon)
from PyQt5.QtWidgets import (QApplication, QProgressBar, QCheckBox, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QSpinBox, QWidget, QPushButton, QSpacerItem, QSizePolicy, QLCDNumber )
from parallelIce.pose3dClient import Pose3DClient
import easyiceconfig as EasyIce
from gui.threadGUI import ThreadGUI

class MainWindow(QWidget):

    updGUI=pyqtSignal()
    def __init__(self, pose3d, parent=None):
        super(MainWindow, self).__init__(parent)
        
        layout = QGridLayout()
        self.tiempo = tiempoWidget(self)
        self.porcentaje = porcentajeWidget(self, pose3d)
        #self.nota = notaWidget(self,pose3d)
        layout.addWidget(self.tiempo,0,0)
        layout.addWidget(self.porcentaje,0,2)
        #layout.addWidget(self.nota,0,1)
    
        vSpacer = QSpacerItem(30, 50, QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout.addItem(vSpacer,1,0)
        
        self.setFixedSize(740,240);

        self.setLayout(layout)
        self.updGUI.connect(self.update)

    def update(self):
        self.porcentaje.updateG()
        #self.nota.updateG()


class porcentajeWidget(QWidget):
    def __init__(self,winParent, pose3d):    
        super(porcentajeWidget, self).__init__()
        self.winParent=winParent
        self.pose3d = pose3d
        self.porcentajeCasa = 0

        vLayout = QVBoxLayout()

        self.porcentajeRecorrido()

        self.Porcentaje = QLabel("Porcentaje: " + str(round(self.porcentajeCasa, 3)) + ' %')

        vLayout.addWidget(self.Porcentaje, 0)

        self.setLayout(vLayout)


    def RTx(self, angle, tx, ty, tz):
        RT = np.matrix([[1, 0, 0, tx], [0, math.cos(angle), -math.sin(angle), ty], [0, math.sin(angle), math.cos(angle), tz], [0,0,0,1]])
        return RT
        
    def RTy(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), 0, math.sin(angle), tx], [0, 1, 0, ty], [-math.sin(angle), 0, math.cos(angle), tz], [0,0,0,1]])
        return RT
    
    def RTz(self, angle, tx, ty, tz):
        RT = np.matrix([[math.cos(angle), -math.sin(angle), 0, tx], [math.sin(angle), math.cos(angle),0, ty], [0, 0, 1, tz], [0,0,0,1]])
        return RT

    def RTCar(self):
        RTx = self.RTx(pi, 0, 0, 0)
        RTz = self.RTz(pi/2, 0, 0, 0)
        return RTx*RTz


    def porcentajeRecorrido(self):
        x = self.pose3d.getX()
        y = self.pose3d.getY()
        self.porcentajeCasa = 30

    def updateG(self):
        self.porcentajeRecorrido()
        self.Porcentaje.setText("Superficie recorrida: " + str(round(self.porcentajeCasa, 3)) + ' %')
        self.update()      
   
   
        
'''class notaWidget(QWidget):
    def __init__(self,winParent,pose3d):    
        super(notaWidget, self).__init__()
        self.winParent=winParent
        self.pose3d = pose3d

        hLayout = QHBoxLayout()
        
        if self.testTime():
            print ('seconds = 0')
    
        #notaTime = self.testTime() * 0.025
        #notaPorc = self.testPorcentaje() * 0.025
        nota = self.testPorcentaje()
        
        notaLabel = QLabel('Nota final: ' + str(nota))
        hLayout.addWidget(notaLabel, 0) 
        self.setLayout(hLayout)

        
    def testTime(self):
        time = tiempoWidget(self)
        seconds = time.seconds
        myTime = False
        while seconds > 0:
            print(seconds)
            seconds -= 1
        if seconds == 0:
            myTime = True
        return myTime
    
    def testPorcentaje(self):
        porcentaje = porcentajeWidget(self,pose3d)
        pCasa = porcentaje.porcentajeCasa
        if pCasa >= 90:
            notaPorc = 10
        elif pCasa < 90 and pCasa >= 75:
            notaPorc = 8
        elif pCasa < 75 and pCasa >= 60:
            notaPorc = 6
        elif pCasa < 60 and pCasa >= 50:
            notaPorc = 5
        else:
            notaPorc = 0
        return notaPorc

    def updateG(self):
        self.update() 
    '''
             

class tiempoWidget(QWidget):

    time = pyqtSignal()
    def __init__(self,winParent):    
        super(tiempoWidget, self).__init__()
        self.winParent=winParent
        self.seconds = 10
        self.pose3d = pose3d
        self.show = False

        self.hLayout = QHBoxLayout()
  
        tiempoLabel = QLabel("Tiempo")
        self.lcd = QLCDNumber(self)
        self.lcd.setMaximumSize(100,50)
        self.hLayout.addWidget(tiempoLabel,0)
        self.hLayout.addWidget(self.lcd, 1)

        hSpacer = QSpacerItem(300, 30, QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.hLayout.addItem(hSpacer)

        self.setLayout(self.hLayout)

        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.printTime)

        # get the palette
        palette = self.lcd.palette()

        # foreground color
        palette.setColor(palette.WindowText, QColor(85, 85, 255))
        # background color
        palette.setColor(palette.Background, QColor(0, 170, 255))
        # "light" border
        palette.setColor(palette.Light, QColor(255, 0, 0))
        # "dark" border
        palette.setColor(palette.Dark, QColor(0, 255, 0))

        # set the palette
        self.lcd.setPalette(palette)
        
    def showNota(self):
        self.show = True
        nota = self.testPorcentaje()
        notaLabel = QLabel('Nota final: ' + str(nota))
        self.hLayout.addWidget(notaLabel, 0) 
        self.setLayout(self.hLayout)

    def printTime(self):
        if self.seconds >0:
            self.seconds -= 1
        else:
            if not self.show:
                self.showNota()
        self.lcd.display(self.seconds)
    
    def testPorcentaje(self):
        porcentaje = porcentajeWidget(self,pose3d)
        pCasa = porcentaje.porcentajeCasa
        if pCasa >= 90:
            notaPorc = 10
        elif pCasa < 90 and pCasa >= 75:
            notaPorc = 8
        elif pCasa < 75 and pCasa >= 60:
            notaPorc = 6
        elif pCasa < 60 and pCasa >= 50:
            notaPorc = 5
        else:
            notaPorc = 0
        return notaPorc




if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    ic = EasyIce.initialize(sys.argv)
    pose3d = Pose3DClient(ic, "Vacuum.Pose3D", True)

    myGUI = MainWindow(pose3d)
    myGUI.show()
    t2 = ThreadGUI(myGUI)
    t2.daemon=True
    t2.start()
    sys.exit(app.exec_())
