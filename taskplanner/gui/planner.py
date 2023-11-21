"""
This module defines a planner widget and related widgets.
"""
from PyQt5.QtWidgets import \
    (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QComboBox,
    QScrollArea,
    QCalendarWidget,
    QColorDialog
    )

from taskplanner.planner import Planner
from taskplanner.gui.styles import TaskWidgetStyle, ICON_SIZES
