import math
from .models import MechanicProfile, SKILL_CHOICES

# Simple Keyword-based Classifier for MVP
# In a real system, you'd use NLTK, Spacy, or a pre-trained Transformer model.
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
    
    # Check for emergency/accident first
    for word in KEYWORDS['Accident']:
        if word in text:
            return 'Accident', 1.0 # High priority
            
    scores = {key: 0 for key in KEYWORDS if key != 'Accident'}
    
    # Calculate simple frequency score
    for category, words in KEYWORDS.items():
        if category == 'Accident': continue
        for word in words:
            if word in text:
                scores[category] += 1
                
    # Find max score
    best_category = 'General'
    max_score = 0
    total_hits = sum(scores.values())
    
    if total_hits > 0:
        for cat, score in scores.items():
            if score > max_score:
                max_score = score
                best_category = cat
    
    # Calculate confidence (heuristic)
    confidence = 0.5 # Default low confidence
    if total_hits > 0:
        confidence = min(0.5 + (max_score / total_hits * 0.4) + (total_hits * 0.1), 1.0)
        
    return best_category, confidence

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles.
    return c * r

def find_nearest_mechanic(user_lat, user_lon, issue_category):
    """
    Finds the nearest available mechanic with the appropriate skill.
    Returns: MechanicProfile object or None
    """
    required_skill = issue_category
    
    # Map Accident/General to closest skills or default to General/Any
    if issue_category == 'Accident':
        # For accidents, maybe any mechanic or specific one? 
        # Requirement says "Still allow mechanic dispatch if vehicle damage involved"
        # Let's assume General or Engine, or just look for nearest ANY mechanic if we treated skills strictly.
        # But for MVP, let's filter purely by availability first, then skill if strictly needed.
        # Let's prioritize Mechanics who listed 'General' or match specific sub-issues if we could parsing more.
        # Simply: Accident -> General for now, or check all.
        pass 

    # Filter mechanics by skill (if not general/accident which might be flexible)
    # If category is General or Accident, we might accept any skill, but let's prefer 'General' 
    # or just find ANY nearby for Accident.
    
    candidates = MechanicProfile.objects.filter(is_available=True)
    
    if issue_category in ['Battery', 'Tyre', 'Engine']:
        candidates = candidates.filter(skill_type=issue_category)
    
    # If no specific skill match, maybe fallback to General?
    if not candidates.exists() and issue_category in ['Battery', 'Tyre', 'Engine']:
         candidates = MechanicProfile.objects.filter(is_available=True, skill_type='General')

    # If still no candidates, return None (or handle in dispatch logic)
    if not candidates.exists():
        # Last resort: Any available mechanic for emergencies?
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
