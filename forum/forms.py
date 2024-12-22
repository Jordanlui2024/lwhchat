from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import ForumModel, ReplyModel


class ForumForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].required = False
        self.fields['title'].widget.attrs['class']="form-control titleforuminput"

    class Meta:
        model = ForumModel
        fields = ('title', 'content')
        widgets = {
            'content': CKEditor5Widget(attrs={"class":"django_ckeditor_5"}, config_name="extends")
        }    

class RelyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].required = False
     

    class Meta:
        model = ReplyModel
        fields = ["content"]
        widgets = {
            'content': CKEditor5Widget(attrs={"class":"django_ckeditor_5"}, config_name="extends")
        }               