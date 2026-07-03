"""Native kitty-graphics animation for emotes.

term-image can only draw an animation by blocking and redrawing frames in place,
which is useless in a scrolling chat. The kitty graphics protocol instead lets the
*terminal* cycle the frames on its own: we transmit every frame once, start an
infinite loop, and each later occurrence of the emote just re-places the same image
id. This module builds those escape sequences by hand.

See https://sw.kovidgoyal.net/kitty/graphics-protocol/#animation
"""

import base64
from itertools import count

from PIL import Image
from term_image.utils import get_cell_size

# Start high to avoid clashing with ids other tools may have transmitted.
_next_id = count(1_000_000)


def _cmd(control: dict, payload: bytes = b"") -> str:
    """Serialize one graphics command, chunking the base64 payload at 4096 bytes."""
    ctl = ",".join(f"{k}={v}" for k, v in control.items())
    if not payload:
        return f"\033_G{ctl}\033\\"
    data = base64.standard_b64encode(payload)
    chunks = [data[i : i + 4096] for i in range(0, len(data), 4096)]
    parts = []
    for i, chunk in enumerate(chunks):
        more = 1 if i < len(chunks) - 1 else 0
        header = f"{ctl},m={more}" if i == 0 else f"m={more}"
        parts.append(f"\033_G{header};{chunk.decode('ascii')}\033\\")
    return "".join(parts)


class Animation:
    """A decoded animated emote plus its prebuilt kitty escape sequences."""

    def __init__(self, transmit: str, place: str):
        self.transmit = transmit  # first occurrence: upload frames + start loop
        self.place = place  # later occurrences: just display the shared image


def _load_frames(path: str, cols: int, rows: int):
    """Return (frames, width, height) where frames is a list of (rgba, duration_ms).
    Frames are scaled to the on-screen pixel size when the cell size is known, to
    bound how much data we push to the terminal."""
    img = Image.open(path)
    cell = get_cell_size()  # (width, height) in pixels, or None
    size = (cols * cell[0], rows * cell[1]) if cell else None

    frames = []
    for i in range(img.n_frames):
        img.seek(i)
        frame = img.convert("RGBA")
        if size:
            frame = frame.resize(size, Image.LANCZOS)
        duration = int(img.info.get("duration", 100)) or 100
        frames.append((frame.tobytes(), duration))
    width, height = (size if size else img.size)
    return frames, width, height


def build(path: str, image_class, height: int):
    """Build an :class:`Animation` for an animated image, or return None if the
    image is not animated."""
    img = Image.open(path)
    if not getattr(img, "is_animated", False) or img.n_frames < 2:
        return None

    # Reuse term-image's sizing so animated emotes match static ones.
    sized = image_class.from_file(path)
    sized.set_size(height=height)
    cols, rows = sized.rendered_size

    frames, w, h = _load_frames(path, cols, rows)
    image_id = next(_next_id)
    root_rgba, root_gap = frames[0]

    seq = [
        # Frame 1: transmit and display at the cursor, scaled into cols x rows.
        _cmd(
            {"a": "T", "i": image_id, "f": 32, "s": w, "v": h,
             "c": cols, "r": rows, "q": 2},
            root_rgba,
        )
    ]
    # Frames 2..N appended with their own gap (z, milliseconds).
    for rgba, gap in frames[1:]:
        seq.append(
            _cmd({"a": "f", "i": image_id, "f": 32, "s": w, "v": h,
                  "z": gap, "q": 2}, rgba)
        )
    # a=T carries no gap for frame 1, so set it by editing frame 1 (r=1).
    seq.append(
        _cmd({"a": "f", "i": image_id, "f": 32, "s": w, "v": h,
              "r": 1, "z": root_gap, "q": 2}, root_rgba)
    )
    # Start looping forever (v=1 == infinite).
    seq.append(_cmd({"a": "a", "i": image_id, "s": 3, "v": 1, "q": 2}))

    place = _cmd({"a": "p", "i": image_id, "c": cols, "r": rows, "q": 2})
    return Animation("".join(seq), place)
