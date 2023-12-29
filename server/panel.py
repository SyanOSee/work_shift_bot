# Third-party
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.security import HTTPBasic
from fastapi.responses import RedirectResponse, Response, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqladmin import Admin

# Standard
from base64 import b64decode
from typing import Tuple
import os
from logger import server_logger
from glob import glob
import zipfile

# Project
import config as cf
from database import db
from .models import UserView, ShiftView, FacilityView, QuestionView, ReportView, LogView

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=cf.panel_server['secret_key'])

security = HTTPBasic()


def verify_credentials(username: str, password: str) -> bool:
    correct_username = cf.database['user']
    correct_password = cf.database['password']
    return username == correct_username and password == correct_password


def extract_basic_auth(credentials: str) -> Tuple[str, str]:
    decoded = b64decode(credentials).decode("utf-8")
    username, _, password = decoded.partition(":")
    return username, password


async def admin_auth_middleware(request: Request, call_next):
    if request.url.path.startswith('/admin'):
        # Extract Basic Auth credentials
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            return Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={"WWW-Authenticate": "Basic"})
        try:
            scheme, _, param = authorization.partition(" ")
            if scheme.lower() == 'basic':
                username, password = extract_basic_auth(param)
                if not verify_credentials(username, password):
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except (ValueError, HTTPException):
            return Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={"WWW-Authenticate": "Basic"})
    response = await call_next(request)
    return response


# Add the middleware to the application
app.add_middleware(BaseHTTPMiddleware, dispatch=admin_auth_middleware)

admin = Admin(app=app, engine=db.engine)
[admin.add_view(view) for view in [
    UserView, ShiftView, FacilityView,
    QuestionView, ReportView, LogView
]]


@app.get('/')
async def home(request: Request):
    return RedirectResponse('/admin')


@app.get('/admin')
async def admin_page(request: Request):
    return await admin.index(request)


async def zip_reports(report_type: str) -> str:
    directory_path = os.path.join(cf.BASE, f"media/reports/{report_type}/*.xlsx")
    csv_files = glob(directory_path)
    zip_file_path = os.path.join(cf.BASE, f"media/reports/{report_type}_reports.zip")

    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for csv_file in csv_files:
            zipf.write(csv_file, os.path.basename(csv_file))

    return zip_file_path


@app.get("/get/{filepath:path}")
async def file_handler(filepath: str):
    file_path = os.path.join(cf.BASE, filepath)

    if os.path.isfile(file_path):
        return FileResponse(file_path)

    server_logger.error(f'File {file_path} not found!')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File {file_path} not found!")


@app.get("/reports/weekly")
async def weekly_reports_handler():
    zip_file_path = await zip_reports('weekly')
    return FileResponse(zip_file_path)


@app.get("/reports/monthly")
async def monthly_reports_handler():
    zip_file_path = await zip_reports('monthly')
    return FileResponse(zip_file_path)


@app.get("/reports/users")
async def monthly_reports_handler():
    zip_file_path = await zip_reports('users')
    return FileResponse(zip_file_path)


@app.on_event("startup")
async def start_server():
    server_logger.info(f'Server started at http://{cf.panel_server["host"]}:{cf.panel_server["port"]}')


async def start_panel():
    from uvicorn import Config, Server

    config = Config(
        app=app, host='0.0.0.0',
        port=int(cf.panel_server['port']))

    server = Server(config=config)

    await server.serve()
