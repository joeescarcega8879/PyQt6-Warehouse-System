import sys
from pathlib import Path
from PyQt6 import uic
from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QMdiSubWindow

from src.common.style_manager import StyleManager

# Base directory for assets — resolves correctly on any OS
_ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"


def _icon(filename: str) -> QIcon:
    """Return a QIcon from the icons directory. Safe on any OS."""
    return QIcon(str(_ICONS_DIR / filename))


# Panel widths for expanded / collapsed states
_PANEL_EXPANDED  = 240
_PANEL_COLLAPSED = 74


class MainView(QMainWindow):

    # Signals
    form_material_signal = pyqtSignal()
    form_line_signal     = pyqtSignal()
    form_user_signal     = pyqtSignal()
    form_receipt_signal  = pyqtSignal()
    form_supplier_signal = pyqtSignal()
    form_request_signal  = pyqtSignal()
    form_settings_signal = pyqtSignal()

    def __init__(self):
        super(MainView, self).__init__()
        self.initializeComponents()
        StyleManager.apply_global_styles(self)

    def initializeComponents(self) -> None:

        ui_path = Path(__file__).resolve().parent / "ui" / "main_view.ui"
        uic.loadUi(str(ui_path), self)

        # Icons
        self.btn_materials.setIcon(_icon("IMG-Materials.png"))
        self.btn_lines.setIcon(_icon("IMG-ProductionLines.png"))
        self.btn_users.setIcon(_icon("IMG-AddUser.png"))
        self.btn_suppliers.setIcon(_icon("IMG-Proveedor.png"))
        self.btn_requests.setIcon(_icon("IMG-Requests.png"))
        self.btn_receipts.setIcon(_icon("IMG-Receipts.png"))
        self.btn_settings.setIcon(_icon("IMG-Settings.png"))

        # Navigation signals
        self.btn_materials.clicked.connect(self.form_material_signal.emit)
        self.btn_users.clicked.connect(self.form_user_signal.emit)
        self.btn_lines.clicked.connect(self.form_line_signal.emit)
        self.btn_receipts.clicked.connect(self.form_receipt_signal.emit)
        self.btn_suppliers.clicked.connect(self.form_supplier_signal.emit)
        self.btn_requests.clicked.connect(self.form_request_signal.emit)
        self.btn_settings.clicked.connect(self.form_settings_signal.emit)
        self.btn_toggle.clicked.connect(self.toggle_dashboard)

        self.show()

    def open_child_form(self, objectInstance, mdiSubWindow) -> None:
        """
        Opens a child form inside the MDI container.
        Closes any previously opened child forms.
        """
        self.mdi_container.closeAllSubWindows()

        StyleManager.apply_global_styles(objectInstance)

        mdiSubWindow.setWidget(objectInstance)
        mdiSubWindow.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        mdiSubWindow.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        self.mdi_container.addSubWindow(mdiSubWindow)
        mdiSubWindow.showMaximized()

    # ── Category labels ───────────────────────────────────────
    _CATEGORY_LABELS = ["lbl_cat_produccion", "lbl_cat_almacen", "lbl_cat_administracion"]

    # ── Button label map: name → expanded text ────────────────
    _BUTTON_LABELS = {
        "btn_requests":  "Requests",
        "btn_lines":     "Production Lines",
        "btn_materials": "Materials",
        "btn_receipts":  "Receipts",
        "btn_suppliers": "Suppliers",
        "btn_users":     "Users",
        "btn_settings":  "Settings",
    }

    def toggle_dashboard(self) -> None:
        collapsing = self.panel_dashboard.width() == _PANEL_EXPANDED

        if collapsing:
            self.panel_dashboard.setFixedWidth(_PANEL_COLLAPSED)
            self.btn_toggle.setText(">>")
            for name in self._BUTTON_LABELS:
                getattr(self, name).setText("")
            for label_name in self._CATEGORY_LABELS:
                getattr(self, label_name).setVisible(False)
        else:
            self.panel_dashboard.setFixedWidth(_PANEL_EXPANDED)
            self.btn_toggle.setText("<< Collapse")
            for name, text in self._BUTTON_LABELS.items():
                getattr(self, name).setText(text)
            for label_name in self._CATEGORY_LABELS:
                getattr(self, label_name).setVisible(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    instance = MainView()
    app.exec()
