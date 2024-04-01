from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


# Create your models here.

class ProfileManager(models.Manager):
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs= Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))

        accepted = set([])
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
        
        available = [profile for profile in profiles if profile not in accepted]
        
        return available
    
    def get_all_profiles(self,me):
        profiles = Profile.objects.all().exclude(user=me)

        return profiles


class Profile(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100,)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="No bio...", max_length=500)
    email =models.EmailField(max_length=50)
    country = models.CharField(max_length=50, blank=True)
    # to images we need to install pillow
    # we will only save path of the image not the actual image 
    # create media root folder for images
    avatar = models.ImageField(default="avatar.png", upload_to= "avatars/")
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    updated = models.DateTimeField(auto_now = True)
    created =models.DateTimeField(auto_now_add=True)
    objects = ProfileManager()

    def get_friends(self):
        return self.friends.all()
    
    def get_friends_no(self):
        return self.friends.all().count()
    
    # we have given 'posts' as related name in authors field of 'post model' so we can retriev data of author in another model using 'related_name'
    def get_posts_no(self):
        return self.posts.all().count()
    
    def get_all_authors_posts(self):
        return self.posts.all()
    
   
    def __str__(self):
        return f"{self.user.username}-{self.created.strftime('%d-%m-%y')}"



STATUS_CHOICES = {
    ('send', 'send'),
    ('accepted', 'accepted')
}

class RelationshipManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES) 
    updated = models.DateTimeField(auto_now = True)
    created =models.DateTimeField(auto_now_add=True) 

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
