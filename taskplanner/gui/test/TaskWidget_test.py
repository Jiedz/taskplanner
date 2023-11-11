from taskplanner.tasks import Task
from taskplanner.gui.tasks import TaskWidget, TaskWidgetSimple

from PyQt5.QtWidgets import QApplication, QFontComboBox
import sys

task4 = Task(name='Task - Level 4')
task3 = Task(name='Task - Level 3')
task4.set_parent_task(task3)
# Set some ancestors
task2 = Task(name='Task - Level 2')
task2b = Task(name='Task - Level 2 B')
task3.set_parent_task(task2)
task1 = Task(name='Task - Level 1')
task2.set_parent_task(task1)
task2b.set_parent_task(task1)
task1._print()
# Build application
app = QApplication(sys.argv)
# Task widget - standard view
task_widget = TaskWidget(task=task1)
task_widget.show()
task1.priority = 'high'
# Show Fonts
'''
font_combobox = QFontComboBox()
font_combobox.show()
'''
sys.exit(app.exec_())