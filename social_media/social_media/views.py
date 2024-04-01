from django.http import HttpRequest
from django.shortcuts import render,redirect
from profiles.models import Profile


def  home_view(request):

    profile = Profile.objects.get(user = request.user)

    context = {
        'profile': profile,
       
    }

    return render(request, 'main/home.html', context)

def redirect_to_login(request):
    return redirect('account_login')  # Assuming 'account_login' is the name of the login URL.


# def  explore_view(request):

#     return render(request, 'main/explore.html')

# def  notifications_view(request):

#     return render(request, 'main/notifications.html')