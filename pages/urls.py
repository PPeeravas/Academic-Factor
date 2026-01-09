from django.urls import path
from . import views  # Import views from the current directory

urlpatterns = [
    # Use 'views.home' instead of 'page_views.home' if you imported it as 'views'
    path('', views.home, name='home'),
]