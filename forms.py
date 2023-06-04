from django import forms
from .models import Admin,Food,Cust,Cart,Order

class FoodForm(forms.ModelForm):
	class Meta:
		model = Food
		fields  = "__all__"
		
class CustForm(forms.ModelForm):
	class Meta:
		model = Cust
		fields  = "__all__"
		
class AdminForm(forms.ModelForm):
	class Meta:
		model = Admin
		fields  = "__all__"		
		
class CartForm(forms.ModelForm):
	class Meta:
		model = Cart
		fields  = "__all__"		
		
class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields  = "__all__"

class OrderFormDate(forms.ModelForm):
    order_date = forms.DateField(label='Order Date', widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Order
        fields = "__all__"

class DateForm(forms.Form):
    selected_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))



