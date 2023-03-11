from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            "text": "Текст на русском",
            "group": "Группа на русском",
        }
        help_texts = {
            "text": "Указывает текст",
            "group": "Указывает название группы",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
