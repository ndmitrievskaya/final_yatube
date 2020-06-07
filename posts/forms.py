from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].required = False

    class Meta:
        model = Post
        fields = ['group', 'text']
