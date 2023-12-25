# Project
from logger import bot_logger


async def format_timedelta_to_hours_minutes(timedelta_obj):
    # Extract total seconds from the timedelta object
    total_seconds = int(timedelta_obj.total_seconds())
    # Calculate hours and minutes
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Format the string to "HH:MM" format
    time_str = f"{hours:02d}:{minutes:02d}"
    return time_str


async def convert_time_to_float(time_str):
    # Split the time string into hours and minutes
    hours_str, minutes_str = time_str.split(':')

    # Convert hours and minutes to integers
    hours = int(hours_str)
    minutes = int(minutes_str)

    # Convert minutes to a fraction of an hour
    fractional_hours = minutes / 60

    # Combine whole hours with fractional hours
    time_in_hours = hours + fractional_hours

    return time_in_hours


async def download_image(image_url: str, destination: str) -> bool:
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                # Read the content of the response asynchronously
                content = await response.read()
                # Write the content to a file asynchronously
                with open(destination, "wb") as file:
                    file.write(content)
                bot_logger.warning(f"Image downloaded successfully to {destination}")
                return True
            else:
                bot_logger.error(f"Failed to download image. Status code: {response.status}")
                return False
