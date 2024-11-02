from django import forms
from .models import Parent, Child, TrialRequest

# Форма для модели Parent
class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent  # Модель, для которой создается форма
        # Поля, которые будут в форме
        fields = ['parent', 'full_name', 'age']
        # Виджеты (HTML-элементы) для каждого поля
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),  # class='form-control' для Bootstrap
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Остальные формы работают аналогично

class ChildForm(forms.ModelForm):
    """
    Форма для создания/редактирования данных ребенка
    """
    class Meta:
        model = Child
        fields = ['full_name', 'age', 'parent', 'groups']
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',  # Bootstrap стили
                    'placeholder': 'Введите ФИО ребенка'
                }
            ),
            'age': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите возраст',
                    'min': 5,  # Минимальный возраст
                    'max': 17  # Максимальный возраст
                }
            ),
            'parent': forms.Select(
                attrs={
                    'class': 'form-control select2'  # select2 для улучшенного выпадающего списка
                }
            ),
            'groups': forms.SelectMultiple(
                attrs={
                    'class': 'form-control select2-multiple'  # Мультивыбор групп
                }
            )
        }

    def clean_age(self):
        """
        Валидация возраста
        """
        age = self.cleaned_data.get('age')
        if age < 5:
            raise forms.ValidationError('Возраст не может быть меньше 5 лет')
        if age > 17:
            raise forms.ValidationError('Возраст не может быть больше 17 лет')
        return age

class TrialRequestForm(forms.ModelForm):
    """
    Форма для создания заявки на пробное занятие
    """
    # Дополнительное поле для согласия на обработку персональных данных
    agreement = forms.BooleanField(
        required=True,
        label='Согласие на обработку персональных данных',
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )
    )

    # Поле для выбора предпочтительного времени
    PREFERRED_TIME_CHOICES = [
        ('morning', 'Утро (9:00-12:00)'),
        ('afternoon', 'День (12:00-16:00)'),
        ('evening', 'Вечер (16:00-20:00)')
    ]

    preferred_time = forms.ChoiceField(
        choices=PREFERRED_TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Предпочтительное время'
    )

    class Meta:
        model = TrialRequest
        fields = [
            'parent_name',
            'phone_number',
            'child_name',
            'child_age',
            'preferred_time'
        ]
        widgets = {
            'parent_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите ФИО родителя'
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+7 (___) ___-__-__',
                    'data-mask': '+7 (000) 000-00-00'  # Маска для телефона
                }
            ),
            'child_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите ФИО ребенка'
                }
            ),
            'child_age': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите возраст ребенка',
                    'min': 5,
                    'max': 17
                }
            )
        }

    def clean_phone_number(self):
        """Валидация номера телефона"""
        phone = self.cleaned_data.get('phone_number')
        # Убираем все символы кроме цифр
        phone = ''.join(filter(str.isdigit, phone))

        if len(phone) != 11:
            raise forms.ValidationError('Неверный формат номера телефона')

        return phone

    def clean(self):
        """Общая валидация формы        """
        cleaned_data = super().clean()
        child_age = cleaned_data.get('child_age')

        if child_age:
            if child_age < 5:
                self.add_error('child_age', 'Возраст не может быть меньше 5 лет')
            elif child_age > 17:
                self.add_error('child_age', 'Возраст не может быть больше 17 лет')

        return cleaned_data