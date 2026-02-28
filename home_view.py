’H"""
ui/home_view.py ‚Äî "My Planned Trips" home screen.

Displays a grid of trip cards with create, rename, duplicate, and delete
functionality. Each card shows trip name, start‚Üíend, date, and a colored
accent bar. Clicking a card opens the trip in the map view.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable

import customtkinter as ctk

from config.themes import Theme
from core.trip_manager import (
    create_trip,
    delete_trip,
    duplicate_trip,
    get_all_trips,
    rename_trip,
)

logger = logging.getLogger(__name__)

DISPLAY_FONT = "Boogaloo"


class HomeView(ctk.CTkFrame):
    """Home screen showing all saved trips with management controls."""

    def __init__(
        self,
        parent: ctk.CTk,
        theme: Theme,
        on_open_trip: Callable[[int], None],
    ) -> None:
        super().__init__(parent, fg_color="transparent")
        self.theme = theme
        self.on_open_trip = on_open_trip
        self._build()

    def _build(self) -> None:
        """Build the home screen layout."""
        # Header row with subtitle and new trip button
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(8, 16))
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Your Adventures",
            font=("SF Pro Display", 18),
            text_color=self.theme.text_secondary,
        ).pack(side="left")

        new_btn = ctk.CTkButton(
            header,
            text="Ôºã New Adventure",
            font=(DISPLAY_FONT, 18),
            fg_color=self.theme.interactive,
            hover_color=self.theme.interactive_hover,
            text_color=self.theme.text_on_accent if self.theme.name == "light" else "#ffffff",
            corner_radius=25,  # More organic/rounded
            height=44,
            width=200,
            command=self._create_new_trip,
        )
        new_btn.pack(side="right")

        # Scrollable trip grid
        self.grid_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=self.theme.bg_tertiary,
            scrollbar_button_hover_color=self.theme.interactive,
        )
        self.grid_frame.pack(fill="both", expand=True)

        # Configure grid columns
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)
        self.grid_frame.columnconfigure(2, weight=1)

        self._populate_trips()

    def _populate_trips(self) -> None:
        """Load and display all trips as cards."""
        # Clear existing cards
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        trips = get_all_trips()

        if not trips:
            self._show_empty_state()
            return

        for idx, trip in enumerate(trips):
            row = idx // 3
            col = idx % 3
            card = self._create_trip_card(trip)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _show_empty_state(self) -> None:
        """Show a message when no trips exist."""
        empty_frame = ctk.CTkFrame(
            self.grid_frame,
            fg_color=self.theme.bg_secondary,
            corner_radius=30,  # Wavy/Organic feel
        )
        empty_frame.grid(row=0, column=0, columnspan=3, padx=20, pady=60, sticky="nsew")

        ctk.CTkLabel(
            empty_frame,
            text="No trips yet",
            font=(DISPLAY_FONT, 24),
            text_color=self.theme.text_primary,
        ).pack(pady=(40, 8))

        ctk.CTkLabel(
            empty_frame,
            text="Click \"Ôºã New Adventure\" to plan your first road trip!",
            font=("SF Pro Text", 14),
            text_color=self.theme.text_secondary,
        ).pack(pady=(0, 40))

    def _create_trip_card(self, trip: dict) -> ctk.CTkFrame:
        """Create a single trip card widget."""
        card = ctk.CTkFrame(
            self.grid_frame,
            fg_color=self.theme.bg_secondary,
            corner_radius=24,  # More organic
            border_width=1,
            border_color=self.theme.border,
            cursor="hand2",
        )

        # Accent bar at top
        accent = ctk.CTkFrame(
            card,
            fg_color=self.theme.action_primary,
            height=4,
            corner_radius=2,
        )
        accent.pack(fill="x", padx=12, pady=(12, 0))

        # Trip name
        ctk.CTkLabel(
            card,
            text=trip["name"],
            font=(DISPLAY_FONT, 18),
            text_color=self.theme.text_primary,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

        # Route summary
        start = trip.get("start_location") or "Not set"
        end = trip.get("end_location") or "Not set"
        route_text = f"{start}  ‚Üí  {end}" if start != "Not set" or end != "Not set" else "Tap to start planning"

        ctk.CTkLabel(
            card,
            text=route_text,
            font=("SF Pro Text", 12),
            text_color=self.theme.text_secondary,
            anchor="w",
            wraplength=250,
        ).pack(fill="x", padx=16, pady=(0, 4))

        # Date
        created = trip.get("created_at", "")
        if created:
            try:
                dt = datetime.fromisoformat(created)
                date_str = dt.strftime("%b %d, %Y")
            except ValueError:
                date_str = created
        else:
            date_str = ""

        ctk.CTkLabel(
            card,
            text=date_str,
            font=("SF Pro Text", 11),
            text_color=self.theme.text_tertiary,
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 8))

        # Action buttons row
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        trip_id = trip["id"]

        ctk.CTkButton(
            btn_frame,
            text="Open",
            font=("SF Pro Text", 11),
            fg_color=self.theme.interactive,
            hover_color=self.theme.interactive_hover,
            corner_radius=8,
            height=28,
            width=60,
            command=lambda tid=trip_id: self.on_open_trip(tid),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_frame,
            text="Rename",
            font=("SF Pro Text", 11),
            fg_color=self.theme.bg_tertiary,
            hover_color=self.theme.border,
            text_color=self.theme.text_secondary,
            corner_radius=8,
            height=28,
            width=60,
            command=lambda tid=trip_id: self._rename_trip(tid),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_frame,
            text="Duplicate",
            font=("SF Pro Text", 11),
            fg_color=self.theme.bg_tertiary,
            hover_color=self.theme.border,
            text_color=self.theme.text_secondary,
            corner_radius=8,
            height=28,
            width=68,
            command=lambda tid=trip_id: self._duplicate_trip(tid),
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            btn_frame,
            text="Delete",
            font=("SF Pro Text", 11),
            fg_color=self.theme.warning,
            hover_color=self.theme.warning_hover,
            corner_radius=8,
            height=28,
            width=56,
            command=lambda tid=trip_id: self._delete_trip(tid),
        ).pack(side="right")

        # Click card to open trip
        card.bind("<Button-1>", lambda e, tid=trip_id: self.on_open_trip(tid))

        return card

    def _create_new_trip(self) -> None:
        """Show dialog to create a new trip."""
        dialog = ctk.CTkInputDialog(
            text="Name your adventure:",
            title="New Trip",
        )
        name = dialog.get_input()
        if name and name.strip():
            trip_id = create_trip(name.strip())
            logger.info("Created trip: %s (id=%d)", name.strip(), trip_id)
            self.refresh()

    def _rename_trip(self, trip_id: int) -> None:
        """Show dialog to rename a trip."""
        dialog = ctk.CTkInputDialog(
            text="New name:",
            title="Rename Trip",
        )
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            rename_trip(trip_id, new_name.strip())
            self.refresh()

    def _duplicate_trip(self, trip_id: int) -> None:
        """Duplicate a trip."""
        new_id = duplicate_trip(trip_id)
        if new_id:
            logger.info("Duplicated trip %d ‚Üí %d", trip_id, new_id)
            self.refresh()

    def _delete_trip(self, trip_id: int) -> None:
        """Show confirmation dialog then delete a trip."""
        confirm = ctk.CTkInputDialog(
            text='Type "delete" to confirm:',
            title="Delete Trip",
        )
        result = confirm.get_input()
        if result and result.strip().lower() == "delete":
            delete_trip(trip_id)
            logger.info("Deleted trip %d", trip_id)
            self.refresh()

    def refresh(self) -> None:
        """Refresh the trip list."""
        self._populate_trips()
⁄ *cascade08⁄€*cascade08€ª *cascade08ªº*cascade08ºΩ *cascade08Ω’*cascade08’Í *cascade08ÍÎ*cascade08Îˇ *cascade08ˇÅ*cascade08ÅÅ *cascade08ÅÉ*cascade08ÉÑ *cascade08Ñô*cascade08ô§  *cascade08§ • *cascade08• ¶  *cascade08¶ ∂ *cascade08∂ ’H *cascade08"(06f4dc7650e0851582b69b2902ce5424d01b3a4623file:///Applications/Day%20Tripping/ui/home_view.py:#file:///Applications/Day%20Tripping