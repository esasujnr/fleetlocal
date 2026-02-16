# Fleet Local

This repository contains the `fleetshare_ws.py` script used to send MAVLink data to my FleetShare server 🚀.

## Download the project 📥

There are two ways to retrieve this repository:

- **Clone with Git**
```bash
  git clone https://github.com/<your-username>/fleetlocal.git
  ```
- **Download the ZIP archive from GitHub**
  On the repository page, click **Code** then **Download ZIP**, then unzip the archive.

## Prerequisites 📦

- Python 3.8 or higher installed on your machine. You can download it from [python.org](https://www.python.org/downloads/).
- An Internet connection to install Python dependencies.

## Installation and execution in Windows PowerShell 💻

1. Open **Windows PowerShell**.
2. Navigate to the project directory:
```powershell
   cd path\to\cloned\folder
   ```
3. Install the dependencies defined in `requirements.txt`:
```powershell
   pip install -r requirements.txt
   ```
4. Run the script from a terminal 🖥️:
```powershell
   python fleetshare_ws.py
   ```

The script connects to the MAVLink stream provided by `WS_URI` and periodically sends the data to the configured HTTP server.

## Error messages ⚠️

If you receive an error message or the script freezes, try the following steps:

1. Press **CTRL+W** to kill the script in the console. 🛑
2. Use the **up arrow** to recall the previous command. ⬆️
3. Press **Enter** to restart the script. 🔁

If the errors persist, check your Internet connection and the `WS_URI` and `HTTP_ENDPOINT` settings.

## In-flight use ✈️

The streamer must remain **running throughout the flight** in order to continue sending
telemetry information. This information is available in raw data form at
<https://fleetshare.onrender.com/drone-position> and can be viewed
on the map at <https://fleetshare.onrender.com>.

If the streamer is connected when the pilot sends the “PN Playback” command,
it retrieves the mission waypoints and also displays them on
the web interface.

