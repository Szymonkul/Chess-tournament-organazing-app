# core/context_processors.py
def is_organizer(request):
    is_organizer = request.user.groups.filter(name='Organizer').exists()
    return {'is_organizer': is_organizer}

