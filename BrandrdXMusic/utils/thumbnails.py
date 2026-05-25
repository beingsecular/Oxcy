import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from unidecode import unidecode
from py_yt import VideosSearch

from BrandrdXMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clean_title(text, limit=45):
    text = re.sub(r"\W+", " ", text)
    text = text.strip()
    if len(text) > limit:
        text = text[:limit] + "..."
    return text


async def get_thumb(videoid):
    os.makedirs("cache", exist_ok=True)
    final_path = f"cache/{videoid}.png"
    temp_path = f"cache/thumb{videoid}.png"

    if os.path.isfile(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub(r"\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(temp_path).convert("RGB")

        # Neon border color random
        neon_colors = ["#00FFFF", "#FF00FF", "#FF1493", "#00FF00", "#FFD700", "#FF4500"]
        GLOW_COLOR = "#ff0099"
        BORDER_COLOR = random.choice(neon_colors)

        image1 = changeImageSize(1280, 720, youtube)
        image1 = image1.filter(ImageFilter.GaussianBlur(20))
        image1 = ImageEnhance.Brightness(image1).enhance(0.4)
        image1 = image1.convert("RGBA")

        thumb_width = 840
        thumb_height = 460

        youtube_thumb = youtube.resize((thumb_width, thumb_height)).convert("RGBA")

        mask = Image.new("L", (thumb_width, thumb_height), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle(
            [(0, 0), (thumb_width, thumb_height)], radius=20, fill=255
        )
        youtube_thumb.putalpha(mask)

        center_x = 640
        center_y_img = 300
        thumb_x = center_x - (thumb_width // 2)
        thumb_y = center_y_img - (thumb_height // 2)
        thumb_x2 = thumb_x + thumb_width
        thumb_y2 = thumb_y + thumb_height

        # Glow layer
        glow_layer = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        draw_glow = ImageDraw.Draw(glow_layer)
        glow_expand = 20
        draw_glow.rounded_rectangle(
            [
                (thumb_x - glow_expand, thumb_y - glow_expand),
                (thumb_x2 + glow_expand, thumb_y2 + glow_expand),
            ],
            radius=30,
            fill=GLOW_COLOR,
        )
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(30))
        image1.paste(glow_layer, (0, 0), glow_layer)

        # Border layer
        border_layer = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        draw_border = ImageDraw.Draw(border_layer)
        border_expand = 5
        draw_border.rounded_rectangle(
            [
                (thumb_x - border_expand, thumb_y - border_expand),
                (thumb_x2 + border_expand, thumb_y2 + border_expand),
            ],
            radius=25,
            fill=BORDER_COLOR,
        )
        image1.paste(border_layer, (0, 0), border_layer)

        # Paste thumbnail
        image1.paste(youtube_thumb, (thumb_x, thumb_y), youtube_thumb)

        draw = ImageDraw.Draw(image1)

        try:
            font_title = ImageFont.truetype("BrandrdXMusic/assets/font.ttf", 45)
            font_details = ImageFont.truetype("BrandrdXMusic/assets/font2.ttf", 30)
            font_watermark = ImageFont.truetype("BrandrdXMusic/assets/font2.ttf", 25)
        except:
            font_title = ImageFont.load_default()
            font_details = ImageFont.load_default()
            font_watermark = ImageFont.load_default()

        def get_text_width(text, font):
            if hasattr(draw, "textlength"):
                return draw.textlength(text, font=font)
            else:
                return draw.textsize(text, font=font)[0]

        title = clean_title(title)

        w_title = get_text_width(title, font_title)
        text_y_pos = thumb_y2 + 30

        draw.text(
            ((1280 - w_title) / 2, text_y_pos),
            text=title,
            fill="white",
            font=font_title,
            stroke_width=1,
            stroke_fill="black",
        )

        stats_text = f"{channel}  •  {views}  •  {duration}"
        w_stats = get_text_width(stats_text, font_details)
        draw.text(
            ((1280 - w_stats) / 2, text_y_pos + 60),
            text=stats_text,
            fill=BORDER_COLOR,
            font=font_details,
            stroke_width=1,
            stroke_fill="black",
        )

        # Bot name top-right
        try:
            bot_name = unidecode(app.name)
        except:
            bot_name = "Music Bot"

        w_bot = get_text_width(bot_name, font_watermark)
        draw.text(
            (1280 - w_bot - 30, 30),
            text=bot_name,
            fill="yellow",
            font=font_watermark,
            stroke_width=1,
            stroke_fill="black",
        )

        try:
            os.remove(temp_path)
        except:
            pass

        image1 = image1.convert("RGB")
        image1.save(final_path)
        return final_path

    except Exception as e:
        print("[THUMB ERROR]", e)
        return YOUTUBE_IMG_URL


async def get_qthumb(vidid):
    try:
        url = f"https://www.youtube.com/watch?v={vidid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL