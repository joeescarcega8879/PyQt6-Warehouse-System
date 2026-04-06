
class MainPresenter:
    def __init__(self, view, main_app, current_user):
        self.view = view
        self.main_app = main_app
        self.current_user = current_user
        self._connect_signals()

    def _connect_signals(self):
        self.view.form_material_signal.connect(self.main_app.open_material_form)
        self.view.form_user_signal.connect(self.main_app.open_user_form)
        self.view.form_line_signal.connect(self.main_app.open_line_form)
        self.view.form_receipt_signal.connect(self.main_app.open_receipt_form)
        self.view.form_supplier_signal.connect(self.main_app.open_supplier_form)
        self.view.form_request_signal.connect(self.main_app.open_request_form)