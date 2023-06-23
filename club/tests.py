from django.test import TestCase
from club.models import (
    StoreGroup,
    Store
)
from django.db import connection

try:
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, unicode, transport_num, profile, plan, time, "Выход" as inout FROM base_checkout
        WHERE transport_num="'''+transport.number+'''"''')

    # SOLUTION:https://docs.djangoproject.com/en/4.1/topics/db/sql/ 
    # By default, the Python DB API will return results without their field names, 
    # which means you end up with a list of values, rather than a dict. At a small 
    # performance and memory cost, you can return results as a dict by using something like this:
    columns = [col[0] for col in cursor.description]
    result = [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
except Exception as ex:
    pass