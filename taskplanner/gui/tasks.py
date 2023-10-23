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

class TaskWidget(QScrollArea):
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
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setFixedWidth(500)
        self.setFixedHeight(500)
        # Toolbar
        self.make_toolbar()
        # Style
        import sys
        current_path = "/".join(sys.modules[self.__class__.__module__].__file__.split('/')[:-1])
        file = open(os.path.join(current_path, 'stylesheets/TaskWidget.css'))
        self.setStyleSheet(file.read())
        file.close()
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
                self.make_completed_pushbutton()
                self.make_close_pushbutton()

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

            def make_close_pushbutton(self):
                # Pushbutton to close the task view
                self.close_pushbutton = QPushButton()
                self.layout.addWidget(self.close_pushbutton)

                def close_pushbutton_clicked():
                    self.task_widget.hide()

                self.close_pushbutton.clicked.connect(close_pushbutton_clicked)

        self.toolbar_widget = Toolbar(parent=self)
        self.layout.addWidget(self.toolbar_widget)

