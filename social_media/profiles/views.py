from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile,Relationship
from .forms import ProfileModelForm
from posts.models import Post
from posts.forms import PostModelForm
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.

def my_profile_view(request):
    profile = Profile.objects.get(user = request.user)
    form = ProfileModelForm(request.POST or None, request.FILES or None , instance = profile)
    p_form = PostModelForm()

    confirm = False
    qs = Post.objects.filter(author = profile)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True

    # if 'submit_p_form' in request.POST:
    p_form = PostModelForm(request.POST , request.FILES)
    if p_form.is_valid():
        instance = p_form.save(commit=False)
        instance.author = profile
        instance.save()
        p_form = PostModelForm()

    context = {
        'profile' : profile,
        'form' : form,
        'confirm' : confirm,
        'qs' : qs,
        'p_form' : p_form,
    }
    
    return render(request, 'profiles/myprofile.html', context)

def invites_received_view(request):
    profile = Profile.objects.get(user = request.user)

    qs = Relationship.objects.invitations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results)==0:
        is_empty=True

    context={ 
        'qs': results,
        'is_empty': is_empty    
    }

    return render(request, 'profiles/my_invites.html', context)

def accept_invitation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk') 
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)

        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    
    return redirect('profiles:my-invites-view')

def reject_invitation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk') 
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()

    return redirect('profiles:my-invites-view')


def profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context={'qs':qs}

    return render(request, 'profiles/profile_list.html', context)

def invite_profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context={'qs':qs}

    return render(request, 'profiles/to_invite_list.html', context)


class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/profile_list.html'
    context_object_name = 'qs'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = User.objects.get(username__iexact = self.request.user)
        profile = Profile.objects.get(user=user)
        
        rel_r = Relationship.objects.filter(sender = profile)
        rel_s = Relationship.objects.filter(receiver = profile)
        rel_receiver = []
        rel_sender = []

        for item in rel_r:
            rel_receiver.append(item.receiver.user)

        for item in rel_s:
            rel_sender.append(item.sender.user)
        
        
        context["rel_receiver"]= rel_receiver
        context["rel_sender"]= rel_sender 
        context["is_empty"]= False
        

        if len(self.get_queryset())==0:
            context["is_empty"]= True

        return context

def send_invitation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profiles:all-profiles-view')


def remove_from_friends(request):

    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | Q(sender=receiver) & Q(receiver=sender))

        rel.delete()

        return redirect(request.META.get('HTTP_REFERER'))
 
    return redirect('profiles:my-profile-view')

