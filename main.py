# IMPORT
from PySide2.QtWidgets import QApplication
from SimpleCurveEditor import *


# CORE
app = QApplication([])

widget = CurveEditor()
widget.show()

app.exec_()