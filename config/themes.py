¬("""
config/themes.py â€” Color theme definitions for Day Tripping.

Three themes: Psychedelic (default), Dark, and Light.
Each theme provides colors for both customtkinter (home screen)
and CSS (webview map view).

Usage:
    from config.themes import get_theme, THEMES
    theme = get_theme("psychedelic")
    bg_color = theme["bg_primary"]
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    """Complete color theme for Day Tripping."""

    name: str

    # Backgrounds
    bg_primary: str        # Main background
    bg_secondary: str      # Card/panel background
    bg_tertiary: str       # Elevated surface

    # Accent colors (semantic)
    action_primary: str    # Routes, navigation, primary buttons (orange/gold)
    action_hover: str      # Primary hover state
    interactive: str       # Buttons, selections, toggles (purple)
    interactive_hover: str
    discovery: str         # Suggestions, new content (teal)
    discovery_hover: str
    warning: str           # Warnings, deletions (coral pink)
    warning_hover: str
    accent: str            # Warm gold accent
    accent_hover: str

    # Text
    text_primary: str      # Main text
    text_secondary: str    # Muted / secondary text
    text_tertiary: str     # Hints, placeholders
    text_on_accent: str    # Text on accent-colored buttons

    # Borders and dividers
    border: str
    divider: str

    # Map-specific
    route_start_color: str   # Route gradient start
    route_end_color: str     # Route gradient end
    route_alt_color: str     # Alternative routes (muted)
    marker_color: str        # Stop markers
    discover_marker: str     # Discovery suggestion markers

    # CTk-specific (customtkinter widget overrides)
    ctk_fg: str              # Frame foreground
    ctk_button: str          # Button color
    ctk_button_hover: str
    ctk_entry_bg: str        # Input field background
    ctk_selected: str        # Selected tab/segment
    ctk_selected_hover: str


# --- Theme Definitions ---

PSYCHEDELIC = Theme(
    name="psychedelic",
    bg_primary="#080010",      # Abyssal Purple (Void)
    bg_secondary="#140524",    # Deep Space
    bg_tertiary="#22093B",     # Bruise Purple
    action_primary="#FF2A00",  # Blood Red (Sun)
    action_hover="#EAEF00",    # Acid Yellow
    interactive="#FF8100",     # Peyote Orange
    interactive_hover="#FF2A00",
    discovery="#EAEF00",       # Acid Yellow
    discovery_hover="#FF8100",
    warning="#FFD500",
    warning_hover="#FF003C",
    accent="#EAEF00",          # Acid Yellow
    accent_hover="#FF8100",
    text_primary="#F1EADD",    # Bleached Bone
    text_secondary="#A88E96",  # Mauve
    text_tertiary="#5E4057",   # Muted
    text_on_accent="#080010",  # Void text on bright buttons
    border="#FF2A00",          # Blood Red Borders
    divider="#22093B",
    route_start_color="#EAEF00", 
    route_end_color="#FF2A00",   
    route_alt_color="#5E4057",
    marker_color="#FF2A00",
    discover_marker="#EAEF00",
    ctk_fg="#140524",
    ctk_button="#FF2A00",
    ctk_button_hover="#EAEF00",
    ctk_entry_bg="#22093B",
    ctk_selected="#FF8100",
    ctk_selected_hover="#FF2A00",
)

DARK = Theme(
    name="dark",
    bg_primary="#1a1a2e",
    bg_secondary="#16213e",
    bg_tertiary="#1f2b47",
    action_primary="#e85d2c",
    action_hover="#f07040",
    interactive="#7c3aed",
    interactive_hover="#6d28d9",
    discovery="#0d9488",
    discovery_hover="#0f766e",
    warning="#ec4899",
    warning_hover="#db2777",
    accent="#d4940a",
    accent_hover="#b8820a",
    text_primary="#e2e8f0",
    text_secondary="#94a3b8",
    text_tertiary="#64748b",
    text_on_accent="#1a1a2e",
    border="#334155",
    divider="#1e293b",
    route_start_color="#e85d2c",
    route_end_color="#7c3aed",
    route_alt_color="#334155",
    marker_color="#e85d2c",
    discover_marker="#0d9488",
    ctk_fg="#16213e",
    ctk_button="#7c3aed",
    ctk_button_hover="#6d28d9",
    ctk_entry_bg="#1f2b47",
    ctk_selected="#7c3aed",
    ctk_selected_hover="#6d28d9",
)

LIGHT = Theme(
    name="light",
    bg_primary="#faf5ef",
    bg_secondary="#f5f0e8",
    bg_tertiary="#ede6db",
    action_primary="#d4521e",
    action_hover="#b8441a",
    interactive="#6d28d9",
    interactive_hover="#5b21b6",
    discovery="#0f766e",
    discovery_hover="#115e59",
    warning="#db2777",
    warning_hover="#be185d",
    accent="#b8820a",
    accent_hover="#a16e08",
    text_primary="#1e293b",
    text_secondary="#475569",
    text_tertiary="#94a3b8",
    text_on_accent="#faf5ef",
    border="#d1c7b7",
    divider="#e2dbd0",
    route_start_color="#d4521e",
    route_end_color="#6d28d9",
    route_alt_color="#d1c7b7",
    marker_color="#d4521e",
    discover_marker="#0f766e",
    ctk_fg="#f5f0e8",
    ctk_button="#6d28d9",
    ctk_button_hover="#5b21b6",
    ctk_entry_bg="#ede6db",
    ctk_selected="#6d28d9",
    ctk_selected_hover="#5b21b6",
)

THEMES: dict[str, Theme] = {
    "psychedelic": PSYCHEDELIC,
    "dark": DARK,
    "light": LIGHT,
}


def get_theme(name: str) -> Theme:
    """Return a Theme by name. Defaults to psychedelic if name is invalid."""
    return THEMES.get(name.lower(), PSYCHEDELIC)
¬(*cascade08"(06f4dc7650e0851582b69b2902ce5424d01b3a4624file:///Applications/Day%20Tripping/config/themes.py:#file:///Applications/Day%20Tripping