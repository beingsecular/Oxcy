import math
from pyrogram.types import InlineKeyboardButton
from BrandrdXMusic.utils.formatters import time_to_seconds


# =========================
# TRACK MARKUP
# =========================
def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="×",
                callback_data=f"forceclose {user_id}",
            )
        ],
    ]


# =========================
# STREAM TIMER MARKUP (SPOTIFY STYLE)
# =========================
def stream_markup_timer(_, vidid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur) or 1
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)

    if 0 < umm <= 10:
        bar = "▰▱▱▱▱▱▱▱▱▱"
    elif 10 < umm < 20:
        bar = "▰▰▱▱▱▱▱▱▱▱"
    elif 20 <= umm < 30:
        bar = "▰▰▰▱▱▱▱▱▱▱"
    elif 30 <= umm < 40:
        bar = "▰▰▰▰▱▱▱▱▱▱"
    elif 40 <= umm < 50:
        bar = "▰▰▰▰▰▱▱▱▱▱"
    elif 50 <= umm < 60:
        bar = "▰▰▰▰▰▰▱▱▱▱"
    elif 60 <= umm < 70:
        bar = "▰▰▰▰▰▰▰▱▱▱"
    elif 70 <= umm < 80:
        bar = "▰▰▰▰▰▰▰▰▱▱"
    elif 80 <= umm < 95:
        bar = "▰▰▰▰▰▰▰▰▰▱"
    else:
        bar = "▰▰▰▰▰▰▰▰▰▰"

    return [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="♩", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="♫", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="✗", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="♬",
                callback_data=f"ADMIN Queue|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⌂",
                url="https://t.me/candy_xbot",
            ),
        ],
        [
            InlineKeyboardButton(
                text="×",
                callback_data=f"forceclose {chat_id}",
            )
        ],
    ]


# =========================
# STREAM MARKUP
# =========================
def stream_markup(_, videoid, chat_id):
    return [
        [
            InlineKeyboardButton(text="♩", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="♫", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="✗", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text="♬",
                callback_data=f"ADMIN Queue|{chat_id}",
            ),
            InlineKeyboardButton(
                text="⌂",
                url="https://t.me/candy_xbot",
            ),
        ],
        [
            InlineKeyboardButton(
                text="×",
                callback_data=f"forceclose {chat_id}",
            )
        ],
    ]


# =========================
# PLAYLIST MARKUP
# =========================
def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text="♬",
                callback_data=f"Playlists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text="♬",
                callback_data=f"Playlists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="×",
                callback_data=f"forceclose {user_id}",
            ),
        ],
    ]


# =========================
# LIVESTREAM MARKUP
# =========================
def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text="♬",
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="×",
                callback_data=f"forceclose {user_id}",
            ),
        ],
    ]


# =========================
# SLIDER MARKUP
# =========================
def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    return [
        [
            InlineKeyboardButton(
                text="♬",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text="♬",
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text="×",
                callback_data=f"forceclose {user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]