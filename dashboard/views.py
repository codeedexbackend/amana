from django.shortcuts import render, redirect,get_object_or_404

# from tailors.models import AddCustomer
from .models import AddTailors,Customer,Order,Item
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
import pdfkit
from xhtml2pdf import pisa
from django.views import View
from .forms import TailorForm  
from datetime import date
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import UpdateAPIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.http import HttpResponseServerError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from .serializers import TailorLoginSerializer,CustomerSerializer,CompletedCustomerSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib import messages
from rest_framework.decorators import api_view


class TailorLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TailorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        print(f"Attempting to authenticate user: {username}")

        user = authenticate(request, username=username, password=password)

        try:
            user = AddTailors.objects.get(username=username)
        except AddTailors.DoesNotExist:
            user = None

        if user:
            print(f"Authentication successful for user: {username}")
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            response_data = {
                'message': 'Authentication successful',
                'status': True,
                'token': token,
                'user_id': user.id,
                'username': user.username,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            print(f"Authentication failed for user: {username}")
            response_data = {
                'error': 'Invalid credentials',
                'status': False,
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


class CustomerListAPIView(ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, status='assigned')

    def perform_create(self, serializer):
        tailor_id = self.kwargs['tailor_id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        serializer.save(tailor=tailor, status='assigned')


class InProgressCustomerUpdateAPIView(UpdateAPIView):
    serializer_class = CustomerSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, id=customer_id, status='assigned')

    def perform_update(self, serializer):
        serializer.save(status='in_progress')

        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']

        tailor = get_object_or_404(AddTailors, id=tailor_id)

        if tailor.assigned_works > 0:
            tailor.assigned_works -= 1
            tailor.save()

        tailor.pending_works += 1
        tailor.save()

        return Response({'status': True}, status=status.HTTP_200_OK)


class InProgressToCompletedAPIView(UpdateAPIView):
    serializer_class = CustomerSerializer
    lookup_field = 'id'

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, id=customer_id, status='in_progress')

    def perform_update(self, serializer):
        serializer.save(status='completed')

        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['id']

        tailor = get_object_or_404(AddTailors, id=tailor_id)

        tailor.pending_works -= 1
        tailor.save()

        tailor.completed_works += 1
        tailor.save()

        return Response({'status': True}, status=status.HTTP_200_OK)


class InProgressCustomerListAPIView(ListAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return Customer.objects.filter(tailor=tailor, status='in_progress')


class CustomerDetailAPIView(RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_object(self):
        tailor_id = self.kwargs['tailor_id']
        customer_id = self.kwargs['pk']
        tailor = get_object_or_404(AddTailors, id=tailor_id)
        return get_object_or_404(Customer, pk=customer_id, tailor=tailor)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        status_changed = False
        

        if 'status' in serializer.validated_data:
            current_status = self.get_object().status
            new_status = serializer.validated_data['status']

            if current_status != new_status:
                status_changed = True
                serializer.save(status=new_status)


        response_data = {
            'status_changed': status_changed,
            'status': True,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CompletedCustomerListAPIView(ListAPIView):
    serializer_class = CompletedCustomerSerializer

    def get_queryset(self):
        tailor_id = self.kwargs['tailor_id']
        return Customer.objects.filter(tailor_id=tailor_id, status='completed')
    
def indexpage(request):
    return render(request,"dashboard.html")

def createcustomer(request):
    tailor = AddTailors.objects.all()
    tailor_works = []
    for tailor in tailor:
        assigned_works = Customer.objects.filter(tailor=tailor, status='assigned').count()
        pending_works = tailor.pending_works  # Assuming you have a pending_works field in AddTailors
        tailor_works.append({'tailor': tailor, 'assigned_works': assigned_works, 'pending_works': pending_works})

    context = {'tailor_works': tailor_works}
    return render(request, 'Create_customer.html', context)

def addtailors(request):
    return render(request,"Add_tailor.html")

def save_tailor(request):
    if request.method == "POST":
        tn = request.POST.get('tname')
        un = request.POST.get('username')
        pwd = request.POST.get('password')
        mob = request.POST.get('mobile')
        obj = AddTailors(tailor=tn,username=un,password=pwd,mobile_number=mob)
        obj.save()
        messages.success(request, "Tailor Added Successfully")
    return redirect(addtailors)
    

def view_tailors(request):
    return render(request,"View_Tailor.html")

def tailor_details(request):
    tailors = AddTailors.objects.all()

    for tailor in tailors:
        # Calculate assigned, pending, upcoming, and completed works
        tailor.assigned_works = Customer.objects.filter(tailor=tailor, status='assigned').count()
        tailor.pending_works = Customer.objects.filter(tailor=tailor, status='in_progress').count()
        tailor.upcoming_works = Customer.objects.filter(tailor=tailor, delivery_date__gt=date.today()).count()
        tailor.completed_works = Customer.objects.filter(tailor=tailor, status='completed').count()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor.html', context)



def additems(request):
    customers = Customer.objects.all()
    return render(request,"Add_items.html",{"customers":customers})


def save_items(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customerName')

        customers = Customer.objects.filter(name=customer_name)

        if customers.exists():
            customer = customers.first()
        else:
            customer = Customer.objects.create(name=customer_name)

        item_names = request.POST.getlist('itemName[]')
        quantities = request.POST.getlist('quantity[]')
        prices = request.POST.getlist('price[]')

        for i in range(len(item_names)):
            if i < len(quantities) and i < len(prices):
                item = Item(
                    customer=customer,
                    item_name=item_names[i],
                    item_quantity=int(quantities[i]),
                    item_price=float(prices[i])
                )
                item.save()
            else:
                print(f"Skipping item at index {i} due to incomplete data.")

        return redirect('additems')

    customers = Customer.objects.all()
    return render(request, 'Add_Items.html', {'customers': customers})


def customer_details(request):
    cus = Customer.objects.all()
    return render(request,"Customer_Details.html",{"cus":cus})

def order_details(request):
    cus = Customer.objects.all()
    return render(request,"Order_Details.html",{"cus":cus})

def upcoming_deliveries(request):
    cus = Customer.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    # Add tailor_name to each customer in cus
    # for customer in cus:
    #     customer.tailor.name = customer.tailor.tailor if customer.tailor else 'No Tailor'

    return render(request, 'dashboard.html', {'cus': cus})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, AddTailors
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import os


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    # Create a PDF file
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def savecustomer(request):
    if request.method == "POST":
        # Your existing form processing logic
        nm = request.POST.get('name')
        mn = request.POST.get('mobile')
        ln = request.POST.get('length')
        sd = request.POST.get('shoulder')
        sl = request.POST.get('sleeve')
        sll = request.POST.get('sleeve_length')
        nc = request.POST.get('neck')
        wr = request.POST.get('wrist')
        ncr = request.POST.get('neck_round')
        clr = request.POST.get('collar')
        rg = request.POST.get('regal')
        lo = request.POST.get('loose')
        po = request.POST.get('pocket')
        cl = request.POST.get('cuff_length')
        ct = request.POST.get('cuff_type')
        b1 = request.POST.get('bottom1')
        b2 = request.POST.get('bottom2')
        od = request.POST.get('order_date')
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')

        # Get or create the tailor instance
        tailor_instance, created = AddTailors.objects.get_or_create(id=tailor_id)

        # Update assigned_works for the selected tailor
        tailor_instance.assigned_works += 1
        tailor_instance.save()

        # Create the customer instance
        obj = Customer(name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg, cuff_length=cl,
                       cuff_type=ct, sleeve_type=sl, sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2, order_date=od,
                       delivery_date=dd, tailor=tailor_instance, button_type=bt, neck_round=ncr, wrist=wr, collar=clr)
        
        obj.save()

        # Fetch the customer instance with the generated bill_number
        customer_with_bill = Customer.objects.get(id=obj.id)

        messages.success(request, f"Successfully added customer: {obj.name}")

        return render(request, 'View_Tailor.html', {'customer': customer_with_bill})
    # Render your form template for GET requests
    return render(request, 'View_Tailor.html', context)

@api_view(['POST'])
def accept_work(request, tailor_id):
    tailor = get_object_or_404(AddTailors, id=tailor_id)
    
    # Update the pending works count
    tailor.pending_works += 1
    tailor.save()

    return Response({'status': 'Pending works updated successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def complete_work(request, tailor_id):
    tailor = get_object_or_404(AddTailors, id=tailor_id)

    # Update the pending and completed works counts
    if tailor.pending_works > 0:
        tailor.pending_works -= 1
        tailor.completed_works += 1
        tailor.save()
        return Response({'status': 'Work completed successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'No pending works to complete'}, status=status.HTTP_400_BAD_REQUEST)




def customerdlt(request,dlt):
    delt = Customer.objects.filter(id=dlt)
    delt.delete()
    return redirect(dashboard)







def dashboard(request):
    total_customers = Customer.objects.count()
    total_orders = Customer.objects.count() 
    cus = Customer.objects.all().order_by('delivery_date')
    context = {'total_customers': total_customers, 'total_orders': total_orders,'cus': cus}
    return render(request, 'dashboard.html', context)


def print_measurement(request, measurement_id):
    # Get the customer instance based on measurement_id
    measurement = Customer.objects.get(pk=measurement_id)
    context = {'measurement': measurement}

    template_path = 'Print_measurements.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=customer_{measurement.name}.pdf'

    # Provide the base URL for resolving relative paths
    base_url = request.build_absolute_uri('/')
    pisa.CreatePDF(html, dest=response, link_callback=lambda uri, _: os.path.join(base_url, uri))

    return response


def tailor_details(request):
    tailors = AddTailors.objects.all()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor.html', context)

# def customer_list(request):
#     customers = Customer.objects.all()
#     return render(request, 'customer_list.html', {'customers': customers})

def all_customers(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

def customer_history(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    orders = Order.objects.filter(customer=customer)
    return render(request, 'customer_history.html',  {'customer': customer, 'orders': orders})

def edit_tailor(request, tailor_id):
    tailor = get_object_or_404(AddTailors, pk=tailor_id)

    if request.method == 'POST':
        form = TailorForm(request.POST, instance=tailor)
        if form.is_valid():
            form.save()
            return redirect('view_tailors')
    else:
        form = TailorForm(instance=tailor)

    return render(request, 'edit_tailor.html', {'form': form, 'tailor_id': tailor_id})

def delete_tailor(request, tailor_id):
    tailor = get_object_or_404(AddTailors, pk=tailor_id)

    # Add your logic for deleting tailor here
    tailor.delete()

    return redirect('view_tailors') 

# def upcoming_deliveries(request):
#     customers = Customer.objects.order_by('delivery_date')
#     return render(request, 'dashboard.html', {'cus': customers})


# def customer_history(request):
#     customers = Customer.objects.all()

#     # Fetch all works for each customer
#     customer_works = {}
#     for customer in customers:
#         works = Work.objects.filter(customer=customer)
#         customer_works[customer] = works

#     return render(request, 'customer_history.html', {'customers': customers, 'customer_works': customer_works})