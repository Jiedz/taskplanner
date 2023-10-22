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
    )
from taskplanner.tasks import Task

class TaskWidget(QWidget):
    '''
    This class defines a task widget.
    '''
    def __init__(self,
                 task:Task,
                 main_color:str=None,
                 visible:bool=True):
        '''
        :param task: :py:class:'taskplanner.tasks.Task'
            The task associated to this widget
        :param main_color: str, optional
        :param visible: bool, optional
        '''
        raise NotImplementedError