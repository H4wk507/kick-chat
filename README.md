# kick-chat

kick.com chat in the terminal

## About

kick-chat is a terminal chat client for [Kick](https://kick.com/) chat.
It aims to provide a simple and minimalistic way of listening to chat messages.

Emotes are rendered inline as real images. This works best in terminals with
graphics support (kitty, iTerm2, WezTerm); other terminals automatically fall
back to a block-character rendering, or to a `:name:` text placeholder if an
emote cannot be fetched.

Animated emotes (GIFs) loop natively in kitty (and other terminals implementing
kitty's graphics animation): the frames are uploaded once and the terminal cycles
them itself, so the chat is never blocked. Elsewhere an animated emote shows its
first frame as a still image.

Rank badges (moderator, VIP, subscriber, ...) are shown as short colored tags
before the username, e.g. `[MOD][SUB] username`.

## Installation

```
pip install kick-chat
```

## How to use

Simply put Kick username as the first argument to the program call.

```
kick-chat xQc
```

## License

Licensed under [GPLv3 License](./LICENSE).
