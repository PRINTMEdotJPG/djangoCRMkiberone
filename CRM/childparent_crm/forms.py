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