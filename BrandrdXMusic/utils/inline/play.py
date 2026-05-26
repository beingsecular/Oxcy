
import os
import random
import string
import asyncio
from random import randint
from typing import Union
from time import time

from pyrogram import client, filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS, lyrical

from BrandrdXMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app, Carbon
from BrandrdXMusic.misc import SUDOERS, db
from BrandrdXMusic.utils import seconds_to_min, time_to_seconds
from BrandrdXMusic.utils.channelplay import get_channeplayCB
from BrandrdXMusic.utils.decorators.language import languageCB
from BrandrdXMusic.utils.decorators.play import PlayWrapper
from BrandrdXMusic.utils.formatters import formats
from BrandrdXMusic.utils.logger import play_logs
from BrandrdXMusic.utils.extraction import extract_user
from BrandrdXMusic.utils.thumbnails import get_thumb
from BrandrdXMusic.utils.exceptions import AssistantErr

from BrandrdXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
    add_active_video_chat,
    is_active_chat,
)

from BrandrdXMusic.utils.inline import aq_markup, close_markup, stream_markup
from BrandrdXMusic.utils.stream.queue import put_queue, put_queue_index
from BrandrdXMusic.utils.pastebin import HottyBin
from youtubesearchpython.future import VideosSearch

# ================= ROTATING VIDEOS ================= #

STREAM_VIDEOS = [
    "https://files.catbox.moe/3h02m3.mp4",
    "https://files.catbox.moe/jo9v5z.mp4",
    "https://files.catbox.moe/1feop0.mp4",
    "https://files.catbox.moe/qr1zhj.mp4",
]

_video_index = {}


def get_next_video(chat_id):
    idx = _video_index.get(chat_id, 0)
    video = STREAM_VIDEOS[idx % len(STREAM_VIDEOS)]
    _video_index[chat_id] = idx + 1
    return video


async def send_stream_message(original_chat_id, chat_id, caption, button, vidid=None):
    stream_video = get_next_video(chat_id)

    try:
        return await app.send_video(
            original_chat_id,
            video=stream_video,
            width=320,
            height=180,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(button),
        )
    except Exception as e:
        print(f"[VIDEO SEND ERROR] {e}")

        try:
            img = await get_thumb(vidid) if vidid else config.YOUTUBE_IMG_URL
            return await app.send_photo(
                original_chat_id,
                photo=img,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(button),
            )
        except Exception as e2:
            print(f"[PHOTO SEND ERROR] {e2}")
            return None


# ================= MAIN STREAM FUNCTION ================= #

async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    from BrandrdXMusic.core.call import Hotty  # Fixed: lazy import to avoid circular import

    if not result:
        return

    if forceplay:
        await Hotty.force_stop_stream(chat_id)

    # ================= PLAYLIST ================= #

    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0

        for search in result:

            if count == config.PLAYLIST_FETCH_LIMIT:
                continue

            try:
                title, duration_min, duration_sec, thumbnail, vidid = await YouTube.details(
                    search,
                    False if spotify else True
                )
            except:
                continue

            if str(duration_min) == "None":
                continue

            if duration_sec > config.DURATION_LIMIT:
                continue

            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )

                position = len(db.get(chat_id)) - 1
                count += 1

                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"

            else:
                if not forceplay:
                    db[chat_id] = []

                status = True if video else None

                try:
                    file_path, direct = await YouTube.download(
                        vidid,
                        mystic,
                        video=status,
                        videoid=True,
                    )
                except:
                    await mystic.edit_text(_["play_3"])
                    return

                await Hotty.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )

                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                    forceplay=forceplay,
                )

                button = stream_markup(_, vidid, chat_id)
                caption = _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:18],
                    duration_min,
                    user_name,
                )

                run = await send_stream_message(
                    original_chat_id,
                    chat_id,
                    caption,
                    button,
                    vidid,
                )

                if run:
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"

        return

    # ================= YOUTUBE ================= #
    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = result["title"].title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]

        status = True if video else None

        try:
            file_path, direct = await YouTube.download(
                vidid,
                mystic,
                videoid=True,
                video=status,
            )
        except:
            await mystic.edit_text(_["play_3"])
            return

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )

        else:
            if not forceplay:
                db[chat_id] = []

            await Hotty.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail,
            )

            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

    # ================= TELEGRAM ================= #
    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = result["title"].title()
        duration_min = result["dur"]

        status = True if video else None

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
            )

        else:
            if not forceplay:
                db[chat_id] = []

            await Hotty.join_call(chat_id, original_chat_id, file_path, video=status)

    # ================= INDEX ================= #
    elif streamtype == "index":
        link = result
        title = "ɪɴᴅᴇx ᴏʀ ᴍ3ᴜ8 ʟɪɴᴋ"
        duration_min = "00:00"

        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
            )

        else:
            if not forceplay:
                db[chat_id] = []

            await Hotty.join_call(
                chat_id,
                original_chat_id,
                link,
                video=True if video else None,
            )