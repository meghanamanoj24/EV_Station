from django.shortcuts import render,redirect
from . models import reg,service_reg,feed,station,service,pay,super_user

# Create your views here.

from django.utils.timezone import make_aware
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import pay
from django.utils.timezone import make_aware
import razorpay

import random
import smtplib
import razorpay #import this
from django.conf import settings
from django.http import JsonResponse #import this
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt #import this
from django.http import HttpResponseBadRequest #import this
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def index(request):
    return render(request,'index.html')

# user views

def home(request):
    return render(request,'home.html')


def register(request):
   if request.method =='POST':
      fname = request.POST.get('rfname')
      phone = request.POST.get('rcontact')
      email = request.POST.get('remail')
      uname = request.POST.get('runame')
      passw = request.POST.get('rpass')
      reg(fullname=fname,contact=phone,email=email,username=uname,password=passw).save()
      return render(request,'login.html')
   else:
      return render(request,'register.html')


def login(request):
   if request.method=='POST':
      uname = request.POST.get('runame')
      passw = request.POST.get('rpass')
      cr = reg.objects.filter(username=uname,password=passw)
      if cr:
         details = reg.objects.get(username=uname, password = passw)
         username = details.username
         request.session['cs']=username

         return render(request,'home.html')
      else:
         message="Invalid Username Or Password"
         return render(request,'login.html',{'me':message})
   else: 
      return render(request,'login.html')

def profile(request):
    c = request.session.get('cs')  # Use get() to avoid KeyError if not exists
    if not c:
        return redirect('login')  # Redirect if not logged in
    
    try:
        # Use filter() instead of get() and take the first result
        cr = reg.objects.filter(username=c).first()
        if not cr:
            messages.error(request, 'User not found')
            return redirect('login')
        
        pfname = cr.fullname
        pcontact = cr.contact
        pemail = cr.email
        return render(request, 'profile.html', {
            'name': pfname,
            'contact': pcontact,
            'email': pemail
        })
    except Exception as e:
        messages.error(request, f'Error accessing profile: {str(e)}')
        return redirect('login')
    

def tutorial(request):
    return render(request,'tutorial.html')
 
 
# service views


def ser_home(request):
    return render(request,'ser_home.html')


def ser_register(request):
   if request.method =='POST':
      lino = request.POST.get('rlino')
      fname = request.POST.get('rfname')
      phone = request.POST.get('rcontact')
      email = request.POST.get('remail')
      location = request.POST.get('rlocation')
      uname = request.POST.get('runame')
      passw = request.POST.get('rpass')
      service_reg(license_no=lino,fullname=fname,contact=phone,email=email,location=location,username=uname,password=passw).save()
      return render(request,'ser_login.html')
   else:
      return render(request,'ser_register.html')


def ser_login(request):
   if request.method=='POST':
      lino =  request.POST.get('rlino')
      uname = request.POST.get('runame')
      passw = request.POST.get('rpass')
      cr = service_reg.objects.filter(license_no=lino,username=uname,password=passw)
      if cr:
         details = service_reg.objects.get(username=uname, password = passw,license_no=lino)
         username = details.username
         request.session['cs']=username
         lino = details.license_no
         request.session['lcu']=lino
         
         return render(request,'ser_home.html')
      else:
         message="Invalid Username Or Password"
         return render(request,'ser_login.html',{'me':message})
   else: 
      return render(request,'ser_login.html')


def ser_profile(request):
   c=request.session['lcu']
   cr=service_reg.objects.get(license_no=c)
   plino=cr.license_no
   pfname=cr.fullname
   pcontact=cr.contact
   pemail=cr.email
   plocation=cr.location
   return render(request,'ser_profile.html',{'lino':plino,'name':pfname,'contact':pcontact,'email':pemail,'location':plocation})
 

def feedback(request):
   fname=request.session['cs']
   if request.method =='POST':
      phone = request.POST.get('fphone')
      email = request.POST.get('fmail')
      msg = request.POST.get('fmsg')
      feed(fullname=fname,phone=phone,email=email,message=msg).save()
      return render(request,'home.html')
   else:
      return render(request,'feedback.html',{'fname':fname})
   
   
# stations view


def stations(request):
    data=station.objects.all()
    return render(request,'stations.html',{'data':data})
 
 
def add_station(request):
   lino=request.session['lcu']
   if request.method =='POST':
      fname = request.POST.get('rfname')
      time = request.POST.get('rtime')
      location = request.POST.get('rlocation')
      contact = request.POST.get('rcontact')
      speed = request.POST.get('rspeed')
      price = request.POST.get('rprice')
      status = request.POST.get('rstatus')
      station(license_no=lino,name=fname,time=time,location=location,contact=contact,speed=speed,price=price,status=status).save()
      return render(request,'ser_home.html')
   else:
      return render(request,'add_station.html',{'lino':lino})


# services view 


def services(request):
    data=service.objects.all()
    return render(request,'services.html',{'data':data})
 
 
def add_service(request):
   lino=request.session['lcu'] 
   if request.method =='POST':
      fname = request.POST.get('rfname')
      time = request.POST.get('rtime')
      location = request.POST.get('rlocation')
      price = request.POST.get('rprice')
      contact = request.POST.get('rcontact')
      status = request.POST.get('rstatus')
      service(license_no=lino,name=fname,time=time,location=location,price=price,contact=contact,status=status).save()
      return render(request,'ser_home.html')
   else:
      return render(request,'add_service.html',{'lino':lino})


# station  payment view



def payment(request, id):
    if request.method == 'POST':
        selected_time = request.POST.get('time')
        
        # Convert string time to datetime object
        try:
            booking_time = make_aware(datetime.datetime.strptime(selected_time, '%Y-%m-%dT%H:%M'))
        except:
            booking_time = datetime.datetime.now()  # fallback to current time
        
        c = request.session['cs']
        sr = reg.objects.get(username=c)
        cr = station.objects.get(id=id)
        lino = cr.license_no
        pname = cr.name
        ploc = cr.location
        price = cr.price
        pfname = sr.fullname
        pcon = sr.contact 
        pmail = sr.email
        
        amount = int(float(price) * 100)

        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency='INR',
            payment_capture='0'
        ))

        request.session['temp_booking'] = {
            'license_no': lino,
            'fullname': pfname,
            'contact': pcon,
            'email': pmail,
            'name': pname,
            'time': booking_time.isoformat(),  # Now a datetime object
            'location': ploc,
            'amount': price,
            'order_id': razorpay_order['id']
        }

        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': settings.RAZOR_KEY_ID,
            'razorpay_amount': amount,
            'amount_in_rupees': float(price),
            'currency': 'INR',
            'callback_url': '/paymenthandler/',
            'user_fullname': pfname,
            'user_email': pmail,
            'user_contact': pcon,
            'station_name': pname,
            'booking_time': selected_time  # Original string for display
        }
        
        return render(request, 'payment.html', context)




@csrf_exempt
def paymenthandler(request):
    if request.method in ["POST", "GET"]:
        try:
            payment_id = request.POST.get('razorpay_payment_id') or request.GET.get('payment_id')
            order_id = request.POST.get('razorpay_order_id') or request.GET.get('order_id')
            signature = request.POST.get('razorpay_signature') or request.GET.get('signature')
            
            if not all([payment_id, order_id, signature]):
                return render(request, 'pay_failed.html')
            
            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Fetch booking details from session
            temp_booking = request.session.get('temp_booking')
            if not temp_booking:
                return render(request, 'pay_failed.html')

            # Save booking details to database
            booking = pay(
                license_no=temp_booking['license_no'],
                fullname=temp_booking['fullname'],
                contact=temp_booking['contact'],
                email=temp_booking['email'],
                name=temp_booking['name'],
                location=temp_booking['location'],
                amount=temp_booking['amount'],
                time=make_aware(datetime.datetime.fromisoformat(temp_booking['time']))
            )
            booking.save()
            
            # After saving, delete temp session
            del request.session['temp_booking']

            return render(request, 'pay_success.html', {
                'booking_id': f"EV-{booking.id}",
                'station_name': booking.name,
                'station_location': booking.location,
                'booking_date': booking.time.strftime('%Y-%m-%d'),
                'booking_time': booking.time.strftime('%H:%M'),
                'duration': 45,  # assuming fixed 45 minutes
                'amount': booking.amount,
                'user_fullname': booking.fullname,
                'user_contact': booking.contact
            })

        except razorpay.errors.SignatureVerificationError:
            return render(request, 'pay_failed.html')
        except Exception as e:
            print(f"Payment processing failed: {str(e)}")
            return render(request, 'pay_failed.html')
    else:
        return redirect('/')



def payments(request,id):
 
 
    c = request.session['cs']
    sr = reg.objects.get(username=c)
    cr = service.objects.get(id=id)
    lino = cr.license_no
    pname = cr.name
    ptime = cr.time
    ploc = cr.location
    price = cr.price
    pfname = sr.fullname
    pcon = sr.contact 
    pmail = sr.email
    totalprice = 0
    e = int(price)
    totalprice = int(e*100)
    pay(license_no=lino,fullname=pfname,contact=pcon,email=pmail,name=pname,time=ptime,location=ploc,amount=price).save()
    print(totalprice)
    
         
# creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
 
# start TLS for security
    s.starttls()
 
# Authentication
    s.login("nefsal003@gmail.com", "htxalvzrrkxupspv")
 
# message to be sent
    number = random.randint(10000,1000000)
    msg = str(number)
    message = f"Your Service Booked Successfully , Your Onetime Code Is {msg}"
# sending the mail
    s.sendmail("nefsal003@gmail.com", pmail, message)
 
# terminating the session
    s.quit()   
    
    
    
    amount=int(totalprice)
    #amount=200
    print('amount is',str(amount))
    currency = 'INR'
    #amount = 20000  # Rs. 200

    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
 
    return render(request, 'payments.html', context=context)



# admin views

def admin_home(request):
    return render(request,'admin_home.html')

def admin_reg(request):
   if request.method =='POST':
      uname = request.POST.get('runame')
      passw = request.POST.get('rpass')
      super_user(username=uname,password=passw).save()
      return render(request,'admin_login.html')
   else:
      return render(request,'admin_reg.html')


def admin_login(request):
   if request.method=='POST':
      uname = request.POST.get('runame')
      passw = request.POST.get('rpass')
      print(uname)
      print(passw)
      cr = super_user.objects.filter(username=uname,password=passw)
      if cr:
         details = super_user.objects.get(username=uname, password = passw)
         username = details.username
         request.session['cs']=username

         return render(request,'admin_home.html')
      else:
         message="Invalid Username Or Password"
         return render(request,'admin_login.html',{'me':message})
   else: 
      return render(request,'admin_login.html')

# booking views

def bookings(request):
    c = request.session.get('cs')
    values = pay.objects.filter(fullname=c)
    return render(request, 'bookings.html', {'values': values})
 
# orders views

def orders(request):
   lcu = request.session.get('lcu')
   values = pay.objects.filter(license_no=lcu)
   return render(request, 'orders.html', {'values': values})





# users list view

def users_list(request):
    data=reg.objects.all()
    return render(request,'users_list.html',{'data':data})


def delete_record1(request,id):
    data=reg.objects.get(id=id)
    data.delete()
    return render(request,'admin_home.html')



def stations_list(request):
    data=station.objects.all()
    return render(request,'stations_list.html',{'data':data})


def delete_record2(request,id):
    data=station.objects.get(id=id)
    data.delete()
    return render(request,'admin_home.html')


def services_list(request):
    data=service.objects.all()
    return render(request,'services_list.html',{'data':data})


def delete_record3(request,id):
    data=service.objects.get(id=id)
    data.delete()
    return render(request,'admin_home.html')

def feedback_list(request):
    data=feed.objects.all()
    return render(request,'feedback_list.html',{'data':data})


def delete_record4(request,id):
    data=feed.objects.get(id=id)
    data.delete()
    return render(request,'admin_home.html')

def payment_list(request):
    data=pay.objects.all()
    return render(request,'payments_list.html',{'data':data})


def delete_record5(request,id):
    data=pay.objects.get(id=id)
    data.delete()
    return render(request,'admin_home.html')


def view_stations(request):
    license_no = request.session.get('lcu')
    stations = station.objects.filter(license_no=license_no)
    return render(request, 'view_station.html', {'stations': stations})

def delete_station(request,id):
    data=station.objects.get(id=id)
    data.delete()
    return render(request,'ser_home.html')

def view_services(request):
    license_no = request.session.get('lcu')
    services = service.objects.filter(license_no=license_no)
    return render(request, 'view_service.html', {'services': services})

def delete_service(request,id):
    data=service.objects.get(id=id)
    data.delete()
    return render(request,'ser_home.html')


def reviews(request):
   lcu = request.session.get('lcu')
   values = feed.objects.filter(phone=lcu)
   return render(request, 'reviews.html', {'data': values})


def stations_search(request):
    if request.method=='POST':
        search=request.POST.get('search')
        data= station.objects.filter(location=search)
        return render(request,'stations.html',{'data':data})

   
def services_search(request):
    if request.method=='POST':
        search=request.POST.get('search')
        data= service.objects.filter(location=search)
        return render(request,'services.html',{'data':data})
    
def update_status(request):
    if request.method == 'POST':
        lino = request.POST.get('lino')
        print(lino)
        status = request.POST.get('status')
        dt=station.objects.get(license_no=lino)
        dt.status = status
        dt.save()
        return redirect('view_stations') 
    
def update_service(request):
    if request.method == 'POST':
        lino = request.POST.get('lino')
        print(lino)
        status = request.POST.get('status')
        dt=service.objects.get(license_no=lino)
        dt.status = status
        dt.save()
        return redirect('view_services') 
    

import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .models import reg, service_reg  # Import your custom models

# Store OTPs temporarily (in production, use cache/database)
otp_storage = {}

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Check both regular users and service providers
        user = None
        try:
            user = reg.objects.get(email=email)
        except reg.DoesNotExist:
            try:
                user = service_reg.objects.get(email=email)
            except service_reg.DoesNotExist:
                messages.error(request, 'No user found with this email address')
                return render(request, 'password_reset.html')
        
        if user:
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            otp_storage[email] = otp
            
            # Send OTP via email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['reset_email'] = email  # Store email in session for verification
            return redirect('verify_otp')
            
    return render(request, 'password_reset.html')

def verify_otp(request):
    if 'reset_email' not in request.session:
        return redirect('password_reset')
    
    email = request.session['reset_email']
    
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        
        if email in otp_storage and otp_storage[email] == user_otp:
            del otp_storage[email]  # Remove used OTP
            return redirect('password_reset_change')
        else:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'verify_otp.html', {'email': email})

def password_reset_change(request):
    if 'reset_email' not in request.session:
        return redirect('password_reset')
    
    email = request.session['reset_email']
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            # Check both models and update password
            updated = False
            try:
                user = reg.objects.get(email=email)
                user.password = password
                user.save()
                updated = True
            except reg.DoesNotExist:
                try:
                    user = service_reg.objects.get(email=email)
                    user.password = password
                    user.save()
                    updated = True
                except service_reg.DoesNotExist:
                    messages.error(request, 'User not found')
            
            if updated:
                del request.session['reset_email']
                return redirect('password_reset_complete')
        else:
            messages.error(request, 'Passwords do not match')
    
    return render(request, 'password_reset_change.html')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')