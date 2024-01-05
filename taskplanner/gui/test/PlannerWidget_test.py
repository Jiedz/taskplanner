from taskplanner.planner import Planner
from taskplanner.gui.planner import PlannerWidget
from taskplanner.gui.styles import PlannerWidgetStyle

from PyQt5.QtWidgets import QApplication
import sys
# Make a task planner
planner = Planner()
# Build application2
app = QApplication(sys.argv)
# Task widget - standard view
try:
    planner_widget = PlannerWidget.from_file()
except:
    planner_widget = PlannerWidget(planner=Planner())
planner_widget.show()
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