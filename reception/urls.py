from django.urls import path

from reception import views

urlpatterns = [
    path('reception_indexpage/', views.reception_indexpage, name='reception_indexpage'),
    path("createcustomer_reception/", views.createcustomer_reception, name="createcustomer_reception"),
    path('search_mobile_recption/', views.search_mobile_recption, name='search_mobile_recption'),
    path("add_order_recption/<int:dataid>/", views.add_order_recption, name="add_order_recption"),
    path("edit_customer_recption/<int:dataid>/", views.edit_customer_recption, name="edit_customer_recption"),
    path("save_add_order_recption/", views.save_add_order_recption, name="save_add_order_recption"),
    path("update_customer_recption/<int:dataid>/", views.update_customer_recption, name="update_customer_recption"),
    path("customerdlt_recption/<int:dlt>/", views.customerdlt_recption, name="customerdlt_recption"),
    path("customer_details_recption/", views.customer_details_recption, name="customer_details_recption"),
    path("single_customer_reception/<int:customer_id>/", views.single_customer_reception, name="single_customer_reception"),
    path("tailor_details_recption/", views.tailor_details_recption, name="tailor_details_recption"),
    path("additems_reception/<int:dataid>/", views.additems_reception, name="additems_reception"),
    path("save_items_recption/", views.save_items_recption, name="save_items_recption"),
    path("savecustomer_recption/", views.savecustomer_recption, name="savecustomer_recption"),
    path('select_dates_recption/', views.select_dates_recption, name='select_dates_recption'),
    path('tailor_work_details_recption/', views.tailor_work_details_recption, name='tailor_work_details_recption'),

    path('check_tailor_works_recption/', views.check_tailor_works_recption, name='check_tailor_works_recption'),
    path('fetch_tailor_options_recption/', views.fetch_tailor_options_recption, name='fetch_tailor_options_recption'),


    # apilinks
    path('tailor/<int:tailor_id>/customer/<int:id>/inprogress-to-completed/',
         views.InProgressToCompletedAPIView.as_view(), name='inprogress_to_completed'),
    path('tailor/<int:tailor_id>/inprogress-customers/', views.InProgressCustomerListAPIView.as_view(),
         name='inprogress_customer_list'),
    path('tailor/<int:tailor_id>/customer/<int:id>/inprogress/', views.InProgressCustomerUpdateAPIView.as_view(),
         name='inprogress_customer_update'),
    path('tailor/login/', views.TailorLoginView.as_view(), name='tailor-login'),
    path('tailor/<int:tailor_id>/assigned_works/', views.CustomerListAPIView.as_view(), name='assigned-customer-list'),
    path('tailor/<int:tailor_id>/completed/', views.CompletedCustomerListAPIView.as_view(),
         name='completed-customer-list'),
]
