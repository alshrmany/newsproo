from django import forms




class ContactForm(forms.Form):
        name = forms.CharField(max_length=100)
        email = forms.EmailField()
        message = forms.CharField(widget=forms.Textarea)

class SimpleSearchForm(forms.Form):
    
    q = forms.CharField(
        label='كلمة البحث',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اكتب كلمة البحث هنا...',
            'style': 'width: 300px;'
        }),
        help_text='اكتب كلمة أو جملة للبحث في عناوين ومحتوى المقالات'
    )