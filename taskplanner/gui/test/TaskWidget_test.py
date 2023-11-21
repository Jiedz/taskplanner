from taskplanner.tasks import Task
from taskplanner.planner import Planner
from taskplanner.gui.tasks import TaskWidget
from taskplanner.gui.styles import TaskWidgetStyle

from PyQt5.QtWidgets import QApplication
import sys

task1 = Task(name='Task - Level 1')
task2 = Task(name='Task - Level 2')
task1b = Task(name='Task - Level 1 B')
task3 = Task(name='Task - Level 3')
task4 = Task(name='Task - Level 4')

task1.add_children_tasks(task2)
task2.add_children_tasks(task3)
task4.set_parent_task(task3)

# Make a task planner
planner = Planner()
print(planner.categories)
planner.add_tasks(task1, task1b)
print(planner.categories)

for task in planner.tasks:
    task._print()

# Build application
app = QApplication(sys.argv)
# Task widget - standard view
style = TaskWidgetStyle(color_palette='dark material')
task_widget = TaskWidget(task=task1,
                         style=style,
                         planner=planner)
task_widget.show()
task1.priority = 'high'
# Show Fonts
'''
font_combobox = QFontComboBox()
font_combobox.show()
'''
'''
color_dialog = QColorDialog()
color_dialog.show()
'''

sys.exit(app.exec_())