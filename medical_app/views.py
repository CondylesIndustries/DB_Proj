from django.shortcuts import render
import psycopg2 as postgres
from django.db import connection, ProgrammingError
import medical_app.raw_sql_queries as rsq
import hashlib

# Create your views here.

user_types = ['patient', 'doctor', 'insurancecompany', 'medicalfacility']

headings = {
    'patient': 'Patient Login',
    'doctor': 'Doctor Login',
    'insurancecompany': 'Insurance Portal Login',
    'medicalfacility': 'Medical Facility Login',
}

def home_view(request):
    return render(request, 'medical_app/home.html')


def findUser(username, password_hash, portal_type):
    with connection.cursor() as cursor:
        query = f'select * from {portal_type} where username = {username} and password_hash = {password_hash}'
        cursor.execute(query)
        one_row = cursor.fetchone()
        return one_row[0]


def login_view(request, portal_type):
    if portal_type not in user_types:
        return render(request, '404.html', status=404)

    if request.method == "GET":

        with connection.cursor() as cursor:
            cursor.execute(rsq.insurance_name_query)
            insurance_names = [row[0] for row in cursor.fetchall()]

            cursor.execute(rsq.medicalfacility_name_query)
            facility_names = [row[0] for row in cursor.fetchall()]

        context = {
            'portal_type': portal_type,
            'heading': headings[portal_type],
            'name_options': insurance_names if portal_type == 'insurancecompany' else facility_names if portal_type == 'medicalfacility' else None
        }
        return render(request, 'medical_app/login.html', context)

    else:
        if portal_type == 'insurancecompany' or portal_type == 'medicalfacility':
            username = request.POST.get('org_name', '')
        else:
            username = request.POST.get('email_address', '')
        password = request.POST.get('password', '')
        password_hash = hashlib.sha256(password)
        user_id = findUser(username, password_hash, portal_type)







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
                    print(cursor.description)
                    if cursor.description != '' and cursor.description is not None:
                        columns = [col.name for col in cursor.description]
                        rows = cursor.fetchall()
                    error = "Successful query"
            except ProgrammingError as e:
                error = str(e)

    return render(request, 'medical_app/custom_query.html', {
        'query': query,
        'columns': columns,
        'rows': rows,
        'error': error
    })