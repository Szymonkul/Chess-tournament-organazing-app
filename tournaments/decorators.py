from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from .models import Tournament


def organizer_required(view_func):
    def _wrapped_view(request,tournament_id,*args,**kwargs):
        tournament = get_object_or_404(Tournament, id=tournament_id)
        if tournament.organizer != request.user:
            return redirect('home')
        return view_func(request, tournament_id, *args, **kwargs)
    return _wrapped_view
