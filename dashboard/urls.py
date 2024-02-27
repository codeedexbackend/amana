from django.urls import path
from dashboard import views
from dashboard.views import TailorLoginView

urlpatterns = [
     path('home/', views.dashboard, name='dashboard'),
     path("createcustomer/",views.createcustomer,name="createcustomer"),
     path("addtailors/",views.addtailors,name="addtailors"),
     path("save_tailor/",views.save_tailor,name="save_tailor"),
     path("view_tailors/",views.tailor_details,name="view_tailors"),
     path("additems/",views.additems,name="additems"),
     path("save_items/",views.save_items,name="save_items"),
     path("customer_details/",views.customer_details,name="customer_details"),
     path("order_details/",views.order_details,name="order_details"),
     path("edit_customer/<int:dataid>/",views.edit_customer,name="edit_customer"),
     path("update_customer/<int:dataid>/",views.update_customer,name="update_customer"),

     path("upcoming_deliveries/",views.upcoming_deliveries,name="upcoming_deliveries"),

     path("customerdlt/<int:dlt>/",views.customerdlt,name="customerdlt"),
     path("savecustomer/",views.savecustomer,name="savecustomer"),
     # path("save_tailor/",views.save_tailor,name="save_tailor"),
     path('generate_pdf/<int:measurement_id>/', views.print_measurement, name='generate_pdf'),
     path('customer_list/', views.all_customers, name='customer_list'),
     path('customer_history/<int:customer_id>/', views.customer_history, name='customer_history'),
     path('edit_tailor/<int:dataid>/', views.edit_tailor, name='edit_tailor'),
     path("updatetailor/<int:dataid>/", views.updatetailor, name='updatetailor'),
     path('delete_tailor/<int:dataid>/', views.delete_tailor, name='delete_tailor'),


    path('tailor/login/',  TailorLoginView.as_view(), name='tailor-login'),
    path('tailor/<int:tailor_id>/assigned_works/', views.CustomerListAPIView.as_view(), name='assigned-customer-list'),
    path('tailor/<int:tailor_id>/customer/<int:id>/inprogress/', views.InProgressCustomerUpdateAPIView.as_view(), name='in_progress_customer_update'),
    path('tailor/<int:tailor_id>/cusinprogress/<int:pk>/', views.CustomerDetailAPIView.as_view(), name='customer-detail'),
    path('tailor/<int:tailor_id>/completed-customers/', views.CompletedCustomerListAPIView.as_view(), name='completed-customers'),


     
     
]

