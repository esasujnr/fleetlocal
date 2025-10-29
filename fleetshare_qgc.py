"""
Lecture du flux MAVLink UDP retransmis par QGroundControl et publication
des donnees vers le serveur FleetShare.
"""

import asyncio
import time
from functools import partial

import requests
from pymavlink import mavutil

UDP_URI = "udp:127.0.0.1:56781"
HTTP_ENDPOINT = "https://fleetshare-wingxtra.onrender.com/drone-position"
HTTP_ENDPOINT_MISSION = "https://fleetshare-wingxtra.onrender.com/drone-mission"
MIN_INTERVAL = 2.0  # secondes


class TelemetryState:
    def __init__(self) -> None:
        self.last_send_time = 0.0
        self.last_lat = None
        self.last_lon = None
        self.last_yaw = None
        self.last_alt = None
        self.last_groundspeed = None
        self.last_airspeed = None
        self.last_windspeed = None
        self.last_position_sysid = None
        self.last_mission_sysid = None
        self.timestamp = None
        self.mission_expected_count = 0
        self.mission_received_count = 0
        self.waypoints = []

    def reset_mission(self) -> None:
        self.mission_expected_count = 0
        self.mission_received_count = 0
        self.waypoints = []
        self.last_mission_sysid = None


def is_waypoint(msg) -> bool:
    # MAV_CMD_NAV_WAYPOINT = 16
    return hasattr(msg, "command") and msg.command == 16


def extract_latlon(msg):
    if hasattr(msg, "x") and hasattr(msg, "y"):
        return round(msg.x, 7), round(msg.y, 7)
    if hasattr(msg, "param5") and hasattr(msg, "param6"):
        return round(msg.param5 * 1e-7, 7), round(msg.param6 * 1e-7, 7)
    return None, None


def get_msg_sysid(msg):
    msg_sysid = None
    try:
        msg_sysid = msg.get_srcSystem()
    except Exception:
        pass
    if msg_sysid is None and hasattr(msg, "_header") and hasattr(msg._header, "srcSystem"):
        msg_sysid = msg._header.srcSystem
    return msg_sysid


def post_position(state: TelemetryState) -> None:
    payload = {
        "timestamp": state.timestamp,
        "lat": state.last_lat,
        "lon": state.last_lon,
        "yaw": state.last_yaw,
        "alt": state.last_alt,
        "groundspeed": state.last_groundspeed,
        "airspeed": state.last_airspeed,
        "windspeed": state.last_windspeed,
        "sysid": state.last_position_sysid,
    }
    try:
        resp = requests.post(
            HTTP_ENDPOINT,
            json=payload,
            headers={"User-Agent": "PyFleet/1.0"},
        )
        if resp.status_code == 200:
            print(
                "POST OK - "
                f"timestamp={state.timestamp} lat={state.last_lat} "
                f"lon={state.last_lon} yaw={state.last_yaw} alt={state.last_alt} "
                f"groundspeed={state.last_groundspeed} airspeed={state.last_airspeed} "
                f"windspeed={state.last_windspeed} sysid={state.last_position_sysid}"
            )
        else:
            print("Erreur HTTP :", resp.status_code, resp.text)
    except Exception as exc:
        print("Exception lors du POST :", exc)


def post_mission(state: TelemetryState) -> None:
    if not state.waypoints:
        return

    mission_sysid = state.last_mission_sysid or state.last_position_sysid
    if mission_sysid is None:
        print("Impossible d'envoyer la mission : sysid inconnu.")
        return

    wp_str = " ".join(
        [f"WP{i + 1}: {lat},{lon}" for i, (lat, lon) in enumerate(state.waypoints)]
    )
    payload = {"waypoints": wp_str, "sysid": mission_sysid}
    try:
        resp = requests.post(
            HTTP_ENDPOINT_MISSION,
            json=payload,
            headers={"User-Agent": "PyFleet/1.0"},
        )
        if resp.status_code == 200:
            print(f"POST WP OK - {wp_str} sysid={mission_sysid}")
        else:
            print("Erreur HTTP WP :", resp.status_code, resp.text)
    except Exception as exc:
        print("Exception lors du POST WP :", exc)


def handle_mission_message(msg, msg_sysid, state: TelemetryState) -> None:
    msg_id = msg.get_msgId()
    mavlink = mavutil.mavlink

    if msg_id == mavlink.MAVLINK_MSG_ID_MISSION_COUNT:
        state.mission_expected_count = msg.count
        state.mission_received_count = 0
        state.waypoints = []
        if msg_sysid is not None:
            state.last_mission_sysid = msg_sysid
        print(f"Reception de mission : {state.mission_expected_count} waypoints attendus.")
        return

    if msg_id in (mavlink.MAVLINK_MSG_ID_MISSION_ITEM, mavlink.MAVLINK_MSG_ID_MISSION_ITEM_INT):
        if is_waypoint(msg):
            lat, lon = extract_latlon(msg)
            if lat is not None and lon is not None:
                state.waypoints.append((lat, lon))
                print(f"Waypoint recu ({len(state.waypoints)}): {lat}, {lon}")
        state.mission_received_count += 1
        if msg_sysid is not None:
            state.last_mission_sysid = msg_sysid

        if (
            state.mission_expected_count > 0
            and state.mission_received_count == state.mission_expected_count
        ):
            post_mission(state)
            state.reset_mission()


def handle_position_message(msg, msg_sysid, state: TelemetryState) -> None:
    msg_id = msg.get_msgId()
    mavlink = mavutil.mavlink

    if msg_id == mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
        state.last_lat = round(msg.lat * 1e-7, 7)
        state.last_lon = round(msg.lon * 1e-7, 7)
        state.last_yaw = round(msg.hdg * 0.01, 2)
        state.timestamp = int(time.time())
        if msg_sysid is not None:
            state.last_position_sysid = msg_sysid
        return

    if msg_id == mavlink.MAVLINK_MSG_ID_VFR_HUD:
        if state.last_position_sysid is None or msg_sysid == state.last_position_sysid:
            state.last_groundspeed = round(msg.groundspeed, 2)
            state.last_airspeed = round(msg.airspeed, 2)
            state.last_alt = round(msg.alt, 2)
        return

    if msg_id == mavlink.MAVLINK_MSG_ID_WIND:
        if state.last_position_sysid is None or msg_sysid == state.last_position_sysid:
            state.last_windspeed = round(msg.speed, 2)
        return

    if msg_id == mavlink.MAVLINK_MSG_ID_HIGH_LATENCY2:
        state.last_lat = round(msg.latitude, 7)
        state.last_lon = round(msg.longitude, 7)
        state.last_alt = msg.altitude
        state.last_groundspeed = round(msg.groundspeed, 2)
        state.last_airspeed = round(msg.airspeed, 2)
        state.last_yaw = msg.heading
        if msg_sysid is not None:
            state.last_position_sysid = msg_sysid
        state.timestamp = int(time.time())


def should_send(state: TelemetryState) -> bool:
    if state.last_lat is None or state.last_position_sysid is None:
        return False
    now = time.monotonic()
    if now - state.last_send_time < MIN_INTERVAL:
        return False
    state.last_send_time = now
    return True


async def stream_positions(state: TelemetryState) -> None:
    loop = asyncio.get_running_loop()
    mav = mavutil.mavlink_connection(UDP_URI, dialect="common", source_system=255)
    print(f"En ecoute sur {UDP_URI} pour les paquets MAVLink.")

    try:
        while True:
            msg = await loop.run_in_executor(
                None, partial(mav.recv_match, blocking=True, timeout=1)
            )
            if msg is None:
                continue

            msg_sysid = get_msg_sysid(msg)
            try:
                handle_mission_message(msg, msg_sysid, state)
                handle_position_message(msg, msg_sysid, state)
            except AttributeError:
                continue

            if should_send(state):
                post_position(state)
    finally:
        try:
            mav.close()
        except Exception:
            pass


async def main() -> None:
    state = TelemetryState()
    while True:
        try:
            await stream_positions(state)
        except Exception as exc:
            print("Erreur de connexion ou de lecture :", exc)
        print("Nouvelle tentative dans 3 secondes...")
        await asyncio.sleep(3)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nArret par l'utilisateur.")
