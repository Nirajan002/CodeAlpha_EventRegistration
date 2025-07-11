from django.shortcuts import render, redirect, get_object_or_404
from .models import Event, Registration
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from .forms import EventForm
from django.utils import timezone

# Create your views here.
def welcome(request):
    return render(request, 'events/welcome.html')

def event_list(request):
    events = Event.objects.all()
    registered_event_ids = set()
    if request.user.is_authenticated:
        registered_event_ids = set(
            Registration.objects.filter(user=request.user, status='active')
            .values_list('event_id', flat=True)
        )
    context = {
        'events': events,
        'registered_event_ids': registered_event_ids,
        'now': timezone.now(),
    }
    return render(request, 'events/event_list.html', context, )


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registration = event.registration_set.filter(user=request.user, status='active').first()
    user_registered = bool(user_registration)

    registrations = None
    if request.user == event.created_by:
        registrations = event.registration_set.filter(status='active')

    return render(request, 'events/event_detail.html', {
        'event': event,
        'user_registered': user_registered,
        'user_registration': user_registration,
        'registrations': registrations,
    })


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if event.date < timezone.now():
        messages.error(request, "You cannot register for past events.")
        return redirect('event_detail', event_id=event.id)

    registration = Registration.objects.filter(user=request.user, event=event).first()

    if registration:
        if registration.status == 'active':
            messages.warning(request, "You have already registered.")
        else:
            registration.status = 'active'
            registration.save()
            messages.success(request, "Your registration has been reactivated!")
    else:
        Registration.objects.create(user=request.user, event=event, status='active')
        messages.success(request, "Successfully registered!")

    return redirect('event_detail', event_id=event_id)

@login_required
def my_registrations(request):
    registered_events = Event.objects.filter(
        registration__user=request.user,
        registration__status='active'
    ).distinct()

    created_events = Event.objects.filter(created_by=request.user)

    return render(request, 'events/my_registrations.html', {
        'registered_events': registered_events,
        'created_events': created_events,
    })


@login_required
def cancel_registration(request, registration_id):
    reg = get_object_or_404(Registration, id=registration_id, user=request.user)
    reg.status = 'cancelled'
    reg.save()
    messages.info(request, "Registration cancelled.")
    return redirect('event_detail', event_id=reg.event.id)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if request.user.is_authenticated:
                event.created_by = request.user
            event.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, created_by=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
        return redirect('event_list')

    return render(request, 'events/confirm_delete.html', {'event': event})
