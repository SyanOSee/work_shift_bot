# Third-party
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBasic
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

# Standard
import os
import io
import zipfile

# Project
from logger import server_logger
import config as cf
from database import db
from handlers.background import reports
from .models import UserView, ShiftView, FacilityView, QuestionView, ReportView, LogView

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=cf.panel_server['secret_key'])
security = HTTPBasic()

admin = Admin(app=app, engine=db.engine)
[admin.add_view(view) for view in [
    UserView,
    ShiftView,
    FacilityView,
    QuestionView,
    ReportView,
    LogView
]]


@app.get('/')
async def home(request: Request):
    return RedirectResponse('/admin')


@app.get('/admin')
async def admin_page(request: Request):
    return await admin.index(request)


def get_report_path(report_name: str) -> str:
    return os.path.join('media/reports', report_name)


def get_facility_user_report_path(facility_id: str) -> str:
    return os.path.join(cf.BASE, 'media\\reports\\facilities', facility_id, 'users_report.xlsx')


def get_report_directory(report_name: str) -> str:
    return os.path.join(cf.BASE, 'media/reports', report_name)


def create_zip(directory_path: str) -> bytes:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, directory_path))
    zip_buffer.seek(0)
    return zip_buffer.read()


@app.get("/reports/weekly")
async def weekly_reports_handler():
    report_directory = get_report_directory('weekly')
    zip_data = create_zip(report_directory)
    return StreamingResponse(io.BytesIO(zip_data), media_type="application/zip",
                             headers={"Content-Disposition": "attachment; filename=weekly_reports.zip"})


@app.get("/reports/monthly")
async def monthly_reports_handler():
    report_directory = get_report_directory('monthly')
    zip_data = create_zip(report_directory)
    return StreamingResponse(io.BytesIO(zip_data), media_type="application/zip",
                             headers={"Content-Disposition": "attachment; filename=monthly_reports.zip"})


@app.get("/reports/users")
async def users_reports_handler():
    await reports.generate_users_report()
    report_path = get_report_path('users_report.xlsx')
    return FileResponse(report_path)


@app.get("/reports/facilities/{facility_id}/users")
async def facility_user_report_handler(facility_id: str):
    await reports.generate_facility_users_report(facility_id=facility_id)
    report_path = get_facility_user_report_path(facility_id)
    return FileResponse(report_path)


@app.get("/get/{filepath:path}")
async def file_handler(filepath: str):
    file_path = os.path.join(cf.BASE, filepath)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    server_logger.error(f'File {file_path} not found!')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File {file_path} not found!")


@app.on_event("startup")
async def start_server():
    server_logger.info(f'Server started at http://{cf.panel_server["host"]}:{cf.panel_server["port"]}')


async def start_panel():
    from uvicorn import Config, Server
    config = Config(
        app=app,
        host='0.0.0.0',
        port=int(cf.panel_server['port'])
    )
    server = Server(config=config)
    await server.serve()
