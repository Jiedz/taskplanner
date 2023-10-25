from taskplanner.tasks import Task
from taskplanner.gui.tasks import TaskWidget

from PyQt5.QtWidgets import QApplication, QFontComboBox
import sys

task = Task()
app = QApplication(sys.argv)
task_widget = TaskWidget(task=task)
task_widget.show()
# Show Fonts
'''
font_combobox = QFontComboBox()
font_combobox.show()
'''
app.exec_()