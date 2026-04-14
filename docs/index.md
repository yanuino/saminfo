# SAMINFO

SAMINFO is a small desktop tool that reads Samsung device information over serial AT commands.

## What it does

- detects connected Samsung USB modem ports
- sends AT+DEVCONINFO
- shows parsed data in a simple GUI

## Requirements

- Python 3.14+
- Samsung USB drivers installed on the host machine
- a connected Samsung device exposing a serial modem interface

## Run locally

```bash
uv sync --dev
uv run python -m saminfo
```

## Main modules

- saminfo.app: GUI entry point and periodic polling
- saminfo.device.detector: serial device detection
- saminfo.device.at_client: AT command transport and response parsing
- saminfo.device.device_command: higher-level download/Odin helpers

## API docs

The public device API is documented in the API section.
