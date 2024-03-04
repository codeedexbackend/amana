from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, RetrieveUpdateAPIView, ListAPIView, \
    get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from dashboard.models import AddTailors, Customer, Item, Add_order
from .serializers import TailorLoginSerializer, CustomerSerializer, CompletedCustomerSerializer


# Create your views here.
def reception_indexpage(request):
    total_customers = Customer.objects.count()
    total_orders = Customer.objects.count()  # Assuming you have an Order model

    total_completed_works = AddTailors.objects.aggregate(Sum('completed_works'))['completed_works__sum']

    cus = Customer.objects.filter(delivery_date__gte=date.today()).order_by('delivery_date')

    context = {'total_customers': total_customers, 'total_orders': total_orders,
               'cus': cus,
               'total_completed_works': total_completed_works}

    return render(request, "reception_dashboard.html", context)


def search_mobile_recption(request):
    results = {'Customer': []}
    query = ""

    if 'q' in request.GET:
        query = request.GET['q']

        results['customer'] = Customer.objects.filter(mobile__icontains=query).exclude(mobile__isnull=True).exclude(
            mobile__exact='')

    return render(request, 'search_reception.html', {'results': results, 'query': query})


def createcustomer_reception(request):
    tailor = AddTailors.objects.all()
    tailor_works = []
    for tailor in tailor:
        assigned_works = Customer.objects.filter(tailor=tailor, status='assigned').count()
        pending_works = tailor.pending_works  # Assuming you have a pending_works field in AddTailors
        tailor_works.append({'tailor': tailor, 'assigned_works': assigned_works, 'pending_works': pending_works})

    context = {'tailor_works': tailor_works}
    return render(request, 'Create_customer_reception.html', context)


def check_tailor_works_recption(request):
    if request.method == 'GET':
        tailor_id = request.GET.get('tailor_id')
        delivery_date = request.GET.get('delivery_date')

        try:
            # Assuming you have a Customer model with a tailor field
            works = Customer.objects.filter(tailor__id=tailor_id, delivery_date=delivery_date)

            # You may need to serialize the works data based on your requirements
            serialized_works = [{'name': work.name, 'other_field': work.other_field} for work in works]

            return JsonResponse({'works': serialized_works})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def fetch_tailor_options_recption(request):
    if request.method == 'GET' and 'delivery_date' in request.GET:
        delivery_date = request.GET.get('delivery_date')

        try:
            tailors = AddTailors.objects.all()
            tailor_options = []

            for tailor in tailors:
                try:
                    # Access the related set of Customer objects using customer_set
                    works_on_date = tailor.customer_set.filter(delivery_date=delivery_date)

                    # Count assigned and pending works separately
                    assigned_works = works_on_date.filter(status='assigned').count()
                    pending_works = works_on_date.filter(status='pending').count()

                    tailor_options.append({
                        'id': tailor.id,
                        'name': tailor.tailor,
                        'assigned_works': assigned_works,
                        'pending_works': pending_works,
                    })
                except Exception as e:
                    print(f"Error processing tailor {tailor.id}: {str(e)}")

            return JsonResponse({'tailor_options': tailor_options})

        except Exception as e:
            # Print the error details to the console
            import traceback
            print(traceback.format_exc())

            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def savecustomer_recption(request):
    context = {}
    if request.method == "POST":
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
        ds = request.POST.get('description')
        tailor_id = request.POST.get('tailor')
        cloth = request.POST.get('Cloth')

        tailor_instance = AddTailors.objects.get(id=tailor_id)

        works_on_delivery_date = Customer.objects.filter(tailor=tailor_instance, delivery_date=dd).count()

        if works_on_delivery_date >= 6:
            error_message = f"Tailor {tailor_instance.tailor} already has 6 or more works on {dd}. Cannot assign new work."
            if request.is_ajax():
                return JsonResponse({'error': error_message}, status=400)
            else:
                messages.error(request, error_message)
                return redirect(createcustomer_reception)

        tailor_instance.assigned_works += 1
        tailor_instance.save()

        try:
            obj = Customer(name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg, cuff_length=cl,
                           cuff_type=ct, sleeve_type=sl, sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2,
                           order_date=od,cloth=cloth,
                           delivery_date=dd, tailor=tailor_instance, button_type=bt, neck_round=ncr, wrist=wr,
                           collar=clr, description=ds)
            obj.save()
            messages.success(request, "Successfully added customer")
            return redirect(createcustomer_reception)
        except IntegrityError as e:
            # Handle IntegrityError
            return JsonResponse({'error': f"IntegrityError: {str(e)}"}, status=500)
        except Exception as e:
            # Handle other exceptions
            return JsonResponse({'error': f"Error saving customer: {str(e)}"}, status=500)

    return render(request, 'Create_customer.html', context)


def customer_details_recption(request):
    cus = Customer.objects.all()
    return render(request, "Customer_details_reception.html", {"cus": cus})

def single_customer_reception(request, customer_id):
    single = Customer.objects.filter(id=customer_id)
    itms = Item.objects.filter(customer_id=customer_id)
    return render(request, "single_customer_reception.html", {'single': single,'itms':itms})


def tailor_details_recption(request):
    tailors = AddTailors.objects.all()

    for tailor in tailors:
        # Calculate assigned, pending, upcoming, and completed works
        tailor.assigned_works = Customer.objects.filter(tailor=tailor, status='assigned').count()
        tailor.pending_works = Customer.objects.filter(tailor=tailor, status='in_progress').count()
        tailor.upcoming_works = Customer.objects.filter(tailor=tailor, delivery_date__gt=date.today()).count()
        tailor.completed_works = Customer.objects.filter(tailor=tailor, status='completed').count()

    context = {'tailors': tailors}
    return render(request, 'View_Tailor_reception.html', context)


def additems_reception(request,dataid):
    customers = Customer.objects.get(id=dataid)
    return render(request, "Add_Items_reception.html", {"customers": customers})


def save_items_recption(request):
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

        return redirect('customer_details_recption')

    customers = Customer.objects.all()
    return render(request, 'Add_Items_reception.html', {'customers': customers})


def add_order_recption(request, dataid):
    add = Customer.objects.get(id=dataid)
    return render(request, "Add_order_reception.html", {"add": add})


def save_add_order_recption(request):
    if request.method == "POST":
        # Your existing form processing logic
        name = request.POST.get('name')
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
        cloth = request.POST.get('cloth')


        # Get or create the tailor instance
        name_instance, created = Customer.objects.get_or_create(name=name)
        tailor_instance, created = AddTailors.objects.get_or_create(tailor=tailor_id)

        # Update assigned_works for the selected tailor
        tailor_instance.assigned_works += 1
        tailor_instance.save()

        # Create the customer instance
        obj = Add_order(name=name_instance, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc, regal=rg, cuff_length=cl,
                       cuff_type=ct, sleeve_type=sl, sleeve_length=sll, pocket=po, bottom1=b1, bottom2=b2,
                       order_date=od,cloth=cloth,
                       delivery_date=dd, tailor=tailor_instance, button_type=bt, neck_round=ncr, wrist=wr, collar=clr)

        obj.save()

        messages.success(request, f"Successfully added new order: {obj.name}")

        return redirect('add_order_recption', dataid=obj.id)


def edit_customer_recption(request, dataid):
    ed = AddTailors.objects.all()
    cus = Customer.objects.get(id=dataid)
    return render(request, "edit_customer_reception.html", {"cus": cus, "ed": ed})


def update_customer_recption(request, dataid):
    if request.method == "POST":
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
        cloth = request.POST.get('cloth')
        try:
            order_date = datetime.strptime(od, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            # Handle invalid date format error
            # You might want to provide a default value or raise an error depending on your use case
            order_date = None
        dd = request.POST.get('delivery_date')
        bt = request.POST.get('button_type')
        tailor_id = request.POST.get('tailor')

        # Get the existing customer
        customer = Customer.objects.get(id=dataid)

        # Get the old tailor before updating
        old_tailor = customer.tailor

        # Get or create the new tailor instance
        new_tailor, created = AddTailors.objects.get_or_create(tailor=tailor_id)

        # Update assigned_works for the old tailor and new tailor
        if old_tailor != new_tailor:
            old_tailor.assigned_works -= 1
            old_tailor.save()
            new_tailor.assigned_works += 1
            new_tailor.save()

        # Update the customer instance
        Customer.objects.filter(id=dataid).update(name=nm, mobile=mn, length=ln, shoulder=sd, loose=lo, neck=nc,
                                                  regal=rg, cuff_length=cl,
                                                  cuff_type=ct, sleeve_type=sl, sleeve_length=sll, pocket=po,
                                                  bottom1=b1, bottom2=b2,cloth=cloth,
                                                  order_date=od, delivery_date=dd, tailor=new_tailor, button_type=bt,
                                                  neck_round=ncr, wrist=wr, collar=clr)

        return redirect(customer_details_recption)


def customerdlt_recption(request, dlt):
    delt = Customer.objects.filter(id=dlt)
    delt.delete()
    return redirect(customer_details_recption)


def tailor_work_details_recption(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        tailors = AddTailors.objects.all()

        tailor_data = []
        for tailor in tailors:
            assigned_works = Customer.objects.filter(
                tailor=tailor, status='assigned', order_date__range=[start_date, end_date]
            ).count()

            pending_works = Customer.objects.filter(
                tailor=tailor, status='in_progress', order_date__range=[start_date, end_date]
            ).count()

            completed_works = Customer.objects.filter(
                tailor=tailor, status='completed', order_date__range=[start_date, end_date]
            ).count()

            tailor_info = {
                'tailor': tailor,
                'assigned_works': assigned_works,
                'pending_works': pending_works,
                'completed_works': completed_works
            }

            tailor_data.append(tailor_info)

        context = {
            'tailor_data': tailor_data,
            'start_date': start_date,
            'end_date': end_date,
        }

        return render(request, 'tailor_details_reception.html', context)

    return render(request, 'tailor_work_reception.html')


def select_dates_recption(request):
    return render(request, "tailor_work_reception.html")


# API


class TailorLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TailorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        print(f"Attempting to authenticate user: {username}")

        user = authenticate(request, username=username, password=password)

        try:
            user = AddTailors.objects.get(username=username, password=password)
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
