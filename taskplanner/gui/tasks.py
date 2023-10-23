'''
This module defines a task widget.
'''

#%% Imports
from PyQt5.QtCore import Qt, QRect
from PyQt5.Qt import QFont
from PyQt5.QtWidgets import \
(
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QBoxLayout,
    QGridLayout,
    QWidget,
    QScrollArea
    )
from taskplanner.tasks import Task
import os

import sys
current_path = "/".join(__file__.split('/')[:-1])
stylesheets_path = os.path.join(current_path, 'stylesheets')
class TaskWidget(QWidget):
    '''
    This class defines a task widget.
    '''
    def __init__(self,
                 task:Task,
                 main_color:str=None):
        '''
        :param task: :py:class:'taskplanner.tasks.Task'
            The task associated to this widget
        :param main_color: str, optional
            The main color of this task and all sub-tasks
        '''
        self.task, self.main_color = task, main_color
        super().__init__()
        # Layout
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)
        # Geometry
        self.setFixedHeight(1000)
        self.setFixedWidth(1200)
        # Toolbar
        self.make_toolbar()
        # Style
        #file = open(os.path.join(stylesheets_path, 'TaskWidget/standard-view/main-layout.css'))
        #self.setStyleSheet(file.read())
        #file.close()
        self.setStyleSheet(
        '''
        QWidget
        {
            background-color:white;
            border: 2px solid #D8D9DA;
            border-radius: 5px;
            font:Sans Serif;
        }
        ''')
    def make_toolbar(self):
        class Toolbar(QWidget):
            '''
            The toolbar contains:

                - A pushbutton to mark the task as completed
                - A pushbutton to close the Task view

            :return:
            '''
            def __init__(self, parent):
                super().__init__()
                self.task_widget = parent
                self.layout = QHBoxLayout()
                self.setLayout(self.layout)
                # Geometry
                x, y, w, h = [getattr(self.task_widget.geometry(), x)() for x in ['x',
                                                                                  'y',
                                                                                  'width',
                                                                                  'height']]
                self.setFixedSize(int(w), int(h * 0.1))
                # Make sub-widgets
                self.make_completed_pushbutton()
                self.make_close_pushbutton()
                # Style
                self.setAttribute(Qt.WA_StyledBackground, True)
                self.setStyleSheet(
                    '''
                    QWidget{
                        background-color:#F1F6F9;
                        font-size:10pt;
                        border:0px;
                        color:#61677A;
                    }
                    ''')

            def make_completed_pushbutton(self):
                #Pushbutton to mark the task as completed
                self.completed_pushbutton = QPushButton('Mark Completed')
                self.layout.addWidget(self.completed_pushbutton)

                def completed_pushbutton_clicked():
                    if self.completed_pushbutton.text() == 'Mark Completed':
                        self.completed_pushbutton.setText('Completed')
                        self.task_widget.task.completed = True
                    else:
                        self.completed_pushbutton.setText('Mark Completed')
                        self.task_widget.task.completed = False
                self.completed_pushbutton.clicked.connect(completed_pushbutton_clicked)
                # Geometry
                self.completed_pushbutton.setFixedSize(int(self.width()*0.25),
                                                       int(self.height()*0.5))
                # Style
                self.completed_pushbutton.setStyleSheet(
                '''
                QPushButton
                {
                    border:2px solid #61677A;
                    border-radius:5px;
                }   
                QPushButton:hover{
                    background-color:#7AA874;
                    color:white;
                }
                QPushButton:clicked{
                    background-color:#7AA874;
                }
                ''')

            def make_close_pushbutton(self):
                # Pushbutton to close the task view
                self.close_pushbutton = QPushButton('X')
                self.layout.addWidget(self.close_pushbutton)

                def close_pushbutton_clicked():
                    self.task_widget.hide()

                self.close_pushbutton.clicked.connect(close_pushbutton_clicked)

                # Geometry
                self.close_pushbutton.setFixedSize(int(self.height()*0.5),
                                                       int(self.height()*0.5))
                # Style
                self.close_pushbutton.setStyleSheet(
                    '''
                    QPushButton
                    {
                        border:2px solid #61677A;
                        border-radius:5px;
                    }   
                    QPushButton:clicked
                    {
                        background-color:#7AA874;
                    }
                    ''')



        self.toolbar_widget = Toolbar(parent=self)
        self.layout.addWidget(self.toolbar_widget)

