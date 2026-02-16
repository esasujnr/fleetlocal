# Fleet Local

This repository contains the `fleetshare_ws.py` script for sending MAVLink data to the FleetShare service.

## Prerequisites

- Python 3.8 or higher installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).
- An Internet connection to install Python dependencies.

## Installation and execution in Windows PowerShell

1. Open **Windows PowerShell**.
2. Navigate to the project directory:
```powershell
   cd path\to\cloned\folder
   ```
3. (Optional) Create a virtual environment to isolate dependencies:
```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
4. Install the dependencies defined in `requirements.txt`:
```powershell
   pip install -r requirements.txt
   ```
5. Run the script:
```powershell
python fleetshare_ws.py
```

The script connects to the MAVLink stream provided by `WS_URI` and periodically sends the data to the configured HTTP server.

## In-flight use

The streamer must remain **running throughout the flight** in order to continue sending
telemetry information. This information is available in raw data form at
<https://fleetshare.onrender.com/drone-position> and can be viewed
on the map at <https://fleetshare.onrender.com>.

If the streamer is connected when the pilot sends the “PN Playback” command,
it retrieves the mission waypoints and also displays them on
the web interface.
