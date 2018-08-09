from django import forms

class UploadForm(forms.Form):
    """
    A basic django form which allows the user to upload a .msg file
    """
    file_name = forms.CharField(label='File Name', max_length=50, required=False,  widget=forms.TextInput(
        attrs={
            'id': 'txtFileName',
            'placeholder': 'File Name (optional)'
        }
    ))
    msg_file = forms.FileField()
