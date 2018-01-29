# coding: utf-8
import numpy as np
import sys, os
import pickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import simpleclient as C
import RotRep as R
import Simulation as G

def my_mouse_data(data):
    return 'lol'

def my_coord_format(x,y):
    return 'hahahaha'

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Peak Explorer')
        self.res=None

        self.bfirstdraw=True
        self.photo=[None]*3
        self.vmin=15
        self.vmax=40
        self.omegaoffset=-1
        self.scatterarts=[]

        self._client=C.socketclient()
        self._xrd=C.XRD()



        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.load_default()

    def load_default(self):
        self.params=np.array([51.9957,81,3.7998e-7,-0.204599,0,
            328.93, 88.8624, 11.7176,
            1182.19,2026.27,
            7.14503,0,0,
            89.1588, 87.5647,0.278594])
        energy=self.params[0]
        etalimit=self.params[1]/180.0*np.pi
        pos=self.params[2:5]
        orien=R.EulerZXZ2Mat(self.params[5:8]/180.0*np.pi)
#        strain=np.array([ 0.00228725, -0.00046991, -0.00013953, -0.0001595 ,  0.00143135,
#                    0.00070123,  0.00089509,  0.00438468,  0.0014488 ])+np.array([ -1.66347153e-03,   9.19749189e-04,   8.19250063e-05,
#                                -1.33069566e-04,  -1.18838324e-03,  -2.40553445e-04,
#                                         1.67946465e-03,  -8.97547675e-03,  -8.87805809e-04])
        strain=np.zeros(9)
        strain=strain.reshape((3,3))+np.eye(3)
        orien=strain.dot(orien)
        Det=G.Detector()
        Det.Move(self.params[8],self.params[9],self.params[10:13],
                R.EulerZXZ2Mat(self.params[13:16]/180.0*np.pi))
        self._xrd.Setup(energy,etalimit,pos,orien,Det)
        self._xrd.Simulate()
        self.choosePeakID.setMinimum(0)
        self.choosePeakID.setMaximum(len(self._xrd.Peaks)-1)
        try:
            self.res=pickle.load(open('tmp_res.pickle','r'))
        except:
            self.res=[None]*len(self._xrd.Peaks)
        self.l0.setText('Setup finished')


    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self._canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    def save_res(self):
        file_choices = "Pickle (*.pickle)|*.pickle"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            pickle.dump(
                    {'res':self.res,
                        'xrd':self._xrd,
                        'param':self.params},open(path,'w'))
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def show_info(self):
        msg="""The parameters that are using:
        Energy(keV):      {0:.3f} 
        Eta limit(deg):   {1:.1f}
        J value:          {8:.3f} 
        K value:          {9:.3f}
        L value(mm):      {10:.5f} 
        Det orien(deg):   {13:.4f} {14:.4f} {15:.4f}

        voxel pos(mm):    {2:.7f}  {3:.7f}  {4:.0f}
        voxel orien(deg): {5:.4f}  {6:.4f}  {7:.4f}
        """.format(*self.params)
        QMessageBox.information(self,"Parameter information",msg.strip())
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())


    def on_draw(self):
        if self.bfirstdraw==True:
            self.imobjs=[]
            for ii in range(3):
                self.imobjs.append(self._axes[ii].imshow(self.photo[ii],
                    vmin=self.vmin,
                    vmax=self.vmax,
                    interpolation='nearest'))
                self.imobjs[ii].format_cursor_data=my_mouse_data
                self._axes[ii].format_coord=my_coord_format
            self.bfirstdraw=False
        else:
            for ii in range(3):
                self.imobjs[ii].set_data(self.photo[ii])
        self._canvas.draw()

        tmpid=self.choosePeakID.value()
        self.l2.setText('Omega ID of mid= {0:d}'.format(self.omegid+self.omegaoffset+1))
        self.l3.setText('Intensity of mid= {0:d}'.format(
            self.photo[1][int(self._xrd.Peaks[tmpid,1])-self.y1,
                int(2047-self._xrd.Peaks[tmpid,0])-self.x1]))

    def changeoffset(self,d):
        self.omegaoffset+=d
        if d > 0:
            for ii in range(2):
                self.photo[ii]=self.photo[ii+1]
            self.photo[2]=self._client.GetImg(self.omegid+self.omegaoffset+2,
                    self.y1,self.y2,self.x1,self.x2)
        else:
            for ii in [2,1]:
                self.photo[ii]=self.photo[ii-1]
            self.photo[0]=self._client.GetImg(self.omegid+self.omegaoffset,
                    self.y1,self.y2,self.x1,self.x2)
        self.on_draw()
            

    def enterPeakID(self):
        self.omegaoffset=-1
        tmpid=self.choosePeakID.value()
        if self.res[tmpid]!=None:
            self.l0.setText('Omega ID range: {0:d} ~ {1:d}'.format(*self.res[tmpid]))
        else:
            self.l0.setText('Omega ID range: not choose yet')
        self.omegid=int((180-self._xrd.Peaks[tmpid,2])*20)
        xran=200
        yran=100
        self.x1=max(0,int(2047-self._xrd.Peaks[tmpid,0]-xran))
        self.x2=min(self.x1+xran*2,2047)
        self.y1=max(0,int(self._xrd.Peaks[tmpid,1]-yran))
        self.y2=min(self.y1+yran*2,2047)
        while len(self.scatterarts)>0:
            self.scatterarts.pop().remove()
        for ii in range(3):
            self.photo[ii]=self._client.GetImg(self.omegid+self.omegaoffset+ii,
                    self.y1,self.y2,self.x1,self.x2)
            self.scatterarts.append(
                    self._axes[ii].scatter([int(2047-self._xrd.Peaks[tmpid,0])-self.x1],
                    [self.y2-int(self._xrd.Peaks[tmpid,1])],marker='x',c='k',s=20))

        self.on_draw()
        self.l1.setText('G= {0:f}'.format(np.linalg.norm(self._xrd.Gs[tmpid])))

    def on_mid(self):
        tmpid=self.choosePeakID.value()
        self.res[tmpid]=(self.omegid+self.omegaoffset+1,self.omegid+self.omegaoffset+1)
        self.l0.setText('Omega ID range: {0:d} ~ {1:d}'.format(*self.res[tmpid]))
        self.choosePeakID.setValue(tmpid+1)

    def on_middown(self):
        tmpid=self.choosePeakID.value()
        self.res[tmpid]=(self.omegid+self.omegaoffset+1,self.omegid+self.omegaoffset+2)
        self.l0.setText('Omega ID range: {0:d} ~ {1:d}'.format(*self.res[tmpid]))
        self.choosePeakID.setValue(tmpid+1)

    def on_pass(self):
        tmpid=self.choosePeakID.value()
        self.choosePeakID.setValue(tmpid+1)

    def on_notsure(self):
        tmpid=self.choosePeakID.value()
        self.res[tmpid]=(self.omegid+self.omegaoffset+1,self.omegid+self.omegaoffset+1,'NotSure')
        self.l0.setText('Omega ID range: {0:d} ~ {1:d}'.format(*self.res[tmpid]))
        self.choosePeakID.setValue(tmpid+1)

    def create_main_frame(self):
        self.main_frame=QWidget()
        self._fig=Figure()
        self._canvas=FigureCanvas(self._fig)
        self._canvas.setParent(self.main_frame)
        self._axes=[]
        for ii in range(3):
            self._axes.append(self._fig.add_subplot(3,1,ii+1))
        self._mpl_toolbar = NavigationToolbar(self._canvas, self.main_frame)

        self.l0=QLabel()
        self.l0.setText('Not Initialized')
        self.l1=QLabel()
        self.l1.setText('G=')
        self.l2=QLabel()
        self.l2.setText('Omega ID of mid=')
        self.l3=QLabel()
        self.l3.setText('Intensity of mid=')
        self.l3.setStyleSheet('color:red; font-weight:bold')

        self.choosePeakID=QSpinBox()
        self.choosePeakID.setValue(0)
        self.connect(self.choosePeakID,SIGNAL('valueChanged(int)'),self.enterPeakID)
        self.ls=QLabel()
        self.ls.setText('PeakID')
        hbox0=QHBoxLayout()
        hbox0.addWidget(self.ls)
        hbox0.addWidget(self.choosePeakID)

        self.up_button=QPushButton("up")
        self.connect(self.up_button,SIGNAL('clicked()'),lambda:self.changeoffset(-1))
        self.mid_button=QPushButton("choose mid frame")
        self.connect(self.mid_button,SIGNAL('clicked()'),self.on_mid)
        self.mid_button.setStyleSheet('background-color: yellow')
        self.middown_button=QPushButton("choose mid+down frame")
        self.connect(self.middown_button,SIGNAL('clicked()'),self.on_middown)
        self.middown_button.setStyleSheet('background-color: orange')
        self.pass_button=QPushButton("give up this peak")
        self.connect(self.pass_button,SIGNAL('clicked()'),self.on_pass)
        self.pass_button.setStyleSheet('background-color: red')
        self.notsure_button=QPushButton("choose mid frame but notsure")
        self.connect(self.notsure_button,SIGNAL('clicked()'),self.on_notsure)
        self.notsure_button.setStyleSheet('background-color: blue')
        self.down_button=QPushButton("down")
        self.connect(self.down_button,SIGNAL('clicked()'),lambda:self.changeoffset(+1))

        vbox0=QVBoxLayout()
        vbox0.addWidget(self.l0)
        vbox0.addWidget(self.l1)
        vbox0.addWidget(self.l2)
        vbox0.addWidget(self.l3)

        vbox1=QVBoxLayout()
        vbox1.addLayout(hbox0)
        vbox1.addWidget(self.up_button)
        vbox1.addWidget(self.down_button)
        vbox1.addWidget(self.mid_button)
        vbox1.addWidget(self.notsure_button)
        vbox1.addWidget(self.middown_button)
        vbox1.addWidget(self.pass_button)

        grid=QGridLayout()
        grid.addWidget(self._canvas,0,0,5,5)
        grid.addLayout(vbox0,0,5,3,1)
        grid.addLayout(vbox1,3,5,3,1)
        grid.addWidget(self._mpl_toolbar,5,0,1,5)
        self.main_frame.setLayout(grid)
        self.setCentralWidget(self.main_frame)
        return

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_default_action = self.create_action("&Load default Exp Setup",
            shortcut="Ctrl+D", slot=self.load_default, 
            tip="Default Setup is hard coded!")
        save_file_action = self.create_action("&Save Results",
            shortcut="Ctrl+S", slot=self.save_res, 
            tip="pickle the result and Exp setup")
        save_plot_action = self.create_action("&Save plot",
            shortcut="Ctrl+C", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (save_file_action,None, save_plot_action,None, load_default_action, None, quit_action))
        
        self.info_menu = self.menuBar().addMenu("&Info")
        info_action = self.create_action("&Params", slot=self.show_info)
        self.add_actions(self.info_menu,(info_action,))

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
    def closeEvent(self,event):
        self._client.Done()
        pickle.dump(self.res,open('tmp_res.pickle','w'))
        event.accept()


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
