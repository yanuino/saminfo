# SAMINFO Project Instructions

## Project Overview
**saminfo** is a tool that detects connected Samsung mobile devices and reads device information via AT commands over serial USB connection. The GUI built with `customtkinter` waits for device connection and displays parsed device info.

## Architecture

### Core Modules (src/device/)

**1. detector.py** - Device Detection
- `detect_samsung_devices()` → Returns list of detected Samsung USB modems
  - Scans serial ports for "SAMSUNG MOBILE USB MODEM" signature
  - Extracts VID/PID from hardware IDs
- `get_first_device()` → Auto-detects first Samsung device
  - Simplifies single-device scenarios
  - Raises `DeviceNotFoundError` if no device connected
- `DetectedDevice` NamedTuple:
  - `port_name`: COM port identifier (COM3, /dev/ttyACM0, etc.)
  - `device_name`: Full USB description
  - `manufacturer`, `product`: USB descriptors
  - `vid`, `pid`: USB vendor/product IDs (if available)

**2. at_client.py** - AT Command Interface
- `send_at_command(command, port_name=None, timeout=2.0, expect_ok=True)` → Core serial communication
  - Auto-detects device if `port_name=None`
  - Adds CRLF termination automatically
  - Validates "OK" response if `expect_ok=True`
  - Handles serial timeouts and errors cleanly
  - Returns raw text response from device
  
- `ATDeviceInfo` Dataclass: Target data structure for device information
  - `model`: Device model code (e.g., SM-G991B)
  - `firmware_version`: Full firmware string
  - `sales_code`: 3-char CSC/region (e.g., XAA, DBT)
  - `imei`: 15-digit IMEI
  - `serial_number`: Device SN field
  - `lock_status`: Device lock status
  - `aid`: Access ID
  - `cc`: Country code (e.g., FR)

- `enter_download_mode(port_name=None, timeout=1.0)` → Reboot to Odin mode
  - Sends AT+FUS? command (no response expected)
  - Device immediately disconnects and reboots

**3. device_command.py** - High-Level Operations
- `enter_odin_mode(port_name=None, wait_timeout=10.0, progress_callback=None)` → Enter Odin mode with polling
  - Sends AT+FUS?, waits for device to reboot into download mode
  - Polls Odin port with timeout
  - Returns True/False on success/timeout
  - Calls `progress_callback(msg)` for status updates

**4. errors.py** - Exception Hierarchy
- `DeviceError`: Base exception
- `DeviceNotFoundError`: Device detection failed
- `DeviceATError`: Serial/AT command failures (timeouts, no response, driver issues)
- `DeviceOdinError`: Download mode communication failures

## Application Flow

### 1. Device Detection Phase
```
1. Call detect_samsung_devices() or get_first_device()
2. Wait for device to appear (show UI spinner/status)
3. Handle DeviceNotFoundError if device not connected
```

### 2. Information Retrieval Phase
```
1. Send AT+DEVCONINFO command via send_at_command("AT+DEVCONINFO")
2. Parse response text into ATDeviceInfo fields
3. Handle potential AT errors (timeouts, malformed response)
```

### 3. Display Phase
```
1. Display ATDeviceInfo fields in customtkinter GUI
2. Show model, IMEI, firmware version, etc.
3. Provide clear, user-friendly formatting
```

## Serial Communication Details

**Port Settings:**
- Baud Rate: 115200
- Data Bits: 8
- Parity: None
- Stop Bits: 1
- Timeout: 2.0 seconds (configurable)

**Command Format:**
- Input: AT command (e.g., "AT+DEVCONINFO") → CRLF appended automatically
- Output: Device response text with or without "OK" suffix

## Key Implementation Notes

### Auto-Device Detection
- If `send_at_command(cmd)` called without `port_name`, automatically detects first Samsung device
- Simplifies GUI: no need to let user select port if only one device connected
- Raises `DeviceNotFoundError` if detection fails

### Error Handling Strategy
- **Serial Errors**: `DeviceATError` wraps timeout/connection failures with helpful messages
- **Missing Device**: `DeviceNotFoundError` guides user to check USB connection and drivers
- **Bad Responses**: Check if "OK" present; if `expect_ok=True` and missing, raise error

### GUI Considerations
- **Waiting State**: Show UI element until `get_first_device()` succeeds
- **Async Pattern**: Consider running detection/AT commands in background thread to avoid UI freezing
- **Status Messages**: Display connection status, command progress, errors clearly
- **Field Formatting**: 
  - IMEI: 15-digit display with formatting
  - Firmware: Show as multiline if needed
  - Sales Code: Display with meaning or region info if available

## Dependencies
- `customtkinter>=5.2.2`: GUI framework
- `pyserial>=3.5`: Serial port communication
- Requires Samsung USB drivers (Windows) or libusb-1.0 (Linux)

## Development Guidelines

### Code Style (Ruff / pyproject.toml)
- Max line length: 120
- Target Python version: py314
- Keep formatting compatible with Ruff format settings:
  - quote-style = preserve
  - skip-magic-trailing-comma = false
- Linting rules enabled:
  - E (pycodestyle errors)
  - F (pyflakes)
  - I (isort)
  - B (bugbear)
  - UP (pyupgrade)
  - SIM (simplify)
- Import sorting behavior:
  - combine-as-imports = true
- Ignore/exclude these folders when running checks:
  - .venv
  - venv
  - __pycache__
  - build
  - dist
  - AppIcons

### Docstrings (Google Style)
- Use Google-style docstrings for all public APIs (public modules, classes, methods, and functions).
- Include these sections when applicable:
  - Args:
  - Returns:
  - Raises:
- In Raises:, use this format for each exception:
  - ExceptionType: description
- Do not use parenthetical exception notes. Avoid forms like:
  - ExceptionType: description (if ...)
  - description (raises ExceptionType)

## Windows Driver Requirements
Samsung USB devices appear as "SAMSUNG MOBILE USB MODEM" when drivers installed.
- Download from Samsung support site or use Windows Update
- Detection failure usually indicates driver issue, not software problem

## Related AT Commands
- `AT+DEVCONINFO`: Device connection info (target for this app)
- `AT+FUS?`: Enter download mode (reboot to Odin)
- Other standard AT commands available per device support

## Development Workflow
1. Design customtkinter window layout
2. Implement device waiting logic with timeout
3. Add AT+DEVCONINFO command execution
4. Parse response into ATDeviceInfo
5. Display formatted information in GUI
6. Handle errors with user-friendly messages
7. Test with real Samsung device
