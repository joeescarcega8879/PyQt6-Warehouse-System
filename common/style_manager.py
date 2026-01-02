
import logging
from pathlib import Path

class StyleManager:
    _global_styles: str = ""

    @staticmethod
    def load_global_styles() -> None:
        """Load global styles from the CSS file."""
        try:
            css_path = Path(__file__).resolve().parents[1] / "assets" / "styles.css"
        
            with css_path.open("r", encoding="utf-8") as f:
                StyleManager._global_styles = f.read()
        
        except Exception as e:
            logging.error(f"Failed to load global styles: {e}")
            StyleManager._global_styles = ""

    @staticmethod
    def apply_to_app(app) -> None:
        """Apply the global styles to the entire application."""
        if StyleManager._global_styles:
            app.setStyleSheet(StyleManager._global_styles)

    @staticmethod
    def apply_global_styles(widget) -> None:
        """Apply the global styles to a specific widget."""
        if StyleManager._global_styles:
            widget.setStyleSheet(StyleManager._global_styles)
