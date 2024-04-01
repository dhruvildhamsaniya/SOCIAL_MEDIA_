from django.shortcuts import render,redirect
from .models import Post,Like
from profiles.models import Profile
from .forms import CommentModelForm
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
# Create your views here.


def post_comment_create_and_list_view(request):
    
    profile = Profile.objects.get(user = request.user)
    qs = Post.objects.filter(author=profile)
    c_form = CommentModelForm()

    if 'submit_c_form' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id = request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()

    context={
        'qs' : qs,
        'profile' : profile,
        'c_form' : c_form,
    }

    return render(request,'posts/main.html' , context)

def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            post_obj.liked.add(profile)

        like, created = Like.objects.get_or_create(user=profile, post_id=post_id)

        if not created:
            if like.value == 'like':
                like.value = 'unlike'
            else:
                like.value= 'like'
            
        else:
            like.value = 'like'

            post_obj.save()
            like.save()

    return redirect('posts:main-post-view')


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/confirm_del.html'
    success_url = reverse_lazy('posts:main-post-view')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)

        if not obj.author.user == self.request.user:
            messages.warning(self.request, 'you need to be the author of the post in order to delete the post')
        
        return obj