from django.db import models
from django.contrib.auth.models import User

SKILL_CHOICES = [
    ('Engine', 'Engine Failure'),
    ('Tyre', 'Tyre Puncture'),
    ('Battery', 'Battery Problem'),
    ('General', 'General Help'),
]

CATEGORY_CHOICES = SKILL_CHOICES + [('Accident', 'Accident / Emergency')]

class VehicleOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vehicle_owner_profile')
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    vehicle_number = models.CharField(max_length=20)
    emergency_contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.username} - Owner"

class MechanicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mechanic_profile')
    phone_number = models.CharField(max_length=15)
    current_latitude = models.FloatField(default=0.0)
    current_longitude = models.FloatField(default=0.0)
    skill_type = models.CharField(max_length=20, choices=SKILL_CHOICES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.skill_type}"

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Assigned', 'Assigned'),
        ('OnTheWay', 'On The Way'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_made')
    mechanic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests_assigned')
    
    issue_description = models.TextField()
    detected_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    confidence_score = models.FloatField(default=0.0)
    
    location_latitude = models.FloatField()
    location_longitude = models.FloatField()
    
    is_emergency = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.detected_category} - {self.customer.username} ({self.status})"
