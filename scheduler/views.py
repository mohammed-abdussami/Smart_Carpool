import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from .forms import EmailUserCreationForm, EmailAuthenticationForm, ProfileForm, ScheduleForm
from .models import UserProfile, Schedule, Match, ChatRoom, ChatMessage
from .utils import create_matches_for_user

logger = logging.getLogger(__name__)
ALLOWED_MATCH_STATUSES = ['accepted', 'rejected', 'pending']


def get_user_matches(user):
    return Match.objects.filter(
        Q(schedule1__user=user) | Q(schedule2__user=user)
    )


def home(request):
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('profile')
    else:
        form = EmailUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    schedules = Schedule.objects.filter(user=request.user).order_by('day', 'start_time')
    matches = get_user_matches(request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'profile': profile,
        'schedules': schedules,
        'matches': matches,
        'form': form,
    })


@login_required(login_url='login')
def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()
            create_matches_for_user(request.user)
            messages.success(request, 'Schedule added! Checking for matches...')
            return redirect('profile')
    else:
        form = ScheduleForm()
    return render(request, 'add_schedule.html', {'form': form})


@login_required(login_url='login')
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    schedule.delete()
    messages.success(request, 'Schedule deleted.')
    return redirect('profile')


@login_required
def matches_view(request):
    matches = get_user_matches(request.user).select_related(
        'schedule1__user', 'schedule2__user'
    ).order_by('-created_at')

    incoming, outgoing = [], []
    for match in matches:
        if match.schedule2.user == request.user:
            incoming.append(match)
        else:
            outgoing.append(match)

    return render(request, 'matches.html', {
        'incoming_matches': incoming,
        'outgoing_matches': outgoing,
    })


@login_required
def update_match_status(request, match_id, status):
    if status not in ALLOWED_MATCH_STATUSES:
        messages.error(request, 'Invalid status.')
        return redirect('matches')
    match = get_object_or_404(Match, id=match_id)
    if match.schedule1.user == request.user or match.schedule2.user == request.user:
        match.status = status
        match.save()
        messages.success(request, f'Match {status}!')
    else:
        messages.error(request, 'Permission denied.')
    return redirect('matches')


@login_required
def chat_room(request, match_id):
    match = get_object_or_404(
        Match.objects.filter(
            Q(schedule1__user=request.user) | Q(schedule2__user=request.user),
            status='accepted'
        ),
        id=match_id
    )
    room, _ = ChatRoom.objects.get_or_create(match=match)
    other_user = (
        match.schedule2.user
        if match.schedule1.user == request.user
        else match.schedule1.user
    )

    if request.method == 'POST':
        msg_text = request.POST.get('message', '').strip()
        if msg_text:
            msg = ChatMessage.objects.create(
                room=room, sender=request.user, message=msg_text
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': {
                    'sender': request.user.email.split('@')[0],
                    'text': msg.message,
                    'timestamp': msg.timestamp.strftime('%H:%M'),
                    'is_sender': True,
                }})
        return redirect('chat_room', match_id=match_id)

    chat_messages = room.messages.select_related('sender').order_by('timestamp')
    return render(request, 'chat_room.html', {
        'room': room,
        'other_user': other_user,
        'chat_messages': chat_messages,
        'match': match,
    })