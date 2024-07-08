from django import forms
from django.forms import ModelForm
from echoverse.models import Articles, ArticleImage, Comments, SavesModel


class ArticleForm(ModelForm):
	class Meta:
		model = Articles
		fields = ('title', 'content', 'category')
		
class ImageForm(ModelForm):
	class Meta:
		model = ArticleImage
		fields = ('image',)
		
		
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content', 'post', 'author', 'parent']

class SavesForm(forms.ModelForm):
    class Meta:
        model = SavesModel
        fields = ['article', 'user']