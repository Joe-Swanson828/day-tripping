�G"""
ui/app.py — Main application window for Day Tripping.

Manages the customtkinter home screen, theme switching, and
transitions to/from the pywebview map view.

Architecture note: On macOS, pywebview's cocoa backend must run on the
main thread.  The main() loop alternates between CTk mainloop and
webview event loop so both always execute on thread-0.
"""

from __future__ import annotations

import logging
import os
import sys

import customtkinter as ctk
from PIL import Image, ImageTk

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config.settings import APP_SUPPORT_DIR, LOG_DIR
from config.themes import get_theme, Theme
from data.database import init_db, get_setting, set_setting
from ui.home_view import HomeView

# --- Logging setup ---
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Font path
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")
DISPLAY_FONT = "Boogaloo"
DISPLAY_FONT_PATH = "Boogaloo-Regular.ttf"
FALLBACK_FONT = "Righteous"
# For headers/titles: Boogaloo
# For body text: SF Pro Text / system


class DayTrippingApp(ctk.CTk):
    """Main application window — home screen with theme management."""

    def __init__(self) -> None:
        super().__init__()

        # Register as a foreground app so it appears in dock / Cmd+Tab
        self._register_as_foreground_app()

        # Initialize database
        init_db()

        # Track pending map requests (trip_id to open after mainloop exits)
        self._pending_map_trip: int | None = None

        # Load saved theme preference
        saved_theme = get_setting("theme", "psychedelic")
        self.current_theme_name = saved_theme
        self.theme = get_theme(saved_theme)

        # Load custom font
        self._load_display_font()

        # Set app icon (dock + window)
        self._set_app_icon()

        # Window setup
        self.title("Day Tripping")
        self.geometry("1200x800")
        self.minsize(1000, 650)

        # Apply theme appearance mode
        self._set_theme_mode()

        # Configure window background
        self.configure(fg_color=self.theme.bg_primary)

        # Build UI
        self._build_titlebar()
        self._build_content()

        # Bring window to foreground on macOS
        self.lift()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))
        self.focus_force()

    def _load_display_font(self) -> None:
        """Load the psychedelic display font if available."""
        # Load Boogaloo as primary, Righteous as fallback
        fonts_to_load = [
            ("Boogaloo-Regular.ttf", "Boogaloo"),
            ("Righteous-Regular.ttf", "Righteous"),
        ]
        
        for font_file, font_name in fonts_to_load:
            font_path = os.path.join(FONT_DIR, font_file)
            if os.path.exists(font_path):
                try:
                    if sys.platform == "darwin":
                        from CoreText import (
                            CTFontManagerRegisterFontsForURL,
                            kCTFontManagerScopeProcess,
                        )
                        from Foundation import NSURL

                        font_url = NSURL.fileURLWithPath_(font_path)
                        success, error = CTFontManagerRegisterFontsForURL(
                            font_url, kCTFontManagerScopeProcess, None
                        )
                        if success:
                            logger.info("Loaded display font: %s (%s)", font_name, font_path)
                        elif error:
                            logger.warning("Font registration error for %s: %s", font_name, error)
                except ImportError:
                    logger.info("PyObjC CoreText not available — using system fonts")
                except Exception as e:
                    logger.warning("Could not load custom font %s: %s", font_name, e)

    def _register_as_foreground_app(self) -> None:
        """Tell macOS this is a regular GUI app (shows in dock + Cmd+Tab)."""
        if sys.platform != "darwin":
            return
        try:
            from AppKit import NSApplication, NSApplicationActivationPolicyRegular
            NSApplication.sharedApplication().setActivationPolicy_(
                NSApplicationActivationPolicyRegular
            )
        except ImportError:
            pass
        except Exception as e:
            logger.warning("Could not set activation policy: %s", e)

    def _set_app_icon(self) -> None:
        """Set the app icon in the macOS dock and window title bar."""
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png"
        )
        if not os.path.exists(icon_path):
            return

        try:
            img = Image.open(icon_path)
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            self._icon_photo = ImageTk.PhotoImage(img)
            self.iconphoto(True, self._icon_photo)
        except Exception as e:
            logger.warning("Could not set window icon: %s", e)

        try:
            if sys.platform == "darwin":
                from AppKit import NSApplication, NSImage
                ns_image = NSImage.alloc().initWithContentsOfFile_(icon_path)
                if ns_image:
                    NSApplication.sharedApplication().setApplicationIconImage_(ns_image)
        except ImportError:
            pass
        except Exception as e:
            logger.warning("Could not set dock icon: %s", e)

    def _set_theme_mode(self) -> None:
        """Set the CTk appearance mode based on theme."""
        if self.current_theme_name == "light":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def _build_titlebar(self) -> None:
        """Build the top bar with app title and theme toggle."""
        bar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        bar.pack(fill="x", padx=24, pady=(16, 0))
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar,
            text="Day Tripping",
            font=(DISPLAY_FONT, 32, "bold"),
            text_color=self.theme.action_primary,
        ).pack(side="left")

        self.theme_var = ctk.StringVar(value=self.current_theme_name.capitalize())
        theme_switch = ctk.CTkSegmentedButton(
            bar,
            values=["Psychedelic", "Dark", "Light"],
            variable=self.theme_var,
            command=self._on_theme_change,
            font=("SF Pro Text", 12),
            selected_color=self.theme.ctk_selected,
            selected_hover_color=self.theme.ctk_selected_hover,
            unselected_color=self.theme.bg_secondary,
            unselected_hover_color=self.theme.bg_tertiary,
            width=220,
        )
        theme_switch.pack(side="right")

    def _build_content(self) -> None:
        """Build the main content area (home view)."""
        self.home_view = HomeView(self, self.theme, self._open_trip)
        self.home_view.pack(fill="both", expand=True, padx=24, pady=(12, 24))

    def _on_theme_change(self, new_theme: str) -> None:
        """Handle theme toggle."""
        theme_name = new_theme.lower()
        self.current_theme_name = theme_name
        self.theme = get_theme(theme_name)

        set_setting("theme", theme_name)
        self._set_theme_mode()
        self.configure(fg_color=self.theme.bg_primary)

        for widget in self.winfo_children():
            widget.destroy()
        self._build_titlebar()
        self._build_content()

    def _open_trip(self, trip_id: int) -> None:
        """Request opening a trip — exits CTk mainloop so main() can launch webview."""
        self._pending_map_trip = trip_id
        self.withdraw()
        self.quit()  # Exit mainloop; main() loop will handle the webview

    def show_and_refresh(self) -> None:
        """Re-show the home window and refresh trip data."""
        self.deiconify()
        self.lift()
        self.home_view.refresh()


def main() -> None:
    """Launch Day Tripping with CTk ↔ webview main-thread switching."""
    app = DayTrippingApp()

    while True:
        app.mainloop()

        trip_id = app._pending_map_trip
        if trip_id is None:
            # User closed the window normally — exit
            break

        # Reset pending state
        app._pending_map_trip = None

        # Open map view on the main thread (required by macOS cocoa)
        try:
            from ui.map_view import open_map_view
            open_map_view(trip_id, app.theme)
        except Exception as e:
            logger.error("Failed to open map view: %s", e)

        # Map view closed — re-show home
        app.show_and_refresh()

    app.destroy()


if __name__ == "__main__":
    main()
�G*cascade08"(06f4dc7650e0851582b69b2902ce5424d01b3a462-file:///Applications/Day%20Tripping/ui/app.py:#file:///Applications/Day%20Tripping