import time
import os
import asyncio
from PIL import Image, ImageEnhance
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb and os.path.exists(thumb):
            parser = createParser(thumb)
            metadata = extractMetadata(parser)
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")

            # Enhance image using PIL
            with Image.open(thumb) as img:
                img = img.convert("RGB")
                
                # Optional: Resize back to original resolution
                resized_img = img.resize((width, height))

                # Enhance brightness/contrast (optional tweak)
                enhancer = ImageEnhance.Sharpness(resized_img)
                enhanced_img = enhancer.enhance(1.3)

                enhanced_img.save(thumb, "JPEG", quality=95)

            parser.close()
    except Exception as e:
        print("fix_thumb error:", e)
        thumb = None

    return width, height, thumb


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{int(time.time())}_thumb.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss", str(ttl),                 # Capture frame at given time
        "-i", video_file,               # Input file
        "-vframes", "1",                # One frame only
        "-q:v", "1",                    # Best quality (1 is best, 31 is worst)
        "-vf", "scale=1280:-1",         # Width 1280px, height auto (maintain aspect ratio)
        "-y",                           # Overwrite output
        out_put_file_name
    ]

    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if os.path.exists(out_put_file_name):
        return out_put_file_name
    return None