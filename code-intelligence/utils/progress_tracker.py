"""
Progress Tracker with GUI
Shows real-time progress of ontology generation in a popup window.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Callable
from datetime import datetime


class ProgressTracker:
    """
    Progress tracking with GUI window.

    Shows:
    - Current step and progress
    - Files processed
    - Estimated time remaining
    - Detailed status messages
    """

    def __init__(self, title="Ontology Generation Progress", total_steps=7):
        """
        Initialize progress tracker.

        Args:
            title: Window title
            total_steps: Total number of major steps
        """
        self.title = title
        self.total_steps = total_steps
        self.current_step = 0
        self.current_file = ""
        self.files_processed = 0
        self.total_files = 0
        self.start_time = None
        self.cancelled = False

        # GUI elements
        self.root = None
        self.step_label = None
        self.file_label = None
        self.progress_bar = None
        self.file_progress_bar = None
        self.status_text = None
        self.time_label = None
        self.cancel_button = None

        # Threading
        self.gui_thread = None
        self._gui_ready = threading.Event()

    def start(self):
        """Start the progress tracker GUI in a separate thread."""
        self.start_time = datetime.now()
        self.cancelled = False

        # Start GUI in separate thread
        self.gui_thread = threading.Thread(target=self._create_gui, daemon=True)
        self.gui_thread.start()

        # Wait for GUI to be ready
        self._gui_ready.wait(timeout=2.0)

    def _create_gui(self):
        """Create the GUI window (runs in separate thread)."""
        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🔨 Generating Code Ontology",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Current step
        self.step_label = ttk.Label(
            main_frame,
            text="Initializing...",
            font=("Arial", 11)
        )
        self.step_label.pack(pady=(0, 10))

        # Overall progress bar
        ttk.Label(main_frame, text="Overall Progress:").pack(anchor=tk.W)
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=560
        )
        self.progress_bar.pack(pady=(5, 15), fill=tk.X)

        # File progress
        self.file_label = ttk.Label(
            main_frame,
            text="Files: 0 / 0",
            font=("Arial", 9)
        )
        self.file_label.pack(anchor=tk.W)

        self.file_progress_bar = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=560
        )
        self.file_progress_bar.pack(pady=(5, 15), fill=tk.X)

        # Current file being processed
        ttk.Label(main_frame, text="Current File:").pack(anchor=tk.W)
        self.current_file_label = ttk.Label(
            main_frame,
            text="",
            font=("Arial", 9),
            foreground="gray"
        )
        self.current_file_label.pack(anchor=tk.W, pady=(0, 15))

        # Status text area
        ttk.Label(main_frame, text="Status Log:").pack(anchor=tk.W)
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 15))

        scrollbar = ttk.Scrollbar(status_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_text = tk.Text(
            status_frame,
            height=8,
            width=70,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.status_text.yview)

        # Time and cancel button frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X)

        self.time_label = ttk.Label(
            bottom_frame,
            text="Elapsed: 0s",
            font=("Arial", 9),
            foreground="gray"
        )
        self.time_label.pack(side=tk.LEFT)

        self.cancel_button = ttk.Button(
            bottom_frame,
            text="Cancel",
            command=self._on_cancel
        )
        self.cancel_button.pack(side=tk.RIGHT)

        # Mark GUI as ready
        self._gui_ready.set()

        # Start time update loop
        self._update_time()

        # Start mainloop
        self.root.mainloop()

    def _update_time(self):
        """Update elapsed time display."""
        if self.root and self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()

            if elapsed < 60:
                time_str = f"Elapsed: {int(elapsed)}s"
            elif elapsed < 3600:
                minutes = int(elapsed / 60)
                seconds = int(elapsed % 60)
                time_str = f"Elapsed: {minutes}m {seconds}s"
            else:
                hours = int(elapsed / 3600)
                minutes = int((elapsed % 3600) / 60)
                time_str = f"Elapsed: {hours}h {minutes}m"

            self.time_label.config(text=time_str)

            # Estimate remaining time
            if self.total_files > 0 and self.files_processed > 0:
                progress = self.files_processed / self.total_files
                if progress > 0:
                    total_estimated = elapsed / progress
                    remaining = total_estimated - elapsed

                    if remaining < 60:
                        est_str = f" | Est. remaining: {int(remaining)}s"
                    elif remaining < 3600:
                        minutes = int(remaining / 60)
                        est_str = f" | Est. remaining: {minutes}m"
                    else:
                        hours = int(remaining / 3600)
                        minutes = int((remaining % 3600) / 60)
                        est_str = f" | Est. remaining: {hours}h {minutes}m"

                    time_str += est_str
                    self.time_label.config(text=time_str)

            # Schedule next update
            if self.root:
                self.root.after(500, self._update_time)

    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.add_status("❌ Cancellation requested...")
        if self.cancel_button:
            self.cancel_button.config(state=tk.DISABLED, text="Cancelling...")

    def update_step(self, step: int, step_name: str):
        """
        Update current step.

        Args:
            step: Step number (1-based)
            step_name: Description of the step
        """
        self.current_step = step

        if self.root and self.step_label:
            self.root.after(0, lambda: self.step_label.config(
                text=f"Step {step}/{self.total_steps}: {step_name}"
            ))

            # Update overall progress bar
            progress = (step / self.total_steps) * 100
            self.root.after(0, lambda: self.progress_bar.config(value=progress))

        self.add_status(f"\n{'='*60}")
        self.add_status(f"📍 Step {step}/{self.total_steps}: {step_name}")
        self.add_status(f"{'='*60}")

    def set_total_files(self, total: int):
        """Set total number of files to process."""
        self.total_files = total
        self.files_processed = 0

        if self.root and self.file_label:
            self.root.after(0, lambda: self.file_label.config(
                text=f"Files: 0 / {total}"
            ))

    def update_file(self, file_path: str):
        """
        Update current file being processed.

        Args:
            file_path: Path to the file
        """
        self.current_file = file_path
        self.files_processed += 1

        if self.root:
            # Update file counter
            if self.file_label:
                self.root.after(0, lambda: self.file_label.config(
                    text=f"Files: {self.files_processed} / {self.total_files}"
                ))

            # Update file progress bar
            if self.file_progress_bar and self.total_files > 0:
                progress = (self.files_processed / self.total_files) * 100
                self.root.after(0, lambda: self.file_progress_bar.config(value=progress))

            # Update current file label (show last 60 chars)
            if self.current_file_label:
                display_path = file_path
                if len(file_path) > 60:
                    display_path = "..." + file_path[-57:]
                self.root.after(0, lambda: self.current_file_label.config(text=display_path))

    def add_status(self, message: str):
        """
        Add a status message to the log.

        Args:
            message: Status message
        """
        if self.root and self.status_text:
            def _add():
                self.status_text.config(state=tk.NORMAL)
                self.status_text.insert(tk.END, message + "\n")
                self.status_text.see(tk.END)
                self.status_text.config(state=tk.DISABLED)

            self.root.after(0, _add)

    def complete(self, success=True):
        """
        Mark process as complete.

        Args:
            success: Whether the process completed successfully
        """
        if self.root:
            if success:
                self.add_status("\n✅ Ontology generation complete!")
                self.root.after(0, lambda: self.step_label.config(
                    text="✅ Complete!"
                ))
                self.root.after(0, lambda: self.progress_bar.config(value=100))
                self.root.after(0, lambda: self.cancel_button.config(
                    text="Close",
                    state=tk.NORMAL
                ))
            else:
                self.add_status("\n❌ Process failed or cancelled")
                self.root.after(0, lambda: self.step_label.config(
                    text="❌ Failed"
                ))

    def close(self):
        """Close the progress window."""
        if self.root:
            self.root.quit()
            self.root.destroy()

    def is_cancelled(self) -> bool:
        """Check if user cancelled the operation."""
        return self.cancelled


# For console-only mode (no GUI)
class ConsoleProgressTracker:
    """Progress tracker that only prints to console."""

    def __init__(self, title="Progress", total_steps=7):
        self.title = title
        self.total_steps = total_steps
        self.current_step = 0
        self.files_processed = 0
        self.total_files = 0
        self.cancelled = False

    def start(self):
        print(f"\n{'='*70}")
        print(f"🚀 {self.title}")
        print(f"{'='*70}\n")

    def update_step(self, step: int, step_name: str):
        self.current_step = step
        print(f"\n{'='*70}")
        print(f"📍 Step {step}/{self.total_steps}: {step_name}")
        print(f"{'='*70}")

    def set_total_files(self, total: int):
        self.total_files = total
        self.files_processed = 0
        print(f"   Total files to process: {total}")

    def update_file(self, file_path: str):
        self.files_processed += 1
        if self.files_processed % 10 == 0:  # Print every 10 files
            progress = (self.files_processed / self.total_files * 100) if self.total_files > 0 else 0
            print(f"   Processed: {self.files_processed}/{self.total_files} ({progress:.1f}%)")

    def add_status(self, message: str):
        print(f"   {message}")

    def complete(self, success=True):
        if success:
            print(f"\n{'='*70}")
            print("✅ Complete!")
            print(f"{'='*70}\n")
        else:
            print(f"\n{'='*70}")
            print("❌ Failed or cancelled")
            print(f"{'='*70}\n")

    def close(self):
        pass

    def is_cancelled(self) -> bool:
        return False
