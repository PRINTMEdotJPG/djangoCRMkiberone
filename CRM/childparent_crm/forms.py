from django import forms
from .models import Parent, Child, TrialRequest, ParentComment

# Форма для модели Parent

class ParentCommentInlineForm(forms.ModelForm):
   class Meta:
       model = ParentComment
       fields = ['text']
       labels = {
           'text': '',  # Убираем метку поля 'text'
       }
       widgets = {
           'text': forms.Textarea(attrs={
               'rows': 3,  # Количество строк в текстовом поле
               'cols': 60,  # Ширина текстового поля
           }),
       }

from django import forms
class WhatsAppMessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 4, 'cols': 50}), # Создаем поле для ввода текста
            label='Сообщение', # Подпись над полем
            initial='Здравствуйте!' # Начальный текст в поле
            )