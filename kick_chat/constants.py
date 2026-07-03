import re

RESET = "\033[0m"
SOCKET_URL = "wss://ws-us2.pusher.com/app/32cbd69e4b950bf97679?protocol=7&client=js&version=8.5.0&flash=false"
EMOTE_URL = "https://files.kick.com/emotes/{id}/fullsize"
EMOTE_PATTERN = re.compile(r"\[emote:(\d+):([^\]]+)\]")
EMOTE_HEIGHT = 1  # emote height in terminal rows; bump for bigger emotes

# Short label + 24-bit color for known Kick badge types (sender.identity.badges).
# Unknown types fall back to the badge's own "text" with a neutral color.
BADGE_STYLES = {
    "broadcaster": ("HOST", (255, 60, 60)),
    "moderator": ("MOD", (0, 199, 120)),
    "verified": ("✓", (30, 150, 255)),
    "vip": ("VIP", (255, 90, 200)),
    "og": ("OG", (0, 200, 190)),
    "founder": ("FDR", (255, 160, 40)),
    "subscriber": ("SUB", (83, 252, 24)),
    "sub_gifter": ("GIFT", (170, 120, 255)),
}
BADGE_DEFAULT_COLOR = (150, 150, 150)
