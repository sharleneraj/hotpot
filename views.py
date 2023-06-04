from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection, transaction
from .forms import FoodForm,CustForm,AdminForm,CartForm,OrderForm,OrderFormDate
from .models import Food,Cust,Admin,Cart,Order
import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator


cursor = connection.cursor()

# Create your views here.

def foodapp(request):
	return render(request,'home.html')

def addfood(request):
	if request.method=="POST":
		form = FoodForm(request.POST,request.FILES)
		if form.is_valid():
			try:
				form.save()
				return redirect("/allfood")
			except:
				return render(request,"error.html")
	else :
		form = FoodForm()
	return render(request,'addfood.html',{'form':form})



def showfood(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        foods = Food.objects.filter(category=category)
    else:
        foods = Food.objects.all()

    paginator = Paginator(foods, 10)  # Change the number '10' to the desired number of items per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'searched_foods': page_obj,  # Pass the paginated foods as 'searched_foods'
        'foodlist': foods,  # Pass the unpaginated foods as 'foodlist'
    }

    return render(request, 'foodlist.html', context)


def deletefood(request,FoodId):
	foods = Food.objects.get(FoodId=FoodId)
	foods.delete()
	return redirect("/allfood")
	
def getfood(request,FoodId):
	foods = Food.objects.get(FoodId=FoodId)
	return render(request,'updatefood.html',{'f':foods})
	
def updatefood(request,FoodId):
	foods = Food.objects.get(FoodId=FoodId)
	form = FoodForm(request.POST,request.FILES,instance=foods)
	if form.is_valid():
		form.save()
		return redirect("/allfood")
	return render(request,'updatefood.html',{'f':foods})
	
def addcust(request):
	if request.method=="POST":
		form = CustForm(request.POST)
		if form.is_valid():
			try:
				form.save()
				return redirect("/login")
			except:
				return render(request,"error.html")
	else :
		form = CustForm()
	return render(request,'addcust.html',{'form':form})
	

def showcust(request):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()  # Convert the selected date to a datetime object
        orders = Cust.objects.filter(OrderDate__date=selected_date)
        print(orders)  # Debug statement
        return render(request, 'orders.html', {'orders': orders, 'selected_date': selected_date})
    else:
        return render(request, 'orders.html')


def customer_orders(request, CustId):
    customer = Cust.objects.get(CustId=CustId)
    orders = customer.order_set.all()
    return render(request, 'customer_details.html', {'customer': customer, 'orders': orders})
def all_orders(request):
    orders = Order.objects.all()

    context = {
        'orders': orders
    }
    return render(request, 'all_orders.html', context)
def deletecust(request,CustId):
	custs = Cust.objects.get(CustId=CustId)
	custs.delete()
	return redirect("/allcustomer")
	
def getcust(request):
	print(request.session['CustId'])
	for c in Cust.objects.raw('Select * from FP_Cust where CustEmail="%s"'%request.session['CustId']):
		custs=c
	return render(request,'updatecust.html',{'c':custs})
	
def updatecust(request,CustId):
	custs = Cust.objects.get(CustId=CustId)
	form = CustForm(request.POST,instance=custs)
	if form.is_valid():
		form.save()
		session_keys = list(request.session.keys())
		for key in session_keys:
			del request.session[key]
		return redirect("/login")
	return render(request,'updatecust.html',{'c':custs})
	
def search_food(request):
    query = request.GET.get('query')  # Get the search query from the request
    searched_foods = []

    if query:
        # Perform the search query on the database
        searched_foods = Food.objects.filter(FoodName__icontains=query)
        if not searched_foods:
            searched_foods = Food.objects.filter(FoodCat__icontains=query)

    foodlist = Food.objects.all()  # Retrieve all food items

    context = {
        'searched_foods': searched_foods,
        'foodlist': foodlist,
    }

    return render(request, 'foodlist.html', context)

	
def login(request):
	return render(request,'login.html')

def doLogin(request):
    if request.method == "POST":
        uid = request.POST.get('userId', '')
        upass = request.POST.get('userpass', '')
        utype = request.POST.get('utype', '')  # Updated this line

        if utype == "Admin":
            for a in Admin.objects.raw('Select * from FP_Admin where AdminId="%s" and AdminPass="%s"' % (uid, upass)):
                if a.AdminId == uid:
                    request.session['AdminId'] = uid
                    return render(request, "home.html", {'success': 'Welcome ' + a.AdminId})
            else:
                return render(request, "login.html", {'failure': 'Incorrect login details'})

        if utype == "User":
            for a in Cust.objects.raw('Select * from FP_Cust where CustEmail="%s" and CustPass="%s"' % (uid, upass)):
                if a.CustEmail == uid:
                    request.session['CustId'] = uid
                    return render(request, "home.html", {'success': 'Welcome ' + a.CustEmail})
            else:
                return render(request, "login.html", {'failure': 'Incorrect login details'})

    return render(request, "login.html", {'failure': 'Invalid user type'})


def doLogout(request):
	key_session = list(request.session.keys())
	for key in key_session:
		del request.session[key]
	return render(request,'home.html',{'success':'Logged out successfully'})
	
def addcart(request,FoodId):
	sql = ' Insert into FP_Cart(CustEmail,FoodId,FoodQuant) values("%s","%d","%d")'%(request.session['CustId'],FoodId,1)
	i=cursor.execute(sql)
	transaction.commit()
	return redirect('/allfood')
	
def delcart(request,CartId):
	cart = Cart.objects.get(CartId=CartId)
	cart.delete()
	return redirect("/allcart")
	
def showcart(request):
	cart=Cart.objects.raw('Select CartId,FoodName,FoodPrice,FoodQuant,FoodImage from FP_Food as f inner join FP_Cart as c on f.FoodId=c.FoodId where c.CustEmail="%s"'%request.session['CustId'])
	transaction.commit()
	return render(request,"cartlist.html",{'cartlist':cart})
	
def updatepasswd(request):
	return render(request,'updatepasswd.html')
		
def changepass(request):
	if request.method == "POST":
		aid=request.session['AdminId']
		opss=request.POST.get('OLDPass','')
		newpss=request.POST.get('NEWPass','')
		cnewpss=request.POST.get('CONFPass','')
		for a in Admin.objects.raw('select * from FP_Admin where AdminId="%s" and AdminPass="%s"'%(aid,opss)):
			if a.AdminId == aid:
				sql = 'update FP_Admin set AdminPass="%s" where AdminId="%s"' %(newpss,request.session['AdminId'])
				i=cursor.execute(sql)
				transaction.commit()
				session_keys = list(request.session.keys())
				for key in session_keys:
					del request.session[key]
				return redirect("/login")
		else:
			return render(request,'updatepasswd.html',{'failure':'Invalid attempt.'})

def placeorder(request):
        if request.method=="POST":
                price=request.POST.getlist('FoodPrice','')
                q=request.POST.getlist('FoodQuant','')
                total=0.0
                for i in range(len(price)):
                    total=total+float(price[i])*float(q[i])
                today = datetime.datetime.now()
                sql = 'insert into FP_Order(CustEmail,OrderDate,TotalBill) values ("%s","%s","%f")' %(request.session['CustId'],today,total)
                i=cursor.execute(sql)
                transaction.commit()
                sql1= 'select * from FP_Order where CustEmail="%s" and OrderDate="%s"'%(request.session['CustId'],today)
                sql = 'delete from FP_Cart where CustEmail="%s"' %(request.session['CustId'])
                i=cursor.execute(sql)
                transaction.commit()
                
                od=Order()
                
                for o in Order.objects.raw(sql1):
                        if o.CustEmail==request.session['CustId']:
                                od=str(o.OrderId)
                                return render(request,'home.html',{'success':'Order placed sucessfully!!!'+str(o.OrderId)})
        else:
        	pass



@login_required  # Add this decorator to ensure the user is logged in
def getorder(request, customer_id):
	try:
		# Retrieve the logged-in user's customer object
		logged_in_customer = Cust.objects.get(CustEmail=request.user.email)

		# Check if the logged-in user is the owner of the requested customer_id
		if logged_in_customer.id == customer_id:
			# Retrieve the orders of the logged-in user
			orders = Order.objects.filter(customer=logged_in_customer)
			return render(request, "orderlist.html", {'orders': orders})
		else:
			return HttpResponse("Unauthorized access")
	except Cust.DoesNotExist:
		return HttpResponse("Customer does not exist")


def order_date(request):
	if request.method == "POST":
		form = OrderFormDate(request.POST)
		if form.is_valid():
			order_date = form.cleaned_data["order_date"]
			with connection.cursor() as cursor:
				cursor.execute("SELECT * FROM FP_Order WHERE OrderDate = %s", [order_date])
				orderlist = cursor.fetchall()

			return render(request, "all_orders.html", {"orderlist": orderlist})
	else:
		form = OrderFormDate()
	return render(request, "all_orders.html", {"form": form})


def updateQNT(request,s):
	print(s)
	ind=s.index('@')
	cartId=int(s[:ind])
	qt=int(s[ind+1:])
	sql="update FP_Cart set FoodQuant='%d' where CartId='%d'"%(qt,cartId)
	i=cursor.execute(sql)
	transaction.commit()


class CustomerDetailsView(TemplateView):
    template_name = 'customer_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data you need for the template
        return context


class CustomerOrdersByDateView(View):
    def get(self, request):
        selected_date = request.GET.get('selected_date')
        orders = Order.objects.filter(OrderDate=selected_date)
        customers = Cust.objects.filter(order__in=orders).distinct()
        context = {'selected_date': selected_date, 'customers': customers}
        return render(request, 'customer_orders_by_date.html', context)

    def post(self, request):
        selected_date = request.POST.get('selected_date')
        orders = Order.objects.filter(OrderDate=selected_date)
        customers = Cust.objects.filter(order__in=orders).distinct()
        context = {'selected_date': selected_date, 'customers': customers}
        return render(request, 'customer_orders_by_date.html', context)

    def get_orders(self, request, customer_id):
        customer = get_object_or_404(Cust, id=customer_id)
        orders = Order.objects.filter(customer=customer, OrderDate=self.selected_date)
        context = {'customer': customer, 'orders': orders}
        return render(request, 'orders.html', context)