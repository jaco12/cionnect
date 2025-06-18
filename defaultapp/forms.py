from django import forms
from .models import Group, File, Task, Profile, Message

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 
                  'description']

class GroupEditForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 
                  'description']

class UploadFileForm(forms.ModelForm):
    keywords = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter keywords separated by commas'})
    )
    class Meta:
        model = File
        fields = ['upload', 
                  'filename',
                  'description', 
                  'keywords']

    def clean_keywords(self):
        keywords = self.cleaned_data['keywords']
        # Convert the comma-separated input into a list of keywords
        return [kw.strip() for kw in keywords.split(',') if kw.strip()]
    
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'completed',]
        widgets = {
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class NicknameForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname']
        widgets = {
            'nickname': forms.TextInput(attrs={'placeholder': 'Enter your nickname'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'message']