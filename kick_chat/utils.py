import os
import sys
from pathlib import Path

from curl_cffi import requests
from term_image.image import KittyImage, auto_image_class
from term_image.utils import get_terminal_name_version

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from kick_chat import kitty
from kick_chat.constants import (
    BADGE_DEFAULT_COLOR,
    BADGE_STYLES,
    EMOTE_HEIGHT,
    EMOTE_PATTERN,
    EMOTE_URL,
    RESET,
)

CACHE_DIR = Path.home() / ".cache" / "kick-chat" / "emotes"


def hex_to_rgb(val: str) -> tuple[int, int, int]:
    return (int(val[i : i + 2], 16) for i in (1, 3, 5))


def render_badges(badges: list) -> str:
    """Render Kick rank badges (sender.identity.badges) as short colored tags to
    place before the username, e.g. "[MOD][SUB] ". Returns "" when there are none.
    Unknown badge types fall back to their payload "text"."""
    tags = []
    for badge in sorted(badges, key=lambda b: b.get("sort_order", 0)):
        label, color = BADGE_STYLES.get(
            badge.get("type"),
            (badge.get("text") or badge.get("type") or "?", BADGE_DEFAULT_COLOR),
        )
        r, g, b = color
        tags.append(f"\033[38;2;{r};{g};{b}m[{label}]{RESET}")
    return "".join(tags) + " " if tags else ""


def pick_image_class():
    """Choose how to render emotes. term-image 0.7.2 only enables the kitty
    graphics protocol for terminals it recognises by name (kitty, konsole), so it
    refuses Ghostty and falls back to blocky half-block rendering even though
    Ghostty fully supports the protocol. Detect such terminals and force kitty.

    Skipped under tmux/screen, which block graphics passthrough — there the only
    option is the block-based fallback."""
    if not os.environ.get("TMUX") and not os.environ.get("STY"):
        name = (get_terminal_name_version()[0] or "").lower()
        if name == "ghostty" or os.environ.get("TERM_PROGRAM") == "ghostty":
            KittyImage.forced_support = True
            return KittyImage
    return auto_image_class()


def iter_message_parts(content: str):
    """Split message content into ("text", str) and ("emote", id, name) parts,
    preserving order. Emotes are encoded by Kick inline as [emote:<id>:<name>]."""
    last = 0
    for match in EMOTE_PATTERN.finditer(content):
        if match.start() > last:
            yield ("text", content[last : match.start()])
        yield ("emote", match.group(1), match.group(2))
        last = match.end()
    if last < len(content):
        yield ("text", content[last:])


class EmoteCache:
    """Downloads and renders Kick emotes once per id, caching the PNG on disk and
    the rendered terminal string in memory. Falls back to :name: on any failure."""

    def __init__(self):
        self._rendered: dict[str, str] = {}
        self._animations: dict[str, kitty.Animation] = {}
        self._image_class = pick_image_class()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _download(self, emote_id: str, path: Path) -> None:
        res = requests.get(
            EMOTE_URL.format(id=emote_id), impersonate="chrome110"
        )
        res.raise_for_status()
        path.write_bytes(res.content)

    def render(self, emote_id: str, name: str) -> str:
        # Animated emote already transmitted: just re-place the shared image.
        if emote_id in self._animations:
            return self._animations[emote_id].place
        if emote_id in self._rendered:
            return self._rendered[emote_id]
        try:
            path = CACHE_DIR / f"{emote_id}.png"
            if not path.exists():
                self._download(emote_id, path)
            # Native kitty animation for animated emotes (kitty terminals only);
            # the terminal loops the frames itself without blocking the chat.
            if self._image_class is KittyImage:
                animation = kitty.build(
                    str(path), self._image_class, EMOTE_HEIGHT
                )
                if animation is not None:
                    self._animations[emote_id] = animation
                    return animation.transmit
            image = self._image_class.from_file(str(path))
            image.set_size(height=EMOTE_HEIGHT)
            rendered = str(image)
        except Exception:
            rendered = f":{name}:"
        self._rendered[emote_id] = rendered
        return rendered
