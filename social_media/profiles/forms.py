from django import forms
from .models import Profile


class ProfileModelForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'bio', 'avatar')




