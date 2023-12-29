# Standard
from uuid import uuid4

# Project
import config as cf


def write_notification(to: int, variable_name: str, value: str):
    with open(cf.BASE + '/database/notifications.txt', 'a', encoding='utf-16') as f:
        f.write(f'{str(uuid4())[:10]} {to} {variable_name} {value}\n')


# Function to track changes to facility_id
def track_facility_id_change(model, value, prev_value, mapper):
    if prev_value != value:
        write_notification(to=model.id, variable_name='facility_id', value=value)


def track_admin_change(model, value, prev_value, mapper):
    if prev_value != value:
        write_notification(to=model.id, variable_name='is_admin', value=value)


def track_post_change(model, value, prev_value, mapper):
    if prev_value != value:
        write_notification(to=model.id, variable_name='post', value=value.replace(' ', '__'))