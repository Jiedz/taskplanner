from taskplanner.planner import Planner
from taskplanner.gui.planner import PlannerWidget, PlannerWidgetStyle
from taskplanner.gui.utilities import select_file
from PyQt5.QtWidgets import QApplication
import sys
from sys import exit

application = QApplication(sys.argv)

widget = PlannerWidget(planner=Planner.from_file(select_file(title='Select a .txt File Containing the Task Planner')))

widget.show()

exit(application.exec_())
