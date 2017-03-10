{% if edit_action != 'blank' %}
{% if edit_action == 'new' %}
<input type="hidden" value="new" id="edited-conference-status" />
<h2>
  New Conference Input
{% else %}
<input type="hidden" value="edit" id="edited-conference-status"  />
<h2>
  Edit Conference Input
{% endif %}
</h2>
<div class="row">
  <div class="col-sm-3">
    {{ conference_edit_form.number.errors }}
    {{ conference_edit_form.number.label_tag }}
    {{ conference_edit_form.number }}
  </div>
  <div class="col-sm-3 col-sm-offset-2">
    <!-- Need to add in date picker widget
        http://stackoverflow.com/questions/32892847/add-calendar-widget-to-django-form -->
    {{ conference_edit_form.date_begins.errors }}
    {{ conference_edit_form.date_begins.label_tag }}
    {{ conference_edit_form.date_begins }}
  </div>
</div>
<div class="row">
  <div class="col-sm-11">
    {{ conference_edit_form.title.errors }}
    {{ conference_edit_form.title.label_tag }}
    {{ conference_edit_form.title }}
  </div>
</div>
<div class="row">
  <div class="col-sm-6" id="conference-city-input">
    <!-- Need to add JS on keyup to limit venue choices -->
    {{ conference_edit_form.city.errors }}
    {{ conference_edit_form.city.label_tag }}
    {{ conference_edit_form.city }}
  </div>
  <div class="col-sm-3 col-sm-offset-1">
    {{ conference_edit_form.state_prov.errors }}
    {{ conference_edit_form.state_prov.label_tag }}
    {{ conference_edit_form.state_prov }}
  </div>
</div>
<div class="row">
  <div class="col-sm-11" id="event-url">
    {{ conference_edit_form.event_web_site.errors }}
    {{ conference_edit_form.event_web_site.label_tag }}
    {{ conference_edit_form.event_web_site }}
  </div>
</div>
<div class="row" id="venue-choices">
  {% include 'registration/addins/conference_venue_choices.html' %}
</div>
<div class="row">
  <div class="col-sm-5">
    {{ conference_edit_form.registrar.errors }}
    {{ conference_edit_form.registrar.label_tag }}
    {{ conference_edit_form.registrar }}
  </div>
  <div class="col-sm-5 col-sm-offset-1">
    {{ conference_edit_form.developer.errors }}
    {{ conference_edit_form.developer.label_tag }}
    {{ conference_edit_form.developer }}
  </div>
</div>
<div class="row">
  <div class="col-sm-3">
    {{ conference_edit_form.company_brand.errors }}
    {{ conference_edit_form.company_brand.label_tag }}
    {{ conference_edit_form.company_brand }}
  </div>
  <div class="col-sm-3 col-sm-offset-1">
    {{ conference_edit_form.billing_currency.errors }}
    {{ conference_edit_form.billing_currency.label_tag }}
    {{ conference_edit_form.billing_currency }}
  </div>
</div>
<div class="row">
  <div class="col-sm-2">
    {{ conference_edit_form.gst_charged.errors }}
    {{ conference_edit_form.gst_charged.label_tag }}
    {{ conference_edit_form.gst_charged }}
  </div>
  <div class="col-sm-2 col-sm-offset-1">
    {{ conference_edit_form.hst_charged.errors }}
    {{ conference_edit_form.hst_charged.label_tag }}
    {{ conference_edit_form.hst_charged }}
  </div>
  <div class="col-sm-2 col-sm-offset-1">
    {{ conference_edit_form.qst_charged.errors }}
    {{ conference_edit_form.qst_charged.label_tag}}
    {{ conference_edit_form.qst_charged }}
  </div>
</div>
<div class="row">
  <div class="col-sm-2">
    {{ conference_edit_form.gst_rate.errors }}
    {{ conference_edit_form.gst_rate.label_tag }}
    {{ conference_edit_form.gst_rate }}
  </div>
  <div class="col-sm-2 col-sm-offset-1">
    {{ conference_edit_form.hst_rate.errors }}
    {{ conference_edit_form.hst_rate.label_tag }}
    {{ conference_edit_form.hst_rate }}
  </div>
  <div class="col-sm-2 col-sm-offset-1">
    {{ conference_edit_form.qst_rate.errors }}
    {{ conference_edit_form.qst_rate.label_tag}}
    {{ conference_edit_form.qst_rate }}
  </div>
</div>
<div class="panel panel-info event-options-box">
  <div class="panel-heading">
    <h2 class="panel-title h2">Event Registration Options</h2>
  </div>
  <div class="panel-body" id="event-options-panel">
    {% include 'registration/addins/conference_options_panel.html' %}
  </div>
</div>

<div class="row">
  <button type="button" class="btn btn-warning col-sm-6 conference-change-button"
    id="abandon-conference-changes">
    Abandon Changes
  </button>
  <button type="button" class="btn btn-success col-sm-6 conference-change-button"
    id="save-conference-changes">
    Save
  </button>

</div>
{% else %}
<div class="row text-center">
  <a href="{% url 'registration:new_delegate_search' %}" class="btn btn-primary">Create New Registration</a>
</div>
{% endif %}
