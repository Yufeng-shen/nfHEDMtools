# coding: utf-8
import pickle
import h5py
import numpy as np
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import RotRep as R
from config_Qt import label as labelcfg
from config_Qt import zgap as zgapcfg
from config_Qt import xygrid as xycfg

class WorkingWindow(QMainWindow):
    def __init__(self, _mainwindow, parent=None):
        QWidget.__init__(self, parent)
        self.idx0=0
        self.idx1=0
        self.bfirstdraw=True
        self.setWindowTitle('Working Window')
        self.mainwindow=_mainwindow
        self.mymask0=self.mainwindow.Mask0[:,:,:,0].astype('bool')
        self.mymask1=self.mainwindow.Mask1[:,:,:,0].astype('bool')
        self.create_main_frame()
        self.create_status_bar()
        self.scattersets=[]
        self.s1hat=((self.mainwindow.s1[self.mainwindow.backnomatched])/np.array([xycfg,xycfg,zgapcfg])).astype(int)
        self.lastgraineuler=[0,0,0]
        self.labelpoints=[]
        self.s0labelID=[]
        self.s1labelID=[]
        self.labelres={}

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)

    def on_draw(self):
        """ Redraws the figure
        """

        self.idx0=self.sp0.value()
        self.idx1=self.sp1.value()
        alpha=self.mainwindow.slider.value()/100.0

        tmp0=self.mymask0[self.idx0]
        tmp1=self.mymask1[self.idx1]
        tmp0=np.stack((tmp0,tmp0,tmp0),axis=-1)
        tmp1=np.stack((tmp1,tmp1,tmp1),axis=-1)

        if self.bfirstdraw==True:
            self.imobj0=self.axes0.imshow(self.mainwindow.IPF0[self.idx0]*tmp0,interpolation='nearest',alpha=alpha,origin='lower')
            self.imobj1=self.axes1.imshow(self.mainwindow.IPF1[self.idx1]*tmp1,interpolation='nearest',alpha=alpha,origin='lower')
            self.bfirstdraw=False
        else:
            self.imobj0.set_data(self.mainwindow.IPF0[self.idx0]*tmp0)
            self.imobj0.set_alpha(alpha)
            self.imobj1.set_data(self.mainwindow.IPF1[self.idx1]*tmp1)
            self.imobj1.set_alpha(alpha)
        self.canvas.draw()
       
    def draw_scatter_trial(self):
        if len(self.scattersets)!=0:
            while len(self.scattersets)>0:
                self.scattersets[-1].remove()
                self.scattersets.pop()
            self.canvas.draw()
            return
        mask=np.where(self.s1hat[:,2]==self.idx1)
        candidate=self.s1hat[mask]
        self.axes1.autoscale(False)
        self.scattersets.append(self.axes1.scatter(candidate[:,0],candidate[:,1]))
        self.canvas.draw()

    def enterID0(self):
        tmpid=int(self.chooseID0.text())
        tmpshat=(self.mainwindow.s0[tmpid]/np.array([xycfg,xycfg,zgapcfg])).astype(int)
        self.axes0.autoscale(False)
        self.scattersets.append(self.axes0.scatter(tmpshat[0],tmpshat[1]))
        self.sp0.setValue(tmpshat[2])
        self.on_draw()
    def enterID1(self):
        tmpid=int(self.chooseID1.text())
        tmpshat=(self.mainwindow.s1[tmpid]/np.array([xycfg,xycfg,zgapcfg])).astype(int)
        self.axes1.autoscale(False)
        self.scattersets.append(self.axes1.scatter(tmpshat[0],tmpshat[1]))
        self.sp1.setValue(tmpshat[2])
        self.on_draw()

    def clean_label_points(self):
        self.s0labelID=[]
        self.s1labelID=[]
        while len(self.labelpoints)>0:
            self.labelpoints[-1].remove()
            self.labelpoints.pop()
        self.canvas.draw()
        return

    def change_idxs(self,cvalue):
        self.idx0+=cvalue
        self.sp0.setValue(self.idx0)
        self.idx1+=cvalue
        self.sp1.setValue(self.idx1)

    def on_grainpick(self):
        if self.bgrainpick.isChecked():
            self.cid=self.canvas.mpl_connect('button_press_event',self.on_click)
        else:
            self.canvas.mpl_disconnect(self.cid)

    def on_click(self,event):
        if event.inaxes==self.axes0:
            x=int(round(event.xdata))
            y=int(round(event.ydata))
            tmpid=self.mainwindow.ID0[self.idx0][y,x,0]
            tmpci=self.mainwindow.ci0[self.idx0][y,x,0]
            self.l0.setText("S0_ID= {:}, CI= {:}".format(tmpid,tmpci))
#            tmpe=self.mainwindow.e0[tmpid-1]
            tmpe=self.mainwindow.ce0[self.idx0][y,x]
#            print tmpe
            self.l3.setText("disorientation is: {:} deg".format(R.Misorien2FZ1(R.EulerZXZ2Mat(self.lastgraineuler)
                ,R.EulerZXZ2Mat(tmpe),'Cubic')[1]/np.pi*180))
            self.lastgraineuler=tmpe
            if self.bgrainlabel.isChecked():
                self.s0labelID.append(tmpid)
                self.labelpoints.append(self.axes0.scatter([x],[y],c='r'))
                self.canvas.draw()
        if event.inaxes==self.axes1:
            x=int(round(event.xdata))
            y=int(round(event.ydata))
            tmpid=self.mainwindow.ID1[self.idx1][y,x,0]
            tmpci=self.mainwindow.ci1[self.idx1][y,x,0]
#            corid=self.mainwindow.backcorID[tmpid]
            self.l1.setText("S1_ID= {:}, CI= {:} ".format(tmpid,tmpci))
#            self.l1.setText("S1_ID= {:}, CI= {:} (->  S0_ID= {:})".format(tmpid,tmpci,corid))
#            tmpe=self.mainwindow.e1[tmpid-1]
            tmpe=self.mainwindow.ce1[self.idx1][y,x]
#            print tmpe
            self.l3.setText("disorientation is: {:} deg".format(R.Misorien2FZ1(R.EulerZXZ2Mat(self.lastgraineuler)
                ,R.EulerZXZ2Mat(tmpe),'Cubic')[1]/np.pi*180))
            self.lastgraineuler=tmpe
            if self.bgrainlabel.isChecked():
                self.s1labelID.append(tmpid)
                self.labelpoints.append(self.axes1.scatter([x],[y],c='r'))
                self.canvas.draw()

    def save_label_points(self):
        tmpstr=unicode(self.setlabel.currentText())
        if tmpstr=='choose label':
            return
        if tmpstr=='customize':
            tmpstr=str(self.customizelabel.text())
        if tmpstr not in self.labelres:
            self.labelres[tmpstr]=[(self.s0labelID,self.s1labelID)]
        else:
            self.labelres[tmpstr].append((self.s0labelID,self.s1labelID))
        pickle.dump(self.labelres,open(labelcfg['outputfilename'],'wb'))
        for tid0 in self.s0labelID:
            self.mymask0[self.mainwindow.ID0[:,:,:,0]==tid0]=0
        for tid1 in self.s1labelID:
            self.mymask1[self.mainwindow.ID1[:,:,:,0]==tid1]=0
        self.clean_label_points()
        self.on_draw()
        return

#    def keyPressEvent(self,event):
#        key = event.key()
#        if key== Qt.Key_Down:
#            print('haha')
#        return

    def create_main_frame(self):

        self.main_frame = QWidget()
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.axes0 = self.fig.add_subplot(121)
        self.axes1 = self.fig.add_subplot(122)

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.bgrainpick = QCheckBox("Grain Info On")
        self.bgrainpick.setChecked(False)
        self.connect(self.bgrainpick, SIGNAL('stateChanged(int)'), self.on_grainpick)
        self.bgrainlabel = QCheckBox("Grain Label On")
        self.bgrainlabel.setChecked(False)
#        self.connect(self.bgrainlabel, SIGNAL('stateChanged(int)'), self.on_grainlabel)

        hbox2=QHBoxLayout()
        hbox2.addWidget(self.mpl_toolbar)
        hbox2.addWidget(self.bgrainpick)
        hbox2.addWidget(self.bgrainlabel)

        self.sp0=QSpinBox()
        self.sp0.setMinimum(0)
        self.sp0.setMaximum(len(self.mainwindow.ID0)-1)
        self.sp0.setValue(self.idx0)
        self.connect(self.sp0,SIGNAL('valueChanged(int)'),self.on_draw)

        self.sp1=QSpinBox()
        self.sp1.setMinimum(0)
        self.sp1.setMaximum(len(self.mainwindow.ID1)-1)
        self.sp1.setValue(self.idx0)
        self.connect(self.sp1,SIGNAL('valueChanged(int)'),self.on_draw)

        self.minus_button = QPushButton("& <-")
        self.connect(self.minus_button, SIGNAL('clicked()'),lambda: self.change_idxs(-1))
        self.plus_button = QPushButton("& ->")
        self.connect(self.plus_button, SIGNAL('clicked()'),lambda: self.change_idxs(+1))

        self.chooseID0=QLineEdit()
        self.chooseID0.setValidator(QIntValidator(1,len(self.mainwindow.s0)-1))
        self.connect(self.chooseID0,SIGNAL('returnPressed()'),self.enterID0)
        self.chooseID1=QLineEdit()
        self.chooseID1.setValidator(QIntValidator(1,len(self.mainwindow.s1)-1))
        self.connect(self.chooseID1,SIGNAL('returnPressed()'),self.enterID1)
        flo0 = QFormLayout()
        flo0.addRow("S0 grain ID =",self.chooseID0)
        flo1 = QFormLayout()
        flo1.addRow("S1 grain ID =",self.chooseID1)


        self.draw_button = QPushButton("unmatched grains on/off")
        self.connect(self.draw_button, SIGNAL('clicked()'),self.draw_scatter_trial)

        hbox = QHBoxLayout()
        hbox.addWidget(self.sp0)
        hbox.addWidget(self.minus_button)
        hbox.addWidget(self.draw_button)
        hbox.addWidget(self.plus_button)
        hbox.addWidget(self.sp1)

        self.l0=QLabel()
        self.l0.setText("Grain 0 information")
        self.l1=QLabel()
        self.l1.setText("Grain 1 information")
        self.l2=QLabel()
        self.l2.setText("label that grain as:")
        self.l3=QLabel()
        self.l3.setText("Disorientation:")
        self.clean_button = QPushButton("clean labeled grain")
        self.connect(self.clean_button, SIGNAL('clicked()'),self.clean_label_points)
        self.setlabel=QComboBox()
        tmp=["choose label","customize"]
        tmp.extend(labelcfg['labels'])
        self.setlabel.addItems(tmp)
        self.customizelabel=QLineEdit()
        self.customizelabel.setText("input customized label here")
        self.save_button = QPushButton("save labeled grain")
        self.connect(self.save_button, SIGNAL('clicked()'),self.save_label_points)

        grid = QGridLayout()
        grid.addWidget(self.l0,0,0,1,2)
        grid.addWidget(self.l1,0,2,1,2)
        grid.addWidget(self.l3,1,0,2,1)
        grid.addWidget(self.clean_button,1,1,1,1)
        grid.addWidget(self.setlabel,1,2,1,1)
        grid.addWidget(self.save_button,1,3,1,1)
        grid.addWidget(self.customizelabel,2,1,1,3)
        grid.addLayout(flo0,3,0,1,2)
        grid.addLayout(flo1,3,2,1,2)
#        hbox3.addWidget(self.setlabel)
        

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(grid)
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox2)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

        self.on_draw()

