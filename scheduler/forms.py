from django import forms
from .models import UserProfile, Schedule

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'car_available', 'car_capacity', 'license_plate']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'car_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['day', 'start_time', 'end_time', 'origin', 'destination', 'flexible']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'flexible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }