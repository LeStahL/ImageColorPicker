import sys
from PyQt6.QtWidgets import QApplication

# Note (@LeStahL): error NEEDS a present QApplication instance.
application: QApplication = QApplication(sys.argv)
