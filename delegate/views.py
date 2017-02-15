from io import BytesIO
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .forms import *
from .constants import *
from crm.models import Person, Changes
from crm.views import add_change_record
from infonex_crm.settings import BASE_DIR
from registration.models import *
from registration.forms import ConferenceSelectForm


#############################
# HELPER FUNCTIONS
#############################
def process_complete_registration(request, assistant_data, company, crm_match,
                                  current_registration, reg_details_data,
                                  registrant, conference, option_list):
    """
    Helper function, called from process_registration once request data
    has been verified
    """
    # 1. create database records if not present
    # a. assistant
    if request.POST['assistant_match_value']:
        assistant = Assistant.objects.get(
            pk=request.POST['assistant_match_value']
        )
        assistant_form = AssistantForm(assistant_data, instance=assistant)
        assistant_form.save()
    else:
        # Check to make sure record not already in the database
        assistant_db_check = Assistant.objects.filter(
            first_name=assistant_data['first_name'],
            last_name=assistant_data['last_name'],
            email=assistant_data['email'],
        )
        if assistant_db_check.count() > 0:
            assistant=assistant_db_check[0]
            assistant_form = AssistantForm(assistant_data, instance=assistant)
            assistant_form.save()
        else:
            assistant = AssistantForm(assistant_data).save()

    # b. company - passed as param

    # c. crm record
    # TODO: decide how to check for existing CRM - done on front end??
    if not crm_match:
        crm_match = Person(
            name=request.POST['first_name'] + ' ' + request.POST['last_name'],
            title=request.POST['title'],
            company=company.name,
            phone=request.POST['phone1'],
            email=request.POST['email1'],
            city=company.city,
            date_created=timezone.now(),
            created_by=request.user,
            date_modified=timezone.now(),
            modified_by=request.user,
        )
        crm_match.save()
        add_change_record(crm_match, 'reg_add')

    # d. registrant
    if registrant:
        delegate_form = NewDelegateForm(request.POST, instance=registrant)
        delegate_form.save()
        registrant.modified_by = request.user
        registrant.date_modified = timezone.now()
        registrant.save()
    else:
        registrant_db_check = Registrants.objects.filter(
            company=company,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email1=request.POST['email1']
        )
        if registrant_db_check.count() > 0:
            registrant = registrant_db_check[0]
            delegate_form = NewDelegateForm(request.POST, instance=registrant)
            delegate_form.save()
            registrant.modified_by = request.user
            registrant.date_modified = timezone.now()
            registrant.save()
        else:
            registrant = Registrants(
                crm_person=crm_match,
                assistant=assistant,
                company=company,
                salutation=request.POST['salutation'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                title=request.POST['title'],
                email1=request.POST['email1'],
                email2=request.POST['email2'],
                phone1=request.POST['phone1'],
                phone2=request.POST['phone2'],
                contact_option=request.POST['contact_option'],
                # delegate_notes=request.POST['delegate_notes'],
                created_by=request.user,
                date_created=timezone.now(),
                modified_by=request.user,
                date_modified=timezone.now(),
            )
            registrant.save()

    # e. reg_details
    if not current_registration:
        reg_detail_db_check = RegDetails.objects.filter(
            conference=conference,
            registrant=registrant
        )
        if reg_detail_db_check.count() > 0 and \
            reg_detail_db_check[0].registration_status not in ('SP', 'SU'):
            current_registration = reg_detail_db_check[0]
        else:
            current_registration = RegDetails(
                date_created=timezone.now(),
                created_by=request.user,
            )
    current_registration.conference = conference
    current_registration.registrant = registrant
    current_registration.register_date = request.POST['register_date']
    if request.POST['cancellation_date'] != '':
        current_registration.cancellation_date = \
            request.POST['cancellation_date']
    else:
        current_registration.cancellation_date = None
    current_registration.registration_status = \
        request.POST['registration_status']
    current_registration.modified_by = request.user
    current_registration.date_modified = timezone.now()
    current_registration.save()

    # f. invoice details
    try:
        current_invoice = Invoice.objects.get(reg_details=current_registration)
    except Invoice.DoesNotExist:
        # The following ensures that we can issue more than one Invoice
        # to a sponsor (for partial payments)
        if current_registration.registration_status in NON_INVOICE_VALUES:
            current_invoice = None
        else:
            current_invoice = Invoice(
                reg_details=current_registration,
            )
    if current_invoice:
        reg_details_form = RegDetailsForm(reg_details_data,
                                          instance=current_invoice)
        reg_details_form.save()

    # g. Event Options (if applicable)
    if len(option_list) > 0:
        for option in option_list:
            new_option = RegEventOptions(
                reg=current_registration,
                option=option
            )
            new_option.save()

    return current_registration, registrant, assistant


#############################
# VIEW FUNCTIONS
#############################
@login_required
def confirmation_details(request):
    """
    Renders confirmation_details page
    as redirect from form submission on index
    """
    current_registration = RegDetails.objects.get(
        pk=request.session['current_registration']
    )
    registrant = Registrants.objects.get(pk=request.session['registrant'])
    if request.session['assistant']:
        assistant = Assistant.objects.get(pk=request.session['assistant'])
    else:
        assistant = None

    context = {
        'current_registration': current_registration,
        'registrant': registrant,
        'assistant': assistant
    }
    return render(request, 'delegate/confirmation_details.html', context)


@login_required
def index(request):
    """ renders base delegate/index.html page """
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    new_company_form = NewCompanyForm()
    company_match_list = None
    assistant_form = AssistantForm()
    conference_select_form = ConferenceSelectForm()
    reg_details_form = RegDetailsForm()
    current_registration = None
    conference = None
    conference_options = None  # Remove when form working
    registrant = None
    company = None
    assistant = None
    crm_match = None
    crm_match_list = None
    options_form = None
    data_source = None
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        conference_options = conference.eventoptions_set.all()
        options_form = OptionsForm(conference)
        crm_id = request.POST['crm_id']
        registrant_id = request.POST['registrant_id']
        conference_select_form = ConferenceSelectForm({'event': conf_id})
        if registrant_id:
            registrant = Registrants.objects.get(pk=registrant_id)
            new_delegate_form = NewDelegateForm(instance=registrant)
            company = registrant.company
            company_select_form = CompanySelectForm(instance=company)
            assistant = registrant.assistant
            if assistant:
                assistant_form = AssistantForm(instance=assistant)
            if registrant.crm_person:
                crm_match = Person.objects.get(pk=registrant.crm_person.id)
            crm_match_list = Person.objects.filter(
                Q(name__icontains=registrant.first_name) &
                Q(name__icontains=registrant.last_name),
                Q(company__icontains=registrant.company.name)
            ).order_by('company', 'name')[:100]
            company_match_list = Company.objects.filter(
                name__icontains=company.name
            )
            data_source = 'delegate'
        else:  # No registrant, so use CRM
            crm_match = Person.objects.get(pk=request.POST['crm_id'])
            name_tokens = crm_match.name.split()
            if len(name_tokens) == 1:
                first_name_guess = ''
                last_name_guess = name_tokens[0]
            elif len(name_tokens) > 1:
                first_name_guess = name_tokens[0]
                last_name_guess = ' '.join(name_tokens[1:])
            else:
                first_name_guess = last_name_guess = ''
            form_data = {'first_name': first_name_guess,
                         'last_name': last_name_guess,
                         'title': crm_match.title,
                         'email1': crm_match.email,
                         'phone1': crm_match.phone,
                         'contact_option': 'D',
            }
            new_delegate_form = NewDelegateForm(form_data)
            crm_match_list = Person.objects.filter(
                name__icontains=crm_match.name,
                company__icontains=crm_match.company
            )
            company_match_list = Company.objects.filter(
                name__icontains=crm_match.company
            )
            company_select_form = CompanySelectForm(
                {'name': crm_match.company}
            )
            data_source = 'crm'
    context = {
        'current_registration': current_registration,
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'new_company_form': new_company_form,
        'company_match_list': company_match_list,
        'assistant_form': assistant_form,
        'conference_select_form': conference_select_form,
        'reg_details_form': reg_details_form,
        'conference': conference,
        'conference_options': conference_options,  # remove when form working
        'options_form': options_form,
        'registrant': registrant,
        'company': company,
        'assistant': assistant,
        'crm_match': crm_match,
        'crm_match_list': crm_match_list,
        'paid_status_values': PAID_STATUS_VALUES,
        'cxl_values': CXL_VALUES,
        'non_invoice_values': NON_INVOICE_VALUES,
        'data_source': data_source,
    }
    return render(request, 'delegate/index.html', context)


@login_required
def process_registration(request):
    """ form submission """

    # request.session['current_registration'] = 1
    # request.session['registrant'] = 1
    # request.session['assistant'] = 1
    # return redirect('/delegate/confirmation_details')

    # 1. instantiate various Nones
    current_registration = None
    new_delegate_form = NewDelegateForm()
    company_select_form = CompanySelectForm()
    new_company_form = NewCompanyForm()
    company_match_list = None
    assistant_form = AssistantForm()
    conference_select_form = ConferenceSelectForm()
    reg_details_form = RegDetailsForm()
    conference = None
    conference_options = None
    options_form = None
    registrant = None
    company = None
    assistant = None
    crm_match = None
    crm_match_list = None
    data_source = None
    company_error = None
    assistant_missing = None
    option_selection_needed = None
    option_list = []

    # 2. verify that it's a POST and define objects based on POST data
    if request.method == 'POST':
        # Populate forms with appropriate data
        new_delegate_form = NewDelegateForm(request.POST)
        company_select_form = CompanySelectForm(request.POST)
        assistant_data = {
            'salutation': request.POST['assistant_salutation'],
            'first_name': request.POST['assistant_first_name'],
            'last_name': request.POST['assistant_last_name'],
            'title': request.POST['assistant_title'],
            'email': request.POST['assistant_email'],
            'phone': request.POST['assistant_phone'],
        }
        assistant_form = AssistantForm(assistant_data)
        reg_details_data = {
            'sales_credit': request.POST['sales_credit'],
            'pre_tax_price': request.POST['pre_tax_price'],
            'gst_rate': request.POST['gst_rate'] if 'gst_rate' in \
                request.POST else 0,
            'hst_rate': request.POST['hst_rate'] if 'hst_rate' in \
                request.POST else 0,
            'qst_rate': request.POST['qst_rate'] if 'qst_rate' in \
                request.POST else 0,
            'payment_date': request.POST['payment_date'] if 'payment_date' in \
                request.POST else None,
            'payment_method': request.POST['payment_method'] if \
                'payment_method' in request.POST else None,
            'deposit_amount': request.POST['deposit_amount'] if \
                'deposit_amount' in request.POST else None,
            'deposit_date': request.POST['deposit_date'] if 'deposit_date' in \
                request.POST else None,
            'deposit_method': request.POST['deposit_method'] if \
                'deposit_method' in request.POST else None,
            'fx_conversion_rate': request.POST['fx_conversion_rate'] if \
                'fx_conversion_rate' in request.POST else 1,
            'register_date': timezone.now(),
            'cancellation_date': request.POST['cancellation_date'] if \
                'cancellation_date' in request.POST else None,
            'registration_status': request.POST['registration_status'],
            'invoice_notes': request.POST['invoice_notes'],
            'registration_notes': request.POST['registration_notes'],
            'sponsorship_description': request.POST['sponsorship_description'] \
                if 'sponsorship_description' in request.POST else None
        }
        reg_details_form = RegDetailsForm(reg_details_data)
        if request.POST['current_regdetail_id']:
            current_registration = RegDetails.objects.get(
                pk=request.POST['current_regdetail_id']
            )

        # set up various objects if present in form
        if request.POST['current_registrant_id']:
            registrant = Registrants.objects.get(
                pk=request.POST['current_registrant_id']
            )
        if request.POST['crm_match_value']:
            crm_match = Person.objects.get(pk=request.POST['crm_match_value'])
        if request.POST['selected_conference_id']:
            conference = Event.objects.get(
                pk=request.POST['selected_conference_id']
            )
        if request.POST['assistant_match_value']:
            assistant = Assistant.objects.get(
                pk=request.POST['assistant_match_value']
            )

        # ensure that various values are correctly submitted
        if request.POST['company_match_value']:
            company = Company.objects.get(pk=request.POST['company_match_value'])
        else:
            company_error = True
        if request.POST['contact_option'] in ['A', 'C'] and not \
            request.POST['assistant_email']:
            assistant_missing = True
        if request.POST.getlist('event-option-selection'):
            for option in request.POST.getlist('event-option-selection'):
                option_list.append(EventOptions.objects.get(pk=option))
        if len(option_list) == 0 and len(conference.eventoptions_set.all()) > 1:
            option_selection_needed = True
        elif len(option_list) == 0 and len(
            conference.eventoptions_set.all()) == 1:
            option_list.append(conference.eventoptions_set.all()[0])

        # ensure everything is valid, then process registration
        if new_delegate_form.is_valid() and company_select_form.is_valid() \
            and assistant_form.is_valid() and reg_details_form.is_valid() \
            and not company_error and not assistant_missing \
            and not option_selection_needed and conference:

            current_registration, registrant, assistant = \
                process_complete_registration(request, assistant_data, company,
                                              crm_match, current_registration,
                                              reg_details_data, registrant,
                                              conference, option_list)
            request.session['current_registration'] = current_registration.pk
            request.session['registrant'] = registrant.pk
            request.session['assistant'] = assistant.pk if assistant else None
            return redirect('/delegate/confirmation_details')

    context = {
        'current_registration': current_registration,
        'new_delegate_form': new_delegate_form,
        'company_select_form': company_select_form,
        'new_company_form': new_company_form,
        'company_match_list': company_match_list,
        'assistant_form': assistant_form,
        'conference_select_form': conference_select_form,
        'reg_details_form': reg_details_form,
        'conference': conference,
        'conference_options': conference_options,  # remove when form working
        'options_form': options_form,
        'registrant': registrant,
        'company': company,
        'assistant': assistant,
        'crm_match': crm_match,
        'crm_match_list': crm_match_list,
        'paid_status_values': PAID_STATUS_VALUES,
        'cxl_values': CXL_VALUES,
        'non_invoice_values': NON_INVOICE_VALUES,
        'data_source': data_source,
        'company_error': company_error,
        'assistant_missing': assistant_missing,
        'option_selection_needed': option_selection_needed,
    }
    return render(request, 'delegate/index.html', context)


#######################
# AJAX Calls
#######################
@login_required
def add_new_company(request):
    """ ajax call to add new company to database and link to current record """
    company = None
    company_match_list = None
    registrant = None
    company_select_form = CompanySelectForm()
    if request.method == 'POST':
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
        company_select_form = CompanySelectForm(request.POST)
        if company_select_form.is_valid():
            company = company_select_form.save()
            if registrant:
                registrant.company = company
                registrant.save()
            company_select_form = CompanySelectForm()
        company_match_list = Company.objects.filter(
            name__icontains=request.POST['name']
        )
    context = {
        'company': company,
        'company_match_list': company_match_list,
        'company_select_form': company_select_form,
        'registrant': registrant,
    }
    return render(request, 'delegate/addins/company_sidebar.html', context)


@login_required
def conf_has_regs(request):
    if request.method != 'POST':
        return HttpResponse('')
    conference = get_object_or_404(Event, pk=request.POST['conf_id'])
    if RegDetails.objects.filter(conference=conference).count() > 0:
        first_reg = 'true'
    else:
        first_reg = 'false'
    print(conference)
    print(conference.billing_currency)
    context = {
        'first_reg': first_reg,
        'conference': conference,
    }
    return render(request, 'delegate/addins/conf_setup_modal.html', context)


@login_required
def link_new_company_record(request):
    """ ajax call to link selected company record to delegate """
    company = None
    if request.method == 'POST':
        company = Company.objects.get(pk=request.POST['company_match_id'])
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
            registrant.company = company
            registrant.save()
    context = {
        'company': company,
    }
    return render(request, 'delegate/addins/company_sidebar_selected.html',
                  context)


@login_required
def link_new_crm_record(request):
    """ Ajax call to link different crm record to delegate """
    crm_match = None
    if request.method == 'POST':
        crm_match = Person.objects.get(pk=request.POST['crm_match_id'])
        if request.POST['delegate_id'] != 'new':
            registrant = Registrants.objects.get(pk=request.POST['delegate_id'])
            registrant.crm_person = crm_match
            registrant.save()
    context = {
        'crm_match': crm_match,
    }
    return render(request, 'delegate/addins/crm_sidebar_selected.html', context)


@login_required
def save_comany_changes(request):
    """ ajax submission to update company information when present """
    pass


@login_required
def update_conference_options(request):
    """ ajax call to update conference options when event is changed """
    conference_options = None
    if request.method == 'POST':
        conf_id = request.POST['conf_id']
        conference = Event.objects.get(pk=conf_id)
        conference_options = conference.eventoptions_set.all()
    context = {'conference_options': conference_options}
    return render(request, 'delegate/addins/conference_options.html', context)


@login_required
def update_crm_match_list(request):
    """ ajax call to update crm suggestions based on delegate info """
    crm_match_list = None
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        company = request.POST['company']
        crm_match_list = Person.objects.filter(
            Q(name__icontains=first_name) &
            Q(name__icontains=last_name),
            Q(company__icontains=company)
        ).order_by('company', 'name')[:100]
    context = {
        'crm_match_list': crm_match_list,
    }
    return render(request, 'delegate/addins/crm_sidebar_list.html', context)


@login_required
def update_cxl_info(request):
    """ ajax call to update cancellation information """
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        form_data = {'registration_status': request.POST['reg_status'],
                     'cancellation_date': timezone.now()}
        if request.POST['regdetail_id'] != 'new':
            current_reg = RegDetails.objects.get(
                pk=request.POST['regdetail_id']
            )
            form_data['cancellation_date'] = current_reg.cancellation_date
            reg_details_form = RegDetailsForm(form_data, instance=current_reg)
        else:
            reg_details_form = RegDetailsForm(form_data)
    context = {
        'reg_details_form': reg_details_form,
        'cxl_values': CXL_VALUES,
    }
    return render(request, 'delegate/addins/cancellation_details.html',
                  context)


@login_required
def update_fx_conversion(request):
    """
    ajax call to update fx_conversion
    happens when selected conference is changed
    should only be called for new registration
    """
    conference = None
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        conference = Event.objects.get(pk=request.POST['conf_id'])
    context = {'conference': conference,
               'reg_details_form': reg_details_form}
    return render(request, 'delegate/addins/fx_details.html', context)


@login_required
def update_payment_details(request):
    """ ajax call to update payment details """
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        form_data = {'registration_status': request.POST['reg_status'],
                     'payment_method': None}
        if request.POST['reg_status'] in PAID_STATUS_VALUES:
            form_data['payment_date'] = timezone.now()
        if request.POST['regdetail_id'] != 'new':
            current_reg = RegDetails.objects.get(
                pk=request.POST['regdetail_id']
            )
            form_data['sponsorship_description'] = \
                current_reg.sponsorship_description
            form_data['payment_date'] = current_reg.payment_date
            form_data['payment_method'] = current_reg.payment_method
            reg_details_from = RegDetailsForm(form_data, instance=current_reg)
        else:
            reg_details_form = RegDetailsForm(form_data)
    context = {
        'reg_details_form': reg_details_form,
        'paid_status_values': PAID_STATUS_VALUES,
    }
    return render(request, 'delegate/addins/status_based_reg_fields.html',
                  context)


@login_required
def update_tax_information(request):
    """
    ajax call to update part of delegate page showing tax info
    happens when selected conference is changed
    should only be called for new registration
    """
    conference = None
    reg_details_form = RegDetailsForm()
    if request.method == 'POST':
        conference = Event.objects.get(pk=request.POST['conf_id'])
    context = {'conference': conference,
               'reg_details_form': reg_details_form}
    return render(request, 'delegate/addins/delegate_tax_information.html',
                  context)


############################
# GRAPHICS/DOCUMENTS
############################
@login_required
def generate_invoice(request):
    reg_details = get_object_or_404(RegDetails, pk=request.GET.get('reg', ''))
    invoice = get_object_or_404(Invoice, reg_details=reg_details)
    file_details = 'inline; filename="invoice_' + str(invoice.pk) + '"'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = file_details
    buffr = BytesIO()
    invoice_pdf = canvas.Canvas(buffr, pagesize=letter)
    logo_path = os.path.join(BASE_DIR,
                             'delegate/static/delegate/INFONEX-logo-tag.jpg')
    black = colors.black

    # Header
    invoice_pdf.setFont('Helvetica-BoldOblique', 16)
    invoice_pdf.drawString(7.2 * inch, 10.275 * inch,'INVOICE')
    invoice_pdf.setLineWidth(2)
    invoice_pdf.line(0.45 * inch, 10.15 * inch, 8.2 * inch, 10.15 * inch)
    invoice_pdf.setLineWidth(1)
    invoice_pdf.line(0.45 * inch, 10.15 * inch - 3, 8.2 * inch, 10.15 * inch - 3)
    invoice_pdf.drawImage(logo_path, 0.45 * inch, 10.275 * inch,
                          height=0.5*inch, width=1.875*inch)

    # Footer
    company_address = [
        'INFONEX',
        '360 Bay Street, Suite 900',
        'Toronto, ON M5H 2V6',
        'Phone: (416) 971-4177',
        'Email: register@infonex.ca',
    ]
    if reg_details.conference.event_web_site:
        company_address.append('Web: ' + reg_details.conference.event_web_site)
    invoice_pdf.setFont('Helvetica-Bold', 10)
    invoice_pdf.drawString(0.45 * inch, 0.75 * inch,
                    'Please Make Cheques Payable to Infonex Inc.')
    invoice_pdf.setFont('Helvetica-Bold', 8)
    invoice_pdf.drawString(0.45 * inch, 0.5 * inch,
                    'GST/HST No: R134050012')
    y = 0.75 *inch
    for line in company_address:
        invoice_pdf.drawRightString(8.2 * inch, y, line)
        y -= 9.6

    # Invoice number & date
    invoice_pdf.setFont('Helvetica-Bold', 10)
    invoice_pdf.drawRightString(7 * inch, 9.8 * inch, 'Invoice Number')
    invoice_pdf.drawRightString(7 * inch, 9.5 * inch, 'Date')
    invoice_pdf.setFont('Helvetica', 12)
    invoice_pdf.drawString(7.2 * inch, 9.8 * inch, str(invoice.pk))
    invoice_pdf.drawString(7.2 * inch, 9.5 * inch,
                           str(reg_details.register_date))

    # Customer Info
    customer_details = []
    if reg_details.registrant.salutation:
        cust_name = reg_details.registrant.salutation + ' '
    else: cust_name = ''
    if reg_details.registrant.first_name:
        cust_name += reg_details.registrant.first_name + ' '
    if reg_details.registrant.last_name:
        cust_name += reg_details.registrant.last_name
    customer_details.append(cust_name)
    if reg_details.registrant.title:
        customer_details.append(reg_details.registrant.title)
    if reg_details.registrant.company.name:
        customer_details.append(reg_details.registrant.company.name)
    if reg_details.registrant.company.address1:
        customer_details.append(reg_details.registrant.company.address1)
    if reg_details.registrant.company.address2:
        customer_details.append(reg_details.registrant.company.address2)
    if reg_details.registrant.company.city:
        city_line = reg_details.registrant.company.city
    else:
        city_line = ''
    if reg_details.registrant.company.state_prov:
        if len(city_line) > 0:
            city_line += ', '
        city_line += reg_details.registrant.company.state_prov + ' '
    if reg_details.registrant.company.postal_code:
        city_line += reg_details.registrant.company.postal_code
    if len(city_line) > 0:
        customer_details.append(city_line)
    if reg_details.registrant.company.country:
        customer_details.append(reg_details.registrant.company.country)
    invoice_pdf.setFont('Helvetica', 11)
    invoice_pdf.drawString(0.45 * inch, 9.5 * inch, 'SOLD TO:')
    invoice_pdf.setFont('Helvetica', 10)
    y = 9.2 * inch
    for line in customer_details:
        invoice_pdf.drawString(0.45 * inch, y, line)
        y -= 12

    # Details Box
    invoice_pdf.setLineWidth(1)
    invoice_pdf.rect(0.45 * inch, 5.15 * inch, 7.75 * inch, 2.75 * inch)
    invoice_pdf.line(0.45 * inch, 7.65 * inch, 8.2 * inch, 7.65 * inch)
    invoice_pdf.line(1.2 * inch, 5.15 * inch, 1.2 * inch, 7.9 * inch)
    invoice_pdf.line(7.2 * inch, 5.15 * inch, 7.2 * inch, 7.9 * inch)
    # put in header info
    invoice_pdf.setFont('Helvetica', 10)
    invoice_pdf.drawCentredString(0.825 * inch, 7.7 * inch, 'Event No.')
    invoice_pdf.drawString(1.4 * inch, 7.7 * inch, 'Registration Details')
    invoice_pdf.drawCentredString(7.7 * inch, 7.7 * inch, 'Amount Due')
    # add order details
    invoice_pdf.setFont('Helvetica-Bold', 12)
    invoice_pdf.drawString(1.4 * inch , 7.4 * inch, reg_details.conference.title)
    invoice_pdf.setFont('Helvetica', 12)
    invoice_pdf.drawCentredString(0.825 * inch, 7.4 * inch,
                                  reg_details.conference.number)
    invoice_pdf.drawRightString(8.1 * inch, 7.4 * inch,
                                '${:,.2f}'.format(invoice.pre_tax_price))
    invoice_pdf.drawString(1.4 * inch, 7.15 * inch, 'Attendee: ' + cust_name)
    invoice_pdf.drawString(1.4 * inch, 6.9 * inch,
                           reg_details.conference.city + ', ' + \
                               reg_details.conference.state_prov)
    reg_option_list = []
    if reg_details.regeventoptions_set.all().count() > 0:
        for detail in reg_details.regeventoptions_set.all():
            start_date = detail.option.startdate.strftime('%-d %B, %Y')
            end_date = detail.option.enddate.strftime('%-d %B, %Y')
            conf_detail = detail.option.name + ' - ' + start_date
            if start_date != end_date:
                conf_detail += ' to ' + end_date
            reg_option_list.append(conf_detail)
    else:
        detail_date = reg_details.conference.date_begins.strftime('%-d %B, %Y')
        conf_detail = 'Conference - ' + detail_date
        reg_option_list.append(conf_detail)
    y = 6.65 * inch
    for option in reg_option_list:
        invoice_pdf.drawString(1.6 * inch, y, option)
        y -= 14


    # Do Stuff

    invoice_pdf.showPage()
    invoice_pdf.save()
    pdf = buffr.getvalue()
    buffr.close()
    response.write(pdf)
    return response
