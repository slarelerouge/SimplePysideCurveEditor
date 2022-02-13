# IMPORT
from PySide2.QtWidgets import QApplication
from SmallCurveEditor import *


# CORE
app = QApplication([])

widget = CurveEditor()
widget.show()

app.exec_()