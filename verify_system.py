import os
import django
import sys

# Setup Django environment
sys.path.append('/home/swaraj/.gemini/antigravity/scratch/roadside_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roadside_project.settings')
django.setup()

from django.contrib.auth.models import User
from dispatch.models import MechanicProfile, VehicleOwnerProfile, ServiceRequest
from dispatch.utils import classify_issue, find_nearest_mechanic

def run_verification():
    print("--- Starting System Verification ---")
    
    # Clean up (for re-runnability)
    User.objects.filter(username__in=['test_mech', 'test_user']).delete()
    
    # 1. Create Mechanic
    print("\n1. Creating Mechanic...")
    mech = User.objects.create_user(username='test_mech', password='password123')
    MechanicProfile.objects.create(
        user=mech, 
        phone_number='1234567890', 
        skill_type='Tyre', 
        current_latitude=12.9716, # Bangalore coords example
        current_longitude=77.5946
    )
    print("   Mechanic 'test_mech' created at (12.9716, 77.5946) with skill 'Tyre'.")
    
    # 2. Create User
    print("\n2. Creating User...")
    user = User.objects.create_user(username='test_user', password='password123')
    VehicleOwnerProfile.objects.create(
        user=user, 
        address='MG Road', 
        phone_number='9876543210', 
        vehicle_number='KA01AB1234', 
        emergency_contact_number='112'
    )
    print("   User 'test_user' created.")

    # 3. Test Text Request (Matching Skill)
    print("\n3. Testing Request Dispatch (Tyre Issue)...")
    issue_text = "I have a flat tyre near MG Road"
    cat, conf = classify_issue(issue_text)
    print(f"   Issue: '{issue_text}' -> Classified as: {cat} (Conf: {conf:.2f})")
    
    # User is close to mechanic
    user_lat, user_lon = 12.9720, 77.5950 # Very close
    
    assigned_mechanic = find_nearest_mechanic(user_lat, user_lon, cat)
    if assigned_mechanic and assigned_mechanic.user.username == 'test_mech':
        print("   SUCCESS: Dispatch logic found correct mechanic.")
    else:
        print(f"   FAILURE: Dispatch logic returned {assigned_mechanic}")

    # Create the actual request object
    srv_req = ServiceRequest.objects.create(
        customer=user,
        issue_description=issue_text,
        detected_category=cat,
        confidence_score=conf,
        location_latitude=user_lat,
        location_longitude=user_lon,
        mechanic=assigned_mechanic.user if assigned_mechanic else None,
        status='Assigned' if assigned_mechanic else 'Open'
    )
    print(f"   Request ID {srv_req.id} created with Status: {srv_req.status}")

    # 4. Test Emergency Flow
    print("\n4. Testing Emergency Flow...")
    emergency_text = "Accident on flyover! Need help!"
    e_cat, e_conf = classify_issue(emergency_text)
    print(f"   Issue: '{emergency_text}' -> Classified as: {e_cat}")
    
    if e_cat == 'Accident':
        print("   SUCCESS: Emergency classifier working.")
    else:
        print("   FAILURE: Emergency classifier failed.")
        
    print("\n--- Verification Complete ---")

if __name__ == '__main__':
    run_verification()
