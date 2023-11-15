from taskplanner.tasks import Task
from taskplanner.gui.tasks import TaskWidget, TaskWidgetSimple
from taskplanner.gui.stylesheets.tasks import TaskWidgetStyle

from PyQt5.QtWidgets import QApplication, QFontComboBox
import sys

task1 = Task(name='Task - Level 1')
task2 = Task(name='Task - Level 2')
task2b = Task(name='Task - Level 2 B')
task3 = Task(name='Task - Level 3')
task4 = Task(name='Task - Level 4')

task1.add_children_tasks(task2, task2b)
task2.add_children_tasks(task3)
task4.set_parent_task(task3)

task1._print()
# Build application
app = QApplication(sys.argv)
# Task widget - standard view
style = TaskWidgetStyle(color_palette='deep purple')
task_widget = TaskWidget(task=task1,
                         style=style)
task_widget.show()
task1.priority = 'high'
# Show Fonts
'''
font_combobox = QFontComboBox()
font_combobox.show()
'''
sys.exit(app.exec_())