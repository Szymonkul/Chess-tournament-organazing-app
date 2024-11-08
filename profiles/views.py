from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from profiles.forms import ProfileForm
from profiles.models import Profile


# Create your views here.

def profile(request, user_id):
    current_user = User.objects.get(pk=user_id)
    profile = Profile.objects.get(user=user_id)

    if profile.title_or_category in ['I', 'II', 'III', 'IV', 'V', 'Bk']:
        title = False
    else:
        title = True

    return render(request, 'profiles/profile.html', {'profile': profile, 'title': title})


def profile_edit(request, user_id):
    user = User.objects.get(pk=user_id)
    profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user.id)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/profile_edit.html', {'user': user, 'form': form, 'birth_date': profile.birth_date})
