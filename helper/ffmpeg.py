import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import Message


async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb != None:
            parser = createParser(thumb)
            metadata = extractMetadata(parser)
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
                
            # Open the image file
            with Image.open(thumb) as img:
                # Convert the image to RGB format and save it back to the same file
                img.convert("RGB").save(thumb)
            
                # Resize the image
                resized_img = img.resize((width, height))
                
                # Save the resized image in JPEG format
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
            '-metadata', f'title={metadata}',  # Set Title Metadata
            '-metadata', f'author={metadata}',  # Set Author Metadata
            '-metadata:s:s', f'title={metadata}',  # Set Subtitle Metadata
            '-metadata:s:a', f'title={metadata}',  # Set Audio Metadata
            '-metadata:s:v', f'title={metadata}',  # Set Video Metadata
            '-metadata', f'artist={metadata}',  # Set Artist Metadata
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        print(e_response)
        print(t_response)

        
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


#gpt


video_path = await add_watermark_to_video(video_path, m.from_user.id)



import os
import asyncio

async def add_watermark_to_video(video_path, user_id):
    watermark_path = f"watermarks/{user_id}.png"
    
    if not os.path.exists(watermark_path):
        return video_path  # No watermark, return original
    
    output_path = f"{video_path}_watermarked.mp4"
    
    cmd = f"""
    ffmpeg -i "{video_path}" -i "{watermark_path}" -filter_complex "[0:v][1:v] overlay=W-w-10:H-h-10" \
    -c:a copy -y "{output_path}"
    """
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()

    if os.path.exists(output_path):
        return output_path
    else:
        return video_path



from helper.database import get_watermark_position

async def add_watermark_to_video(video_path, user_id):
    watermark_path = f"watermarks/{user_id}.png"
    
    if not os.path.exists(watermark_path):
        return video_path
    
    output_path = f"{video_path}_watermarked.mp4"
    position = await get_watermark_position(user_id)
    
    positions = {
        "top-left": "10:10",
        "top-right": "W-w-10:10",
        "bottom-left": "10:H-h-10",
        "bottom-right": "W-w-10:H-h-10",
        "center": "(W-w)/2:(H-h)/2"
    }
    pos_str = positions.get(position, "W-w-10:H-h-10")
    
    cmd = f"""
    ffmpeg -i "{video_path}" -i "{watermark_path}" -filter_complex "[0:v][1:v] overlay={pos_str}" \
    -c:a copy -y "{output_path}"
    """
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()

    if os.path.exists(output_path):
        return output_path
    else:
        return video_path




# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @JishuBotz & @Madflix_Bots
# Developer @JishuDeveloper
