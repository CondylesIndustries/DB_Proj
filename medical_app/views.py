from django.shortcuts import render
import psycopg2 as postgres
from django.db import connection, ProgrammingError

# Create your views here.

def home_view(request):
    return render(request, 'medical_app/home.html')

def custom_query_view(request):
    query = ''
    rows = []
    columns = []
    error = None

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

        if query != '':
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    if cursor.description != '':
                        columns = [col.name for col in cursor.description]
                        rows = cursor.fetchall()
            except ProgrammingError as e:
                error = str(e)

    return render(request, 'medical_app/custom_query.html', {
        'query': query,
        'columns': columns,
        'rows': rows,
        'error': error
    })