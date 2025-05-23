from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        '',
        auth_views.LoginView.as_view(
            template_name='employee/login.html',
            next_page='dashboard'  # ✅ Add this
        ),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('leave/<int:pk>/edit/', views.edit_leave, name='edit_leave'),
    path('leave/<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),
]
