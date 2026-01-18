"""
Settings dialog for WeatherClock Pi.

Allows users to configure time zones for the 3 clocks.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Callable, Optional, Tuple, List

from utils.config import (
    ThemeColors, 
    TimezoneConfig, 
    COMMON_TIMEZONES,
    AppConfig,
    save_config
)


logger = logging.getLogger(__name__)


class SettingsDialog(tk.Toplevel):
    """
    Modal dialog for configuring timezone settings.
    """
    
    def __init__(self, parent, colors: ThemeColors, config: AppConfig,
                 on_save: Optional[Callable[[AppConfig], None]] = None,
                 **kwargs):
        super().__init__(parent, **kwargs)
        
        self.colors = colors
        self.config = config
        self.on_save = on_save
        
        # Window settings
        self.title("Settings")
        self.configure(bg=colors.background)
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.geometry("500x450")
        self.update_idletasks()
        
        # Get parent geometry
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_w - 500) // 2
        y = parent_y + (parent_h - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        # Build UI
        self._create_widgets()
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind('<Escape>', lambda e: self._on_close())
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Title
        title_label = tk.Label(
            self,
            text="⚙️ Settings",
            bg=self.colors.background,
            fg=self.colors.primary_text,
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            self,
            text="Configure time zones for each clock",
            bg=self.colors.background,
            fg=self.colors.secondary_text,
            font=("Helvetica", 12)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Timezone selectors container
        selectors_frame = tk.Frame(self, bg=self.colors.background)
        selectors_frame.pack(fill=tk.X, padx=30)
        
        # Main clock selector
        self.main_var = tk.StringVar(value=self.config.main_timezone.timezone)
        self._create_timezone_selector(
            selectors_frame,
            "Main Clock (Large)",
            self.main_var,
            self.config.main_timezone
        )
        
        # Secondary clock 1 selector
        self.sec1_var = tk.StringVar(value=self.config.secondary_timezone_1.timezone)
        self._create_timezone_selector(
            selectors_frame,
            "Secondary Clock 1",
            self.sec1_var,
            self.config.secondary_timezone_1
        )
        
        # Secondary clock 2 selector
        self.sec2_var = tk.StringVar(value=self.config.secondary_timezone_2.timezone)
        self._create_timezone_selector(
            selectors_frame,
            "Secondary Clock 2",
            self.sec2_var,
            self.config.secondary_timezone_2
        )
        
        # Buttons
        button_frame = tk.Frame(self, bg=self.colors.background)
        button_frame.pack(pady=30)
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_close,
            bg=self.colors.card_background,
            fg=self.colors.primary_text,
            font=("Helvetica", 12),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self._on_save,
            bg=self.colors.accent,
            fg="#000000",
            font=("Helvetica", 12, "bold"),
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=10)
    
    def _create_timezone_selector(self, parent, label: str, 
                                   var: tk.StringVar,
                                   current_config: TimezoneConfig):
        """Create a timezone selector row."""
        frame = tk.Frame(parent, bg=self.colors.background)
        frame.pack(fill=tk.X, pady=10)
        
        # Label
        label_widget = tk.Label(
            frame,
            text=label,
            bg=self.colors.background,
            fg=self.colors.primary_text,
            font=("Helvetica", 14)
        )
        label_widget.pack(anchor="w")
        
        # Dropdown
        values = [f"{tz[1]} ({tz[0]})" for tz in COMMON_TIMEZONES]
        
        # Style the combobox
        style = ttk.Style()
        style.configure(
            "Custom.TCombobox",
            fieldbackground=self.colors.card_background,
            background=self.colors.card_background,
        )
        
        combo = ttk.Combobox(
            frame,
            textvariable=var,
            values=values,
            state="readonly",
            font=("Helvetica", 12),
            width=40
        )
        combo.pack(fill=tk.X, pady=(5, 0))
        
        # Set current value
        current_tz = current_config.timezone
        for i, tz in enumerate(COMMON_TIMEZONES):
            if tz[0] == current_tz:
                combo.current(i)
                break
    
    def _get_timezone_from_display(self, display: str) -> Tuple[str, str, str]:
        """Extract timezone, label, and country from display string."""
        # Format: "Label (timezone)"
        for tz_id, tz_label in COMMON_TIMEZONES:
            display_str = f"{tz_label} ({tz_id})"
            if display == display_str:
                # Split label into city and country
                if ", " in tz_label:
                    parts = tz_label.split(", ")
                    return tz_id, parts[0], parts[1]
                return tz_id, tz_label, ""
        
        # Fallback
        return "America/New_York", "New York", "USA"
    
    def _on_save(self):
        """Handle save button click."""
        # Get selected values
        main_tz, main_label, main_country = self._get_timezone_from_display(self.main_var.get())
        sec1_tz, sec1_label, sec1_country = self._get_timezone_from_display(self.sec1_var.get())
        sec2_tz, sec2_label, sec2_country = self._get_timezone_from_display(self.sec2_var.get())
        
        # Update config
        self.config.main_timezone = TimezoneConfig(main_tz, main_label, main_country)
        self.config.secondary_timezone_1 = TimezoneConfig(sec1_tz, sec1_label, sec1_country)
        self.config.secondary_timezone_2 = TimezoneConfig(sec2_tz, sec2_label, sec2_country)
        
        # Save to file
        save_config(self.config)
        
        logger.info(f"Settings saved: {main_tz}, {sec1_tz}, {sec2_tz}")
        
        # Callback
        if self.on_save:
            self.on_save(self.config)
        
        self._on_close()
    
    def _on_close(self):
        """Handle dialog close."""
        self.grab_release()
        self.destroy()
