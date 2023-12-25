FROM python:3.10
COPY . /usr/src/app/work_shift_bot/
WORKDIR /usr/src/app/work_shift_bot/
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /usr/src/app/work_shift_bot/requirements.txt
CMD ["python", "start.py"]
