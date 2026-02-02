from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import VehicleOwnerProfile, MechanicProfile, ServiceRequest

class VehicleOwnerInline(admin.StackedInline):
    model = VehicleOwnerProfile
    can_delete = False
    verbose_name_plural = 'Vehicle Owner Profile'

class MechanicInline(admin.StackedInline):
    model = MechanicProfile
    can_delete = False
    verbose_name_plural = 'Mechanic Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (VehicleOwnerInline, MechanicInline)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'mechanic', 'detected_category', 'status', 'is_emergency', 'created_at')
    list_filter = ('status', 'is_emergency', 'detected_category')
    search_fields = ('customer__username', 'mechanic__username', 'issue_description')
