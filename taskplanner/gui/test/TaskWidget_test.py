from taskplanner.tasks import Task
from taskplanner.gui.tasks import TaskWidget

from PyQt5.QtWidgets import QApplication, QFontComboBox
import sys

task = Task()
# Set some ancestors
parent_task = Task(name='Parent ')
task.set_parent_task(parent_task)
grandparent_task = Task(name='Granparent')
parent_task.set_parent_task(grandparent_task)
# Build application
app = QApplication(sys.argv)
task_widget = TaskWidget(task=task)
task_widget.show()
# Show Fonts
'''
font_combobox = QFontComboBox()
font_combobox.show()
'''
app.exec_()