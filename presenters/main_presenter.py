
class MainPresenter:
    def __init__(self, view, navigation, current_user):
        self.view = view
        self.navigation = navigation
        self.current_user = current_user
        self._connect_signals()

    def _connect_signals(self):
        self.view.form_material_signal.connect(self.navigation.open_material_form)
        self.view.form_user_signal.connect(self.navigation.open_user_form)