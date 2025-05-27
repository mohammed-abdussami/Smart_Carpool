from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import UserProfile, Schedule, Match, ChatRoom, ChatMessage
from .utils import create_matches_for_user
from .forms import ProfileForm, ScheduleForm
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

# Constants
ALLOWED_MATCH_STATUSES = ['accepted', 'rejected', 'pending']

# Utility Functions
def get_user_matches(user):
    """DRY helper to get matches for a user"""
    return Match.objects.filter(
        Q(schedule1__user=user) | Q(schedule2__user=user)
    )

# Views
def home(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
        messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        logger.info(f'Creating UserProfile for new user: {request.user.username}')
        profile = UserProfile.objects.create(user=request.user)

    schedules = Schedule.objects.filter(user=request.user)
    matches = get_user_matches(request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'schedules': schedules,
        'matches': matches,
        'form': form,
    }
    return render(request, 'profile.html', context)

@login_required
def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()
            create_matches_for_user(request.user)
            messages.success(request, 'Schedule added successfully!')
            return redirect('profile')
    else:
        form = ScheduleForm()
    return render(request, 'add_schedule.html', {'form': form})

@login_required
def matches_view(request):
    matches = get_user_matches(request.user).select_related(
        'schedule1', 'schedule2', 'schedule1__user', 'schedule2__user'
    )

    incoming = []
    outgoing = []
    
    for match in matches:
        if match.schedule2.user == request.user:
            incoming.append(match)
        else:
            outgoing.append(match)

    context = {
        'incoming_matches': incoming,
        'outgoing_matches': outgoing,
    }
    return render(request, 'matches.html', context)

@login_required
def chat_room(request, match_id):
    match = Match.objects.filter(
        id=match_id,
        status='accepted'
    ).filter(
        Q(schedule1__user=request.user) | Q(schedule2__user=request.user)
    ).first()

    if not match:
        messages.error(request, 'Chat room not found or access denied.')
        return redirect('matches')
    
    room, created = ChatRoom.objects.get_or_create(match=match)
    other_user = match.schedule2.user if match.schedule1.user == request.user else match.schedule1.user
    messages = room.messages.all().order_by('timestamp')[:50]
    
    return render(request, 'chat_room.html', {
        'room': room,
        'other_user': other_user,
        'messages': messages,
    })

@login_required
def update_match_status(request, match_id, status):
    if status not in ALLOWED_MATCH_STATUSES:
        messages.error(request, 'Invalid status.')
        return redirect('matches')

    try:
        match = Match.objects.get(id=match_id)
        if match.schedule2.user == request.user or match.schedule1.user == request.user:
            match.status = status
            match.save()
            messages.success(request, f'Match {status} successfully!')
        else:
            messages.error(request, 'You cannot update this match.')
    except Match.DoesNotExist:
        messages.error(request, 'Match not found.')
    return redirect('matches')