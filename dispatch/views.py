from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserRegistrationForm, MechanicRegistrationForm, ServiceRequestForm
from .models import ServiceRequest, MechanicProfile
from .utils import classify_issue, find_nearest_mechanic

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_home')
    else:
        form = UserRegistrationForm()
    return render(request, 'dispatch/register_user.html', {'form': form})

def register_mechanic(request):
    if request.method == 'POST':
        form = MechanicRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mechanic_dashboard')
    else:
        form = MechanicRegistrationForm()
    return render(request, 'dispatch/register_mechanic.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if hasattr(user, 'mechanic_profile'):
                return redirect('mechanic_dashboard')
            else:
                return redirect('user_home')
    else:
        form = AuthenticationForm()
    return render(request, 'dispatch/login.html', {'form': form})

@login_required
def user_home(request):
    return render(request, 'dispatch/user_home.html')

@login_required
def create_request(request):
    if request.method == 'POST':
        # AJAX or Form submit
        issue_text = request.POST.get('issue_description', '')
        lat = float(request.POST.get('latitude', 0.0))
        lon = float(request.POST.get('longitude', 0.0))
        is_emergency = request.POST.get('is_emergency') == 'true'

        category, confidence = classify_issue(issue_text)
        if is_emergency:
            category = 'Accident' 
        
        # Create Request
        srv_req = ServiceRequest.objects.create(
            customer=request.user,
            issue_description=issue_text,
            detected_category=category,
            confidence_score=confidence,
            location_latitude=lat,
            location_longitude=lon,
            is_emergency=is_emergency,
            status='Open'
        )

        # Dispatch Logic
        mechanic = find_nearest_mechanic(lat, lon, category)
        if mechanic:

            srv_req.mechanic = mechanic.user
            srv_req.status = 'Assigned'
            srv_req.save()
            
            
        return JsonResponse({'status': 'success', 'request_id': srv_req.id})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def request_status(request, request_id):
    srv_req = get_object_or_404(ServiceRequest, id=request_id, customer=request.user)
    return JsonResponse({
        'status': srv_req.status,
        'mechanic': srv_req.mechanic.username if srv_req.mechanic else None,
        'category': srv_req.detected_category
    })

@login_required
def mechanic_dashboard(request):
    requests = ServiceRequest.objects.filter(mechanic=request.user, status='Assigned')

    return render(request, 'dispatch/mechanic_dashboard.html', {'requests': requests})

@login_required
def mechanic_update_request(request, request_id, action):
    srv_req = get_object_or_404(ServiceRequest, id=request_id, mechanic=request.user)
    
    if action == 'accept':
        srv_req.status = 'OnTheWay'
        request.user.mechanic_profile.is_available = False
        request.user.mechanic_profile.save()
        
    elif action == 'reject':
        srv_req.mechanic = None # Unassign
        srv_req.status = 'Open' # Back to open pool
        
    elif action == 'complete':
        srv_req.status = 'Completed'
        request.user.mechanic_profile.is_available = True
        request.user.mechanic_profile.save()
        
    srv_req.save()
    return redirect('mechanic_dashboard')

@login_required
def update_location(request):
    if request.method == 'POST':
        lat = float(request.POST.get('latitude'))
        lon = float(request.POST.get('longitude'))
        profile = request.user.mechanic_profile
        profile.current_latitude = lat
        profile.current_longitude = lon
        profile.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def toggle_availability(request):
    if request.method == 'POST':
        profile = request.user.mechanic_profile
        profile.is_available = not profile.is_available
        profile.save()
        return JsonResponse({'status': 'success', 'is_available': profile.is_available})
    return JsonResponse({'status': 'error'}, status=400)
