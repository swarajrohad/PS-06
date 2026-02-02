from django import forms
from django.contrib.auth.models import User
from .models import VehicleOwnerProfile, MechanicProfile, ServiceRequest, SKILL_CHOICES

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea)
    phone_number = forms.CharField(max_length=15)
    vehicle_number = forms.CharField(max_length=20)
    emergency_contact_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'password', 'full_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            VehicleOwnerProfile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone_number=self.cleaned_data['phone_number'],
                vehicle_number=self.cleaned_data['vehicle_number'],
                emergency_contact_number=self.cleaned_data['emergency_contact_number']
            )
        return user

class MechanicRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    skill_type = forms.ChoiceField(choices=SKILL_CHOICES)
    # Location will be captured via JS preferably, or manual input for now
    current_latitude = forms.FloatField(initial=0.0, widget=forms.HiddenInput, required=False)
    current_longitude = forms.FloatField(initial=0.0, widget=forms.HiddenInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'full_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            MechanicProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                skill_type=self.cleaned_data['skill_type'],
                current_latitude=self.cleaned_data['current_latitude'] or 0.0,
                current_longitude=self.cleaned_data['current_longitude'] or 0.0
            )
        return user

class ServiceRequestForm(forms.Form):
    issue_description = forms.CharField(widget=forms.Textarea, required=False)
    # Latitude/Longitude will be filled by JS
    location_latitude = forms.FloatField(widget=forms.HiddenInput)
    location_longitude = forms.FloatField(widget=forms.HiddenInput)
    is_emergency = forms.BooleanField(required=False, widget=forms.HiddenInput)
