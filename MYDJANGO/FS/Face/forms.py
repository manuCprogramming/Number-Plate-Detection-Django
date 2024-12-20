from django import forms
from .models import LicensePlate

class LicensePlateForm(forms.ModelForm):
    class Meta:
        model = LicensePlate
        fields = ['plate_number', 'name', 'rc_number', 'place', 'age', 'vehicle_type', 'vehicle_name', 'mobile_number', 'aadhar_number', 'image']
