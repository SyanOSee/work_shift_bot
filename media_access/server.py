# Third-party
from aiohttp import web

# Project
from logger import media_logger
import os
import config as cf
import zipfile
from glob import glob


async def file_handler(request):
    # Extract filename from the request match_info
    file_path = cf.BASE + '/' + request.match_info.get('filepath', "")

    if os.path.isfile(file_path):
        # Return the file response
        return web.FileResponse(file_path)
    else:
        # Return a 404 Not Found response if the file doesn't exist
        media_logger.error(f'File {file_path} not found!')


async def zip_reports(user_id: int, report_type: str) -> str:
    directory_path = os.path.join(cf.BASE, f'media/reports/{report_type}/*.xlsx')
    csv_files = glob(directory_path)
    zip_file_path = os.path.join(cf.BASE, f'media/reports/{report_type}_reports.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for csv_file in csv_files:
            zipf.write(csv_file, os.path.basename(csv_file))
    return zip_file_path


async def weekly_reports_handler(request):
    user_id = int(request.match_info.get('user_id'))
    zip_file_path = await zip_reports(user_id, 'weekly')
    return web.FileResponse(zip_file_path)


async def monthly_reports_handler(request):
    user_id = int(request.match_info.get('user_id'))
    zip_file_path = await zip_reports(user_id, 'monthly')
    return web.FileResponse(zip_file_path)


async def start_server():
    app = web.Application()
    # Configure your aiohttp app here

    # Set up a dynamic route to serve files from the media/file/ directory
    app.router.add_route('GET', '/get/{filepath:.*}', file_handler)
    app.router.add_route('GET', '/reports/weekly/{user_id}', weekly_reports_handler)
    app.router.add_route('GET', '/reports/monthly/{user_id}', monthly_reports_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, cf.media_server['host'], cf.media_server['port'])
    await site.start()
    media_logger.info(f'Server started at http://{cf.media_server["host"]}:{cf.media_server["port"]}')
