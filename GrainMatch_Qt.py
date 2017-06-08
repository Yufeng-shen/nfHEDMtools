# coding: utf-8
import h5py
import numpy as np
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class WorkingWindow(QMainWindow):
    def __init__(self, _mainwindow, parent=None):
        QWidget.__init__(self, parent)
        self.idx0=0
        self.idx1=0
        self.bfirstdraw=True
        self.setWindowTitle('Working Window')
        self.mainwindow=_mainwindow
        self.create_main_frame()
        self.create_status_bar()

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)

    def on_draw(self):
        """ Redraws the figure
        """

        self.idx0=self.sp0.value()
        self.idx1=self.sp1.value()
        alpha=self.mainwindow.slider.value()/100.0

        tmp0=self.mainwindow.Mask0[self.idx0][:,:,0]
        tmp1=self.mainwindow.Mask1[self.idx1][:,:,0]
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
        x=int(round(event.xdata))
        y=int(round(event.ydata))
        if event.inaxes==self.axes0:
            self.l0.setText("ID:{:}".format(self.mainwindow.ID0[self.idx0][y,x,0]))
        if event.inaxes==self.axes1:
            self.l1.setText("ID:{:}".format(self.mainwindow.ID1[self.idx1][y,x,0]))

    def create_main_frame(self):

        self.main_frame = QWidget()
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        self.axes0 = self.fig.add_subplot(121)
        self.axes1 = self.fig.add_subplot(122)

        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        self.bgrainpick = QCheckBox("Pick Grain On")
        self.bgrainpick.setChecked(False)
        self.connect(self.bgrainpick, SIGNAL('stateChanged(int)'), self.on_grainpick)

        hbox2=QHBoxLayout()
        hbox2.addWidget(self.mpl_toolbar)
        hbox2.addWidget(self.bgrainpick)

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

        self.l0=QLabel()
        self.l0.setText("Grain 0 information")
        self.l1=QLabel()
        self.l1.setText("Grain 1 information")

        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'),self.on_draw)

        hbox = QHBoxLayout()
        hbox.addWidget(self.sp0)
        hbox.addWidget(self.l0)
        hbox.addWidget(self.minus_button)
        hbox.addWidget(self.draw_button)
        hbox.addWidget(self.plus_button)
        hbox.addWidget(self.l1)
        hbox.addWidget(self.sp1)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.canvas)
#        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox2)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

        self.on_draw()

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Grain Matching')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

    def load_default(self):
        self.a0 = h5py.File('/home/fyshen13/Downloads/AngFiles_Anneal0_Output/Segment_15_2deg_27.dream3d')
        self.ID0=self.a0['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF0=self.a0['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        self.Mask0=self.a0['DataContainers']['ImageDataContainer']['CellData']['Mask']

        self.a1 = h5py.File('/home/fyshen13/Downloads/AngFiles_Anneal1_Output/Segment_match_2deg_27.dream3d')
        self.ID1=self.a1['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF1=self.a1['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        self.Mask1=self.a1['DataContainers']['ImageDataContainer']['CellData']['Mask']

        self.workingwindow=WorkingWindow(_mainwindow=self)
        self.workingwindow.show()
    def load_plot(self):
        file_choices = "DREAM3D (*.dream3d)"
        filename0 = unicode(QFileDialog.getOpenFileName(self,
                'Load state 0 file','',file_choices))
        self.a0 = h5py.File(filename0)
        self.ID0=self.a0['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF0=self.a0['DataContainers']['ImageDataContainer']['CellData']['IPFColor']
        filename1 = unicode(QFileDialog.getOpenFileName(self,
                'Load state 1 file','',file_choices))
        self.a1 = h5py.File(filename1)
        self.ID1=self.a1['DataContainers']['ImageDataContainer']['CellData']['FeatureIds']
        self.IPF1=self.a1['DataContainers']['ImageDataContainer']['CellData']['IPFColor']

        self.workingwindow=WorkingWindow(_mainwindow=self)
        self.workingwindow.show()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
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
    

    def create_main_frame(self):
        self.main_frame=QWidget()
#        self.canvas.mpl_connect('button_press_event',self.on_button)
        # Bind the 'pick' event for clicking on one of the bars
        #
#        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        
        # Other GUI controls
        # 
#        self.textbox = QLineEdit()
#        self.textbox.setMinimumWidth(200)
##        self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
#        
#        self.draw_button = QPushButton("&Draw")
#        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
#        
#        self.grid_cb = QCheckBox("Show &Grid")
#        self.grid_cb.setChecked(False)
#        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
#        
        slider_label = QLabel('alpha (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
#        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
#        hbox = QHBoxLayout()
#        
#        for w in [  self.textbox, self.draw_button, self.grid_cb,
#                    slider_label, self.slider]:
#            hbox.addWidget(w)
#            hbox.setAlignment(w, Qt.AlignVCenter)
#        
#        vbox = QVBoxLayout()
#        vbox.addWidget(self.canvas)
#        vbox.addWidget(self.mpl_toolbar)
#        vbox.addLayout(hbox)
#        
#        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.slider)
        return

    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_default_action = self.create_action("&Load default dream3d",
            shortcut="Ctrl+D", slot=self.load_default, 
            tip="Load the dream3d file")
        load_file_action = self.create_action("&Load dream3d",
            shortcut="Ctrl+L", slot=self.load_plot, 
            tip="Load the dream3d file")
        save_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (save_file_action,None, load_file_action,None, load_default_action, None, quit_action))
        
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


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
