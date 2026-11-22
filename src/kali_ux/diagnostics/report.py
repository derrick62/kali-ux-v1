"""Read-only diagnostic report; excludes environment values and user data."""

from kali_ux.control_center.model import ControlCenterModel
from kali_ux.core.registry import FEATURES
from kali_ux.features.gesture_control.conflicts import inspect_gesture_providers
from kali_ux.platform.capabilities import detect


def build_report() -> dict:
    platform = detect()
    try:
        model = ControlCenterModel()
        features = model.rows()
        config_error = None
    except (OSError, ValueError) as exc:
        # Keep diagnostics usable when a user's config is malformed. Do not
        # overwrite or silently repair it; report the issue for manual recovery.
        features = [
            {
                "key": feature.key,
                "title": feature.title,
                "implementation": feature.status,
                "requirements": list(feature.requires),
                "state": "configuration unavailable",
            }
            for feature in FEATURES
        ]
        config_error = str(exc)

    providers = [
        {
            "name": item.name,
            "installed": item.installed,
            "running": item.running,
            "autostart_entries": list(item.autostart_entries),
            "may_conflict": item.may_conflict,
        }
        for item in inspect_gesture_providers()
    ]
    report = {
        "platform": platform,
        "features": features,
        "gesture_providers": providers,
        "notes": [
            "No system settings were changed.",
            "Feature preferences do not start background services.",
            "Gesture input is not started automatically.",
            "Window thumbnails are captured on demand in the local X11 session "
            "and are not persisted.",
            "Other gesture handlers are reported but never disabled or reconfigured automatically.",
        ],
    }
    if config_error:
        report["configuration_error"] = config_error
    return report
