from PyQt6.QtCore import QTimer
from common.enums import StatusType
from common.styles import STATUSBAR_STYLES

class StatusBarController:
    """Controller for managing status bar messages and styles."""

    def __init__(self, status_bar):
        self.status_bar = status_bar

    
    def show_message(self, message: str, duration: int, status_type: StatusType)-> None:
        """Display a message on the status bar with appropriate styling.

        Args:
            message (str): The message to display.
            duration (int): Duration in milliseconds to display the message.
            status_type (StatusType): The type of status message (e.g., INFO, ERROR).
        """
        self.status_bar.setStyleSheet("")

        style = STATUSBAR_STYLES.get(status_type)
        if style:
            self.status_bar.setStyleSheet(style)

        self.status_bar.showMessage(message, duration)

        QTimer.singleShot(duration, lambda: self.status_bar.setStyleSheet("background-color: white;"))