"""SAMINFO GUI entrypoint.

The app waits for a connected Samsung device, reads AT+DEVCONINFO,
and displays the parsed information.
"""

from __future__ import annotations

import threading
import time

import customtkinter as ctk

from saminfo.device import ATDeviceInfo, DeviceATError, DeviceNotFoundError, read_device_info_at


class SamInfoApp(ctk.CTk):
    """Desktop GUI for Samsung device information over AT commands."""

    def __init__(self) -> None:
        """Initialize the window, widgets, and background polling."""
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("SAMINFO")
        self.geometry("760x420")
        self.minsize(680, 380)

        self._stop_event = threading.Event()
        self._build_ui()
        self._start_polling_thread()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(
            self,
            text="Samsung Device Information",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Waiting for Samsung device...",
            font=ctk.CTkFont(size=14),
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        self.info_box = ctk.CTkTextbox(self, wrap="word", font=ctk.CTkFont(size=14))
        self.info_box.grid(row=2, column=0, padx=20, pady=(0, 12), sticky="nsew")
        self.info_box.insert("1.0", "No device information available yet.")
        self.info_box.configure(state="disabled")

        self.refresh_button = ctk.CTkButton(
            self,
            text="Refresh Now",
            command=self._refresh_once,
        )
        self.refresh_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="e")

    def _start_polling_thread(self) -> None:
        thread = threading.Thread(target=self._poll_device_loop, daemon=True)
        thread.start()

    def _poll_device_loop(self) -> None:
        while not self._stop_event.is_set():
            self._query_and_update()
            time.sleep(2.0)

    def _refresh_once(self) -> None:
        thread = threading.Thread(target=self._query_and_update, daemon=True)
        thread.start()

    def _query_and_update(self) -> None:
        self._set_status("Status: Searching for Samsung device...")
        try:
            device_info = read_device_info_at(timeout=2.0)
        except DeviceNotFoundError:
            self._set_status("Status: Waiting for Samsung device...")
            return
        except DeviceATError as ex:
            self._set_status(f"Status: AT error: {ex}")
            return
        except Exception as ex:  # noqa: BLE001
            self._set_status(f"Status: Unexpected error: {ex}")
            return

        self._set_status("Status: Device connected and info loaded.")
        self._set_info(device_info)

    def _set_status(self, message: str) -> None:
        self.after(0, lambda: self.status_label.configure(text=message))

    def _set_info(self, info: ATDeviceInfo) -> None:
        content = "\n".join([
            f"Model: {info.model or '-'}",
            f"Firmware: {info.firmware_version or '-'}",
            f"Sales Code: {info.sales_code or '-'}",
            f"IMEI: {info.imei or '-'}",
            f"Serial Number: {info.serial_number or '-'}",
            f"Lock Status: {info.lock_status or '-'}",
            f"AID: {info.aid or '-'}",
            f"Country Code: {info.cc or '-'}",
        ])

        def _update_box() -> None:
            self.info_box.configure(state="normal")
            self.info_box.delete("1.0", "end")
            self.info_box.insert("1.0", content)
            self.info_box.configure(state="disabled")

        self.after(0, _update_box)

    def destroy(self) -> None:
        """Stop background work before closing the application window."""
        self._stop_event.set()
        super().destroy()
