from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetCompleteView

app_name = 'school_app'  # Namespacing the URLs for better reference in templates

urlpatterns = [
    path('', views.home, name='home'),  # Add the root URL pattern

    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.sign_up_view, name='signup'),  # Add signup URL

    # Password reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='school_app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='school_app/password_reset_complete.html'), name='password_reset_complete'),

    # Dashboard
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # Course Management
    path('courses/', login_required(views.course_list), name='course_list'),
    path('courses/create/', login_required(views.course_create), name='course_create'),
    path('courses/<int:pk>/', login_required(views.course_detail), name='course_detail'),
    path('courses/<int:pk>/update/', login_required(views.course_update), name='course_update'),
    path('courses/<int:pk>/delete/', login_required(views.course_delete), name='course_delete'),

    # Enrollment Management
    path('enrollments/', login_required(views.enrollment_list), name='enrollment_list'),
    path('enrollments/create/', login_required(views.enrollment_create), name='enrollment_create'),
    path('enrollments/<int:pk>/', login_required(views.enrollment_detail), name='enrollment_detail'),
    path('enrollments/<int:pk>/update/', login_required(views.enrollment_update), name='enrollment_update'),
    path('enrollments/<int:pk>/delete/', login_required(views.enrollment_delete), name='enrollment_delete'),

    # Student Management
    path('students/', login_required(views.student_list), name='student_list'),
    path('students/create/', login_required(views.student_create), name='student_create'),
    path('students/<int:pk>/', login_required(views.student_detail), name='student_detail'),
    path('students/<int:pk>/update/', login_required(views.student_update), name='student_update'),
    path('students/<int:pk>/delete/', login_required(views.student_delete), name='student_delete'),

    # Teacher Management
    path('teachers/', login_required(views.teacher_list), name='teacher_list'),
    path('teachers/create/', login_required(views.teacher_create), name='teacher_create'),
    path('teachers/<int:pk>/', login_required(views.teacher_detail), name='teacher_detail'),
    path('teachers/<int:pk>/update/', login_required(views.teacher_update), name='teacher_update'),
    path('teachers/<int:pk>/delete/', login_required(views.teacher_delete), name='teacher_delete'),

    # Grade Management
    path('grades/', login_required(views.grade_list), name='grade_list'),
    path('grades/create/', login_required(views.grade_create), name='grade_create'),
    path('grades/<int:pk>/update/', login_required(views.grade_update), name='grade_update'),
    path('grades/<int:pk>/delete/', login_required(views.grade_delete), name='grade_delete'),

    # Fee Management
    path('fees/', login_required(views.fee_list), name='fee_list'),
    path('fees/create/', login_required(views.fee_create), name='fee_create'),
    path('fees/<int:pk>/update/', login_required(views.fee_update), name='fee_update'),
    path('fees/<int:pk>/delete/', login_required(views.fee_delete), name='fee_delete'),

    # User Management
    path('users/', login_required(views.user_list), name='user_list'),
    path('users/create/', login_required(views.user_create), name='user_create'),
    path('users/<int:pk>/', login_required(views.user_detail), name='user_detail'),
    path('users/<int:pk>/update/', login_required(views.user_update), name='user_update'),
    path('users/<int:pk>/delete/', login_required(views.user_delete), name='user_delete'),

    path('create-admin/', views.create_admin, name='create_admin'),

    # Communication
    path('announcements/', login_required(views.announcement_list), name='announcement_list'),
    path('announcements/create/', login_required(views.announcement_create), name='announcement_create'),
    
    path('chat/', login_required(views.chat_list), name='chat_list'),
    path('chat/<int:room_id>/', login_required(views.chat_room), name='chat_room'),
    path('chat/send-message/', login_required(views.send_message), name='send_message'),
    
    path('notifications/', login_required(views.notification_list), name='notification_list'),
    path('notifications/settings/', login_required(views.notification_settings), name='notification_settings'),
    path('search/', views.search, name='search'),
]
# Compare this snippet from school_management/backend/school_app/views.py:
