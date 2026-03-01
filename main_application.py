import sys
from PyQt6.QtWidgets import QApplication, QMdiSubWindow

from database.connection import connect_db
from views.login_view import LoginView
from views.main_view import MainView
from views.user_view import UserView
from views.material_view import MaterialView
from views.line_view import LineView
from views.change_password_view import ChangePasswordView
from views.receipt_view import ReceiptView
from views.supplier_view import SupplierView
from views.generic_view import GenericView

from common.style_manager import StyleManager
from common.status_bar_controller import StatusBarController

from presenters.login_presenter import LoginPresenter
from presenters.main_presenter import MainPresenter
from presenters.material_presenter import MaterialPresenter
from presenters.user_presenter import UserPresenter
from presenters.change_password_presenter import ChangePasswordPresenter
from presenters.production_line_presenter import LinePresenter
from presenters.supplier_receipt_presenter import SupplierReceiptPresenter
from presenters.supplier_presenter import SupplierPresenter
from presenters.generic_presenter import GenericPresenter

class MainApplication:

    """Main application controller handling view navigation and interactions."""

    def __init__(self):
        self._init_login()

    def _init_login(self):
        self.login_view = LoginView()
        self.login_presenter = LoginPresenter(self.login_view, on_login_success=self._initialize_main_view)
        self.login_view.show()

    def _initialize_main_view(self, user) -> None:
        self.current_user = user

        self.main_view = MainView()
        self.status_bar_controller = StatusBarController(self.main_view.statusBar())
        self.main_presenter = MainPresenter(self.main_view, main_app=self, current_user=self.current_user)

        self.main_view.showMaximized()
        self.login_view.close()

    def open_receipt_form(self) -> None:
        self.receipt_view = ReceiptView()
        self.receipt_presenter = SupplierReceiptPresenter(self.receipt_view, main_app=self ,current_user=self.current_user, status_handler=self.status_bar_controller.show_message)

        sub_window = QMdiSubWindow()
        self.main_view.open_child_form(self.receipt_view, sub_window)

    def open_material_form(self) -> None:
        self.material_view = MaterialView()
        self.material_presenter = MaterialPresenter(self.material_view, current_user=self.current_user, status_handler=self.status_bar_controller.show_message)

        sub_window = QMdiSubWindow()
        self.main_view.open_child_form(self.material_view, sub_window)

    def open_user_form(self) -> None:
        self.user_view = UserView()
        self.user_presenter = UserPresenter(self.user_view, main_app=self,  current_user=self.current_user, status_handler=self.status_bar_controller.show_message)

        sub_window = QMdiSubWindow()
        self.main_view.open_child_form(self.user_view, sub_window)

    def open_change_password_form(self, user_id: int) -> None:
        change_password_view = ChangePasswordView()
        self.change_password_presenter = ChangePasswordPresenter(
            view=change_password_view,
            user_id=user_id,
            current_user=self.current_user,
            status_handler=self.status_bar_controller.show_message
        )

        change_password_view.exec()

    def open_generic_form(self, on_material_selected = None) -> None:
        self.generic_view = GenericView()
        
        self.generic_presenter = GenericPresenter(
            view=self.generic_view, 
            status_handler=self.status_bar_controller.show_message
        )

        if on_material_selected:
            self.generic_view.material_selected.connect(on_material_selected)

        self.generic_view.exec()

    def open_line_form(self) -> None:
        self.line_view = LineView()
 
        self.line_presenter = LinePresenter(self.line_view, current_user=self.current_user, status_handler=self.status_bar_controller.show_message)

        sub_window = QMdiSubWindow()
        self.main_view.open_child_form(self.line_view, sub_window)
        
    def open_supplier_form(self) -> None:
        self.supplier_view = SupplierView()
 
        self.supplier_presenter = SupplierPresenter(self.supplier_view, main_app=self, current_user=self.current_user, status_handler=self.status_bar_controller.show_message)

        sub_window = QMdiSubWindow()
        self.main_view.open_child_form(self.supplier_view, sub_window)


def main():
    app = QApplication(sys.argv)

    StyleManager.load_global_styles()
    StyleManager.apply_to_app(app)
    
    if not connect_db():
        sys.exit(1)
    
    controller = MainApplication()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()