from django.forms.fields import MultipleChoiceField
from django import forms
from django.contrib.auth import get_user_model
from .models import BookableInput, Bookable
from django.conf import settings


TIME_FORMAT = settings.TIME_FORMAT
USER_MODEL = get_user_model()

DAYS_CHOICES = (
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday'),
)


class ServiceCreateForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    price = forms.DecimalField(min_value=0, max_digits=8, decimal_places=2)
    thumbnail = forms.ImageField(required=False)
    unit = forms.CharField(label="Price measurement unit")
    hour_start = forms.TimeField(input_formats=('%I:%M %p',))
    hour_end = forms.TimeField(input_formats=('%I:%M %p',))
    available_days = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=DAYS_CHOICES
    )
    custom_inputs = forms.CharField(required=False, widget=forms.HiddenInput())


class ServiceUpdateForm(forms.ModelForm):
    hour_start = forms.TimeField(input_formats=('%I:%M %p',), widget=forms.TimeInput(format=TIME_FORMAT))
    hour_end = forms.TimeField(input_formats=('%I:%M %p',), widget=forms.TimeInput(format=TIME_FORMAT))
    available_days = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=DAYS_CHOICES,
        required=False
    )

    class Meta:
        model = Bookable
        fields = ['name', 'description', 'price', 'thumbnail', 'unit', 'hour_start', 'hour_end']


class CustomForm(forms.Form):
    def __init__(self, *args, **kwargs):
        custom_inputs = kwargs.pop('custom_inputs')
        bookable = kwargs.pop('bookable')
        super(CustomForm, self).__init__(*args, **kwargs)

        field_address = forms.CharField(
            label="Service Address",
            required=True
        )
        field_address.widget.attrs.update({
            'asst_field_type': BookableInput.FIELD_TYPE_TEXT
        })
        self.fields["address"] = field_address

        field_selected_date = forms.DateField(
            label="Select a start date", input_formats=('%b %d, %Y',)
        )
        field_selected_date.widget.attrs.update({
            'asst_field_type': BookableInput.FIELD_TYPE_DATE
        })
        self.fields["selected_date"] = field_selected_date

        field_selected_time = forms.TimeField(
            label="Choose a time", input_formats=('%I:%M %p',)
        )
        field_selected_time.widget.attrs.update({
            'asst_field_type': BookableInput.FIELD_TYPE_TIME
        })
        self.fields["selected_time"] = field_selected_time

        quantity_label_suffix = "" if bookable.unit.endswith("s") else "s"

        field_quantity = forms.IntegerField(
            label=f"Number of {bookable.unit}{quantity_label_suffix}",
            min_value=1
        )
        field_quantity.widget.attrs.update(
            {
                'asst_field_type': BookableInput.FIELD_TYPE_TEXT,
                'value': 1
            }
        )
        self.fields["quantity"] = field_quantity

        for i, custom_input in enumerate(custom_inputs):
            label = custom_input.label
            field_type = custom_input.field_type
            field_required = custom_input.field_required
            if not field_required:
                label += " (optional)"
            if field_type == BookableInput.FIELD_TYPE_TEXT:
                new_field = forms.CharField(
                    label=label, required=field_required
                )
            elif field_type == BookableInput.FIELD_TYPE_TEXT_MULTILINE:
                new_field = forms.CharField(
                    label=label, widget=forms.Textarea, required=field_required
                )
            elif field_type == BookableInput.FIELD_TYPE_DATE:
                new_field = forms.DateField(
                    label=label, input_formats=('%b %d, %Y',), required=field_required
                )
            elif field_type == BookableInput.FIELD_TYPE_TIME:
                new_field = forms.TimeField(
                    label=label, input_formats=('%I:%M %p',), required=field_required
                )
            elif field_type == BookableInput.FIELD_TYPE_CHECKBOX:
                new_field = forms.BooleanField(
                    label=label, required=field_required
                )
            new_field.widget.attrs.update({
                'asst_field_type': field_type
            })
            self.fields['custom_input_%s' % i] = new_field


class WorkerCreateForm(forms.Form):
    user = forms.ModelChoiceField(queryset=USER_MODEL.objects.filter(profile__is_worker=False))


class WorkerDeleteForm(forms.Form):
    worker = forms.ModelChoiceField(queryset=USER_MODEL.objects.filter(profile__is_worker=True))
