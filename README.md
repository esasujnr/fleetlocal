# Fleet Local

This repository contains the `fleetshare_ws.py` script used to send MAVLink data to my FleetShare server 🚀.

## Download the project 📥

There are two ways to retrieve this repository:

- **Clone with Git**
```bash
  https://github.com/esasujnr/fleetlocal.git
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

If you encounter an error message or the script freezes, try the following steps:

1. Press **CTRL+W** to kill the script in the console. 🛑
2. Use the **up arrow** to recall the previous command. ⬆️
3. Press **Enter** to restart.

Translated with DeepL.com (free version)
