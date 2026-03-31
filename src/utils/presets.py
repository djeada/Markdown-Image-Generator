"""Social media image dimension presets."""

from typing import Any, Dict, List

PRESETS: Dict[str, Dict[str, Any]] = {
    "instagram-square": {"width": 1080, "height": 1080, "label": "Instagram Square Post"},
    "instagram-portrait": {"width": 1080, "height": 1350, "label": "Instagram Portrait"},
    "instagram-story": {"width": 1080, "height": 1920, "label": "Instagram/TikTok Story"},
    "twitter": {"width": 1200, "height": 675, "label": "Twitter/X Post"},
    "linkedin": {"width": 1200, "height": 627, "label": "LinkedIn Post"},
    "linkedin-article": {"width": 1200, "height": 644, "label": "LinkedIn Article Cover"},
    "youtube-thumbnail": {"width": 1280, "height": 720, "label": "YouTube Thumbnail"},
    "facebook": {"width": 1200, "height": 630, "label": "Facebook Post"},
    "pinterest": {"width": 1000, "height": 1500, "label": "Pinterest Pin"},
    "presentation": {"width": 1920, "height": 1080, "label": "16:9 Presentation"},
}


def get_preset(name: str) -> Dict[str, Any]:
    """Return the preset dict for *name*.

    Args:
        name: Preset key (case-insensitive, leading/trailing whitespace stripped).

    Returns:
        A dict with ``width``, ``height``, and ``label`` keys.

    Raises:
        KeyError: If the preset name is not recognised.
    """
    key = name.strip().lower()
    if key not in PRESETS:
        available = ", ".join(sorted(PRESETS))
        raise KeyError(f"Unknown preset '{name}'. Available presets: {available}")
    return PRESETS[key]


def list_presets() -> List[Dict[str, Any]]:
    """Return a list of all presets with their names included.

    Each element is a dict with ``name``, ``width``, ``height``, and ``label``.
    """
    return [{"name": k, **v} for k, v in PRESETS.items()]
