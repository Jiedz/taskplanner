from taskplanner.tasks import Task
from taskplanner.gui.tasks import TaskWidget

from PyQt5.QtWidgets import QApplication
import sys

task = Task()
app = QApplication(sys.argv)
task_widget = TaskWidget(task=task)
task_widget.show()
app.exec_()