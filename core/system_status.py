# core/system_status.py
"""
System status — CPU, RAM, disk, temperature, fan, task manager.
"""

import logging
import platform
import subprocess

import psutil

logger = logging.getLogger("VoiceAssist.SystemStatus")

PLATFORM = platform.system()


def cpu_usage() -> str:
    """Return current CPU usage percentage."""
    try:
        percent = psutil.cpu_percent(interval=1)
        return f"CPU usage is {percent}%"
    except Exception as e:
        logger.error(f"CPU usage error: {e}", exc_info=True)
        return "Sorry, could not get CPU usage"


def ram_usage() -> str:
    """Return current RAM usage."""
    try:
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        return f"RAM usage is {mem.percent}% — {used_gb:.1f} GB of {total_gb:.1f} GB used"
    except Exception as e:
        logger.error(f"RAM usage error: {e}", exc_info=True)
        return "Sorry, could not get RAM usage"


def disk_usage(path: str = None) -> str:
    """Return disk usage for the given path."""
    try:
        if path is None:
            path = "C:\\" if PLATFORM == "Windows" else "/"

        disk = psutil.disk_usage(path)
        used_gb = disk.used / (1024 ** 3)
        total_gb = disk.total / (1024 ** 3)
        return f"Disk usage is {disk.percent}% — {used_gb:.1f} GB of {total_gb:.1f} GB used"
    except Exception as e:
        logger.error(f"Disk usage error: {e}", exc_info=True)
        return "Sorry, could not get disk usage"


def get_temperature() -> str:
    """Return CPU temperature if available."""
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return "Temperature data not available on this system"

        # Get the first available temperature reading
        for name, entries in temps.items():
            if entries:
                temp = entries[0].current
                return f"CPU temperature is {temp}°C"

        return "Temperature data not available on this system"
    except AttributeError:
        return "Temperature data not available on this system"
    except Exception as e:
        logger.error(f"Temperature error: {e}", exc_info=True)
        return "Could not read temperature data"


def get_fan_speed() -> str:
    """Return fan speed if available."""
    try:
        fans = psutil.sensors_fans()
        if not fans:
            return "Fan speed data not available on this system"

        for name, entries in fans.items():
            if entries:
                rpm = entries[0].current
                return f"Fan speed is {rpm} RPM"

        return "Fan speed data not available on this system"
    except AttributeError:
        return "Fan speed data not available on this system"
    except Exception as e:
        logger.error(f"Fan speed error: {e}", exc_info=True)
        return "Could not read fan speed data"


def full_status() -> str:
    """Return combined system status summary."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        if PLATFORM == "Windows":
            disk = psutil.disk_usage("C:\\")
        else:
            disk = psutil.disk_usage("/")

        return f"System status: CPU at {cpu}%, RAM at {mem.percent}%, Disk at {disk.percent}%"
    except Exception as e:
        logger.error(f"Full status error: {e}", exc_info=True)
        return "Sorry, could not get system status"


def open_task_manager() -> str:
    """Open the system's task manager / activity monitor."""
    try:
        if PLATFORM == "Windows":
            subprocess.Popen(["taskmgr"])
        elif PLATFORM == "Darwin":
            subprocess.Popen(["open", "-a", "Activity Monitor"])
        elif PLATFORM == "Linux":
            try:
                subprocess.Popen(["gnome-system-monitor"])
            except FileNotFoundError:
                subprocess.Popen(["xterm", "-e", "htop"])

        return "Opening task manager"
    except Exception as e:
        logger.error(f"Task manager error: {e}", exc_info=True)
        return "Could not open task manager"
