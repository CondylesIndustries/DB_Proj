from django.shortcuts import render
import psycopg2 as postgres
from django.db import connection, ProgrammingError
import medical_app.raw_sql_queries as rsq
import hashlib
from django.http import HttpResponseRedirect

from .forms import patientRegister
from .forms import doctorRegister
from .forms import insuranceRegister

from .queryhelper import selectOne
from .queryhelper import selectAll
from .queryhelper import execute

# Create your views here.

user_types = ['patient', 'doctor', 'insurancecompany', 'medicalfacility']

headings = {
    'patient': 'Patient Login',
    'doctor': 'Doctor Login',
    'insurancecompany': 'Insurance Portal Login',
    'medicalfacility': 'Medical Facility Login',
}

def home_view(request):
    html_info = {
        'patient': request.session.get('patient', -1),
        'doctor': request.session.get('doctor', -1),
        'insurancecompany': request.session.get('insurancecompany', -1),
    }
    if html_info['patient'] != -1:
        html_info['welcome'] = selectOne('SELECT first_name FROM patient WHERE patient_id=%s', [html_info['patient']])[0]
    elif html_info['doctor'] != -1:
        html_info['welcome'] = selectOne('SELECT last_name FROM doctor WHERE doctor_id=%s', [html_info['doctor']])[0]
    elif html_info['insurancecompany'] != -1:
        html_info['welcome'] = selectOne('SELECT company_name FROM insurancecompany WHERE insurance_id=%s', [html_info['insurancecompany']])[0]
        
    return render(request, 'medical_app/home.html', html_info)


def findUser(username, password_hash, portal_type):
    if portal_type == 'insurancecompany':
        one_row = selectOne('select insurance_id from insurancecompany where company_name = %s and password_hash = %s', [username, password_hash])
    elif portal_type == 'patient':
        one_row = selectOne(f'select patient_id from patient where email = %s and password_hash = %s', [username, password_hash])
    elif portal_type == 'doctor':
        one_row = selectOne(f'select doctor_id from doctor where email = %s and password_hash = %s', [username, password_hash])
    return one_row
    

def registerUser(
        portal_type,
        username,
        password_hash,
        first_name=None,
        last_name=None,
        date_of_birth=None,
        phone_number=None,
        insurance_name=None,
        address=None,
        affiliate_office_name=None,
        specialty=None,
        ):
    if portal_type == 'patient':
        insurance_id = selectOne('SELECT insurance_id FROM insurancecompany WHERE company_name = %s', [insurance_name])[0]
        execute("""
                INSERT INTO patient(first_name, last_name, date_of_birth, phone_number, email, insurance_id, password_hash) VALUES
                (%s, %s, %s, %s, %s, %s, %s)
                """,
                [first_name, last_name, date_of_birth, phone_number, username, int(insurance_id), password_hash]
            )
    elif portal_type == 'doctor':
        facility_id = selectOne('SELECT facility_id FROM medicalfacility WHERE facility_name = %s', [affiliate_office_name])[0]
        execute("""
                INSERT INTO doctor(affiliate_office_id, first_name, last_name, specialty, email, password_hash) VALUES
                (%s, %s, %s, %s, %s, %s)
                """,
                [int(facility_id), first_name, last_name, specialty, username, password_hash]
            )
    elif portal_type == 'insurancecompany':
        execute("""
                INSERT INTO insurancecompany(company_name, address, phone_number, password_hash) VALUES
                (%s, %s, %s, %s)
                """,
                [username, address, phone_number, password_hash]
            )


def login_view(request, portal_type):
    if portal_type not in user_types:
        return render(request, '404.html', status=404)

    with connection.cursor() as cursor:
        cursor.execute(rsq.insurance_name_query)
        insurance_names = [row[0] for row in cursor.fetchall()]

        cursor.execute(rsq.medicalfacility_name_query)
        facility_names = [row[0] for row in cursor.fetchall()]

        context = {
            'portal_type': portal_type,
            'heading': headings[portal_type],
            'name_options': insurance_names if portal_type == 'insurancecompany' else facility_names if portal_type == 'medicalfacility' else None,
            'password_mismatch': False,
        }

    if request.method == "GET":
        return render(request, 'medical_app/login.html', context)

    else:
        if portal_type == 'insurancecompany' or portal_type == 'medicalfacility':
            username = request.POST.get('org_name', '')
        else:
            username = request.POST.get('email_address', '')
        password = request.POST.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user_id = findUser(username, password_hash, portal_type)
        if user_id:
            request.session[portal_type] = user_id[0]
            return HttpResponseRedirect('/')
        else :
            context['password_mismatch'] = True
            return render(request, "medical_app/login.html", context)


def register_view(request):
    patient_form = None
    doctor_form = None
    insurance_form = None

    if request.method == 'POST':
        if 'submit_patient' in request.POST:
            patient_form = patientRegister(request.POST)
            if patient_form.is_valid():
                registerUser(
                    portal_type='patient',
                    username=patient_form.cleaned_data['email'],
                    password_hash=hashlib.sha256(patient_form.cleaned_data['password1'].encode()).hexdigest(),
                    first_name=patient_form.cleaned_data['first_name'],
                    last_name=patient_form.cleaned_data['last_name'],
                    date_of_birth=patient_form.cleaned_data['date_of_birth'],
                    phone_number=patient_form.cleaned_data['phone_number'],
                    insurance_name=patient_form.cleaned_data['insurance_name'],
                )
                request.session['patient'] = selectOne('SELECT patient_id FROM patient WHERE email=%s', [patient_form.cleaned_data['email']])[0]
                return HttpResponseRedirect("/")
        elif 'submit_doctor' in request.POST:
            doctor_form = doctorRegister(request.POST)
            if doctor_form.is_valid():
                registerUser(
                    portal_type='doctor',
                    username=doctor_form.cleaned_data['email'],
                    password_hash=hashlib.sha256(doctor_form.cleaned_data['password1'].encode()).hexdigest(),
                    first_name=doctor_form.cleaned_data['first_name'],
                    last_name=doctor_form.cleaned_data['last_name'],
                    specialty=doctor_form.cleaned_data['specialty'],
                    affiliate_office_name=doctor_form.cleaned_data['affiliate_office_name'],
                )
                request.session['doctor'] = selectOne('SELECT doctor_id FROM doctor WHERE email=%s', [doctor_form.cleaned_data['email']])[0]
                return HttpResponseRedirect("/")
        elif 'submit_insurance' in request.POST:
            insurance_form = insuranceRegister(request.POST)
            if insurance_form.is_valid():
                registerUser(
                    portal_type='insurancecompany',
                    username=insurance_form.cleaned_data['company_name'],
                    password_hash=hashlib.sha256(insurance_form.cleaned_data['password1'].encode()).hexdigest(),
                    address = insurance_form.cleaned_data['street'] + ', '
                        + insurance_form.cleaned_data['city'] + ' '
                        + insurance_form.cleaned_data['state'] + ', '
                        + insurance_form.cleaned_data['zip_code'],
                    phone_number=insurance_form.cleaned_data['phone_number'],
                )
                request.session['insurancecompany'] = selectOne('SELECT insurance_id FROM insurancecompany WHERE company_name=%s', [insurance_form.cleaned_data['company_name']])[0]
                return HttpResponseRedirect("/")

    else:
        patient_form = patientRegister()
        doctor_form = doctorRegister()
        insurance_form = insuranceRegister()
        html_info = {
            "patient_form": patient_form,
            "doctor_form": doctor_form,
            "insurance_form": insurance_form,
        }

        return render(request, "medical_app/register.html", html_info)


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

def signout(request):
    request.session['patient'] = -1
    request.session['doctor'] = -1
    request.session['insurancecompany'] = -1
    return HttpResponseRedirect("/")