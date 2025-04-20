import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb:
            parser = createParser(thumb)
            metadata = extractMetadata(parser)
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
                
            with Image.open(thumb) as img:
                img.convert("RGB").save(thumb)
                resized_img = img.resize((width, height))
                resized_img.save(thumb, "JPEG")
                
            parser.close()
    except Exception as e:
        print(e)
        thumb = None 
       
    return width, height, thumb


async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    return None


async def add_metadata(input_path, output_path, metadata, ms):
    try:
        await ms.edit("<i>I Found Metadata, Adding Into Your File ⚡</i>")
        command = [
            'ffmpeg', '-y', '-i', input_path, '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
            '-metadata', f'title={metadata}',
            '-metadata', f'author={metadata}',
            '-metadata:s:s', f'title={metadata}',
            '-metadata:s:a', f'title={metadata}',
            '-metadata:s:v', f'title={metadata}',
            '-metadata', f'artist={metadata}',
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        print(stderr.decode().strip())
        print(stdout.decode().strip())

        if os.path.exists(output_path):
            await ms.edit("<i>Metadata Has Been Successfully Added To Your File ✅</i>")
            return output_path
        else:
            await ms.edit("<i>Failed To Add Metadata To Your File ❌</i>")
            return None
    except Exception as e:
        print(f"Error occurred while adding metadata: {str(e)}")
        await ms.edit("<i>An Error Occurred While Adding Metadata To Your File ❌</i>")
        return None





# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @JishuBotz & @Madflix_Bots
# Developer @JishuDeveloper