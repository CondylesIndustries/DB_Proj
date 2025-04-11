from django.db import connection

# Helper Queries
def selectOne(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.fetchone()

def selectAll(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.fetchall()

def execute(query, params):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])