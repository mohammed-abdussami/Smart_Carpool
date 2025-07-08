import logging
from math import radians, sin, cos, sqrt, atan2
from django.db import models
from django.utils import timezone
from .models import Schedule, Match
from datetime import datetime

logger = logging.getLogger(__name__)

def simple_distance(loc1, loc2):
    """
    Calculate a simple distance score between two locations
    Uses string similarity for demonstration - replace with your own logic
    """
    from difflib import SequenceMatcher
    return 1 - SequenceMatcher(None, loc1.lower(), loc2.lower()).ratio()

def calculate_distance(origin1, dest1, origin2, dest2):
    """
    Simplified distance calculation without geospatial dependencies
    """
    try:
        origin_score = simple_distance(origin1, origin2)
        dest_score = simple_distance(dest1, dest2)
        
        return {
            'origin_distance': origin_score * 10,  # Scale to km-like units
            'dest_distance': dest_score * 10,
            'average_distance': (origin_score + dest_score) * 5
        }
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        return None

from datetime import datetime

def time_difference(time1, time2):
    """Calculate time difference in minutes"""
    if isinstance(time1, str):
        try:
            time1 = datetime.strptime(time1, "%H:%M:%S").time()
        except ValueError:
            time1 = datetime.strptime(time1, "%H:%M").time()
    if isinstance(time2, str):
        try:
            time2 = datetime.strptime(time2, "%H:%M:%S").time()
        except ValueError:
            time2 = datetime.strptime(time2, "%H:%M").time()

    now = timezone.now()
    datetime1 = now.replace(hour=time1.hour, minute=time1.minute, second=0, microsecond=0)
    datetime2 = now.replace(hour=time2.hour, minute=time2.minute, second=0, microsecond=0)

    return abs((datetime1 - datetime2).total_seconds() / 60)

def find_matches(schedule):
    """Find potential matches without any geospatial dependencies"""
    same_day_schedules = Schedule.objects.filter(
        day=schedule.day
    ).exclude(
        user=schedule.user
    ).select_related('user')

    potential_matches = []
    for other_schedule in same_day_schedules:
        if Match.objects.filter(
            (models.Q(schedule1=schedule) & models.Q(schedule2=other_schedule)) |
            (models.Q(schedule1=other_schedule) & models.Q(schedule2=schedule))
        ).exists():
            continue

        distance_data = calculate_distance(
            schedule.origin, schedule.destination,
            other_schedule.origin, other_schedule.destination
        )
        if not distance_data:
            continue

        start_diff = time_difference(schedule.start_time, other_schedule.start_time)
        end_diff = time_difference(schedule.end_time, other_schedule.end_time)
        flex_bonus = 30 if (schedule.flexible or other_schedule.flexible) else 0

        score = (
            (distance_data['average_distance'] * 0.5) +
            (start_diff + end_diff) * 0.3 -
            flex_bonus * 0.2
        )

        potential_matches.append({
            'schedule': other_schedule,
            'score': score,
            'origin_distance': distance_data['origin_distance'],
            'dest_distance': distance_data['dest_distance'],
            'time_diff': (start_diff + end_diff) / 2
        })

    return sorted(potential_matches, key=lambda x: x['score'])

def create_matches_for_user(user):
    """Create matches without any special dependencies"""
    for schedule in Schedule.objects.filter(user=user):
        for match in find_matches(schedule)[:5]:  # Limit to top 5 matches
            Match.objects.create(
                schedule1=schedule,
                schedule2=match['schedule'],
                score=match['score']
            )