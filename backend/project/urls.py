from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import routers
from booking.views import (
    CompanyConfigView, 
    BusinessHoursView, 
    ServicesListView, 
    AvailabilityView, 
    AvailabilitySlotsView,
    CreateBookingView
)

# Initialize DRF Router
router = routers.DefaultRouter()

urlpatterns = [
    # Admin Interface
    path("admin/", admin.site.urls),
    
    # Root Redirect to Admin
    path("", RedirectView.as_view(url="/admin/"), name="home-redirect-admin"),
    
    # API Endpoints
    path("api/config/", CompanyConfigView.as_view(), name="api-config"),
    path("api/business-hours/", BusinessHoursView.as_view(), name="api-business-hours"),
    path("api/services/", ServicesListView.as_view(), name="api-services"),
    path("api/availability/days/", AvailabilityView.as_view(), name="api-availability-days"),
    path("api/availability/slots/", AvailabilitySlotsView.as_view(), name="api-availability-slots"),
    path("api/bookings/", CreateBookingView.as_view(), name="api-bookings"),
    path("api/", include(router.urls)),
]

# Serve Media Files in Development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
