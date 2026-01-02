import os
import sys
from tkinter.ttk import Style
from PyQt6 import uic
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QApplication, QComboBox, QMdiSubWindow

# from  material_view import MaterialView
from common.style_manager import StyleManager

class MainView(QMainWindow):

    # Signals
    form_material_signal = pyqtSignal()
    form_user_signal = pyqtSignal()

    def __init__(self):
        super(MainView, self).__init__()

          # Initialize components
        self.initializeComponents()

        # Load global styles
        StyleManager.apply_global_styles(self)

    def initializeComponents(self) -> None:
        
        # Load UI Path
        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "main_view.ui")
        # Load UI
        uic.loadUi(ui_path, self)

        self.btn_materials.clicked.connect(self.form_material_signal.emit)

        self.btn_users.clicked.connect(self.form_user_signal.emit)

        self.show()

    
    def open_child_form(self, objectInstance, mdiSubWindow) -> None:
        """"
        Opens a child form inside the MDI container.
        Closes any previously opened child forms.
        
        :param objectInstance: The instance of the child form to be opened.
        :param mdiSubWindow: The QMdiSubWindow that will contain the child form.

        """
        self.mdi_container.closeAllSubWindows()

        StyleManager.apply_global_styles(objectInstance)

        mdiSubWindow.setWidget(objectInstance)
        mdiSubWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        mdiSubWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.mdi_container.addSubWindow(mdiSubWindow)
        mdiSubWindow.showMaximized()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    instance = MainView()

    app.exec()
