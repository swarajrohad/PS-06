import math
from .models import MechanicProfile, SKILL_CHOICES


KEYWORDS = {
    'Battery': ['battery', 'dead', 'start', 'voltage', 'spark'],
    'Tyre': ['tyre', 'tire', 'flat', 'puncture', 'air', 'blowout'],
    'Engine': ['engine', 'smoke', 'noise', 'oil', 'heat', 'stall', 'breakdown'],
    'Accident': ['crash', 'accident', 'collision', 'hit', 'hurt', 'injury', 'blood', 'ambulance'],
}

def classify_issue(text):
    """
    Classifies the issue description into a category and assigns a confidence score.
    Returns: (category, confidence_score)
    """
    text = text.lower()
    
    for word in KEYWORDS['Accident']:
        if word in text:
            return 'Accident', 1.0
            
    scores = {key: 0 for key in KEYWORDS if key != 'Accident'}
    
    for category, words in KEYWORDS.items():
        if category == 'Accident': continue
        for word in words:
            if word in text:
                scores[category] += 1
                
    best_category = 'General'
    max_score = 0
    total_hits = sum(scores.values())
    
    if total_hits > 0:
        for cat, score in scores.items():
            if score > max_score:
                max_score = score
                best_category = cat
    
    confidence = 0.5 
    if total_hits > 0:
        confidence = min(0.5 + (max_score / total_hits * 0.4) + (total_hits * 0.1), 1.0)
        
    return best_category, confidence

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 
    return c * r

def find_nearest_mechanic(user_lat, user_lon, issue_category):
    """
    Finds the nearest available mechanic with the appropriate skill.
    Returns: MechanicProfile object or None
    """
    required_skill = issue_category
    
    if issue_category == 'Accident':

        pass 
    
    candidates = MechanicProfile.objects.filter(is_available=True)
    
    if issue_category in ['Battery', 'Tyre', 'Engine']:
        candidates = candidates.filter(skill_type=issue_category)
    
    if not candidates.exists() and issue_category in ['Battery', 'Tyre', 'Engine']:
         candidates = MechanicProfile.objects.filter(is_available=True, skill_type='General')

    if not candidates.exists():
        if issue_category == 'Accident':
            candidates = MechanicProfile.objects.filter(is_available=True)
            if not candidates.exists():
                return None
        else:
            return None

    best_mechanic = None
    min_dist = float('inf')

    for mechanic in candidates:
        dist = haversine(user_lat, user_lon, mechanic.current_latitude, mechanic.current_longitude)
        if dist < min_dist:
            min_dist = dist
            best_mechanic = mechanic
            
    return best_mechanic
