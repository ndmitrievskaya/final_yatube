from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].required = False

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'group': 'Группа, в которой будет опубликован пост',
            'text': 'Текст поста'
        }
        labels = {
            'group': 'Группа',
            'text': 'Текст',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        help_texts = {'text': 'Текст комментария'}
        labels = {'text': 'Текст'}
