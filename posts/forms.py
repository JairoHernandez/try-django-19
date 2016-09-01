from django import forms
from .models import Post

class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = [ 
			"title", 
			"content", 
			"image", # From video "File Uploads with FileField & ImageField"
			"draft",
			"publish",
		] # These fields are internal to ModelForm and must be exact.

		 
