from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from .models import (
    Enrollment, Student, Course, Teacher, Grade, FeePayment,
    Announcement, ChatMessage, ChatRoom, Notification,
    UserNotificationSetting, Attendance, Assignment, ExamResult, SchoolEvent
)
from django.forms import ModelForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max, Avg, Min
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta
from itertools import chain
from django.db import models

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('school_app:dashboard')
        else:
            return redirect('school_app:student_dashboard')
    return redirect('school_app:login')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('school_app:dashboard')
        else:
            return redirect('school_app:student_dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_role = request.POST.get('user_role')
            remember_me = request.POST.get('remember_me') == 'on'
            
            user = authenticate(username=username, password=password)
            if user is not None:
                # Check if user role matches their actual role
                if user_role == 'admin' and user.is_staff:
                    login(request, user)
                    messages.success(request, 'You have been logged out successfully.')
                    if not remember_me:
                        request.session.set_expiry(0)  # Session expires when browser closes
                    return redirect('school_app:dashboard')
                elif user_role == 'student' and not user.is_staff:
                    # Check if student profile exists
                    try:
                        student = Student.objects.get(user=user)
                        login(request, user)
                        messages.success(request, 'You have been logged out successfully.')
                        if not remember_me:
                            request.session.set_expiry(0)  # Session expires when browser closes
                        return redirect('school_app:student_dashboard')
                    except Student.DoesNotExist:
                        messages.error(request, 'No student profile found for this account.')
                else:
                    messages.error(request, 'Please select the correct role for your account.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
        
    return render(request, 'school_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('school_app:login')

@staff_member_required
def dashboard(request):
    # Basic statistics
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_courses = Course.objects.count()
    
    # Get current date and date range for upcoming events
    today = timezone.now()
    thirty_days_from_now = today + timezone.timedelta(days=30)
    
    # Fetch upcoming assignments
    upcoming_assignments = Assignment.objects.filter(
        due_date__gte=today,
        due_date__lte=thirty_days_from_now
    ).select_related('course').order_by('due_date')

    # Fetch upcoming exams
    upcoming_exams = ExamResult.objects.filter(
        date__gte=today,
        date__lte=thirty_days_from_now
    ).select_related('course').order_by('date')

    # Fetch upcoming school events
    upcoming_events = SchoolEvent.objects.filter(
        start_date__gte=today,
        start_date__lte=thirty_days_from_now
    ).order_by('start_date')

    # Combine all events for the calendar
    calendar_events = []
    
    # Add assignments
    for assignment in upcoming_assignments:
        calendar_events.append({
            'title': f'Assignment Due: {assignment.title}',
            'start': assignment.due_date.isoformat(),
            'end': assignment.due_date.isoformat(),
            'color': '#ff9f89',  # Reddish color for assignments
            'url': f'/assignment/{assignment.id}/',
            'type': 'assignment'
        })
    
    # Add exams
    for exam in upcoming_exams:
        calendar_events.append({     
            'title': f'Exam: {exam.course.name}',
            'start': exam.date.isoformat(),
            'end': exam.date.isoformat(),
            'color': '#ffd700',  # Gold color for exams
            'url': f'/exam/{exam.id}/',
            'type': 'exam'
        })
    
    # Add school events
    for event in upcoming_events:
        calendar_events.append({
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'color': event.color,
            'url': f'/event/{event.id}/',
            'type': event.event_type.lower(),
            'location': event.location
        })

    # Enrollment trends (last 6 months)
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    enrollment_trends = (
        Enrollment.objects
        .filter(created_at__gte=six_months_ago)
        .extra(
            select={
                'month': "substr(created_at, 1, 7)"  # Extract YYYY-MM from the date string
            }
        )
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Attendance statistics (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    attendance_stats = (
        Attendance.objects
        .filter(date__gte=thirty_days_ago)
        .values('status')
        .annotate(count=Count('id'))
    )

    # Grade distribution
    grade_distribution = (
        Grade.objects
        .values('course__name')
        .annotate(
            avg_score=Avg('score'),
            min_score=Min('score'),
            max_score=Max('score')
        )
        .order_by('-avg_score')[:5]
    )

    # Teacher workload
    teacher_workload = (
        Course.objects
        .values('teacher__name')
        .annotate(course_count=Count('id'))
        .order_by('-course_count')
    )

    # Recent enrollments with related data
    recent_enrollments = Enrollment.objects.select_related(
        'student', 'course'
    ).order_by('-created_at')[:5]

    # Recent announcements
    recent_announcements = Announcement.objects.select_related(
        'created_by'
    ).order_by('-created_at')[:5]

    # Get unread notifications count and recent notifications
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
    else:
        unread_notifications_count = 0
        recent_notifications = []

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'enrollment_trends': json.dumps(list(enrollment_trends), cls=DjangoJSONEncoder),
        'attendance_stats': json.dumps(list(attendance_stats), cls=DjangoJSONEncoder),
        'grade_distribution': json.dumps(list(grade_distribution), cls=DjangoJSONEncoder),
        'teacher_workload': json.dumps(list(teacher_workload), cls=DjangoJSONEncoder),
        'recent_enrollments': recent_enrollments,
        'recent_announcements': recent_announcements,
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
        'calendar_events': json.dumps(calendar_events, cls=DjangoJSONEncoder),
        'upcoming_assignments': upcoming_assignments[:5],  # Limit to 5 for the widget
        'upcoming_exams': upcoming_exams[:5],  # Limit to 5 for the widget
        'upcoming_events': upcoming_events[:5],  # Limit to 5 for the widget
    }

    return render(request, 'school_app/dashboard.html', context)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

def sign_up_view(request):
    if request.user.is_authenticated:
        return redirect('school_app:dashboard')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Make the user a staff member by default
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('school_app:login')
    else:
        form = SignUpForm()
    return render(request, 'school_app/signup.html', {'form': form})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'school_app/password_reset_form.html'  # Specify the template to use

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'teacher']

@staff_member_required
def course_list(request):
    courses = Course.objects.all().order_by('name')
    return render(request, 'school_app/course_list.html', {'courses': courses})

@staff_member_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully.')
            return redirect('school_app:course_list')
    else:
        form = CourseForm()
    
    return render(request, 'school_app/course_form.html', {
        'form': form,
        'action': 'Create'
    })

@staff_member_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('school_app:course_list')
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'school_app/course_form.html', {
        'form': form,
        'action': 'Update'
    })

@staff_member_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('school_app:course_list')
    
    return render(request, 'school_app/course_confirm_delete.html', {
        'course': course
    })

@staff_member_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrolled_students = course.enrollments.all().select_related('student')
    return render(request, 'school_app/course_detail.html', {
        'course': course,
        'enrolled_students': enrolled_students
    })

class TeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'subject_specialty']

def teacher_list(request):
    teachers = Teacher.objects.all().order_by('name')
    return render(request, 'school_app/teacher_list.html', {'teachers': teachers})

def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher created successfully.')
            return redirect('school_app:teacher_list')
    else:
        form = TeacherForm()
    return render(request, 'school_app/teacher_form.html', {'form': form, 'action': 'Create'})

def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully.')
            return redirect('school_app:teacher_list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'school_app/teacher_form.html', {'form': form, 'action': 'Update'})

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
        return redirect('school_app:teacher_list')
    return render(request, 'school_app/teacher_confirm_delete.html', {'teacher': teacher})

def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    courses = teacher.courses.all()
    return render(request, 'school_app/teacher_detail.html', {'teacher': teacher, 'courses': courses})

def grade_delete(request, pk):
    return render(request, 'school_app/grade_confirm_delete.html')  # Render the grade deletion confirmation template

def grade_update(request, pk):
    return render(request, 'school_app/grade_form.html')  # Render the grade update template

def grade_create(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade created successfully.')
            return redirect('school_app:grade_list')
    else:
        form = GradeForm()
    return render(request, 'school_app/grade_form.html', {'form': form, 'action': 'Create'})

def grade_list(request):
    grades = Grade.objects.all().order_by('-date')
    return render(request, 'school_app/grade_list.html', {'grades': grades})

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'date_of_birth', 'status']

def student_list(request):
    students = Student.objects.all().order_by('name')
    return render(request, 'school_app/student_list.html', {'students': students})

def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully.')
            return redirect('school_app:student_list')
    else:
        form = StudentForm()
    return render(request, 'school_app/student_form.html', {'form': form, 'action': 'Create'})

def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('school_app:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'school_app/student_form.html', {'form': form, 'action': 'Update'})

def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('school_app:student_list')
    return render(request, 'school_app/student_confirm_delete.html', {'student': student})

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.all()
    grades = student.grade_set.all()
    return render(request, 'school_app/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
        'grades': grades
    })

@staff_member_required
def enrollment_list(request):
    enrollments = Enrollment.objects.all().select_related('student', 'course').order_by('-enrollment_date')
    return render(request, 'school_app/enrollment_list.html', {'enrollments': enrollments})

@staff_member_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment.objects.select_related('student', 'course'), pk=pk)
    return render(request, 'school_app/enrollment_detail.html', {'enrollment': enrollment})

@staff_member_required
def enrollment_create(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment created successfully.')
            return redirect('school_app:enrollment_list')
    else:
        form = EnrollmentForm()
    
    return render(request, 'school_app/enrollment_form.html', {
        'form': form,
        'action': 'Create'
    })

@staff_member_required
def enrollment_update(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment updated successfully.')
            return redirect('school_app:enrollment_list')
    else:
        form = EnrollmentForm(instance=enrollment)
    
    return render(request, 'school_app/enrollment_form.html', {
        'form': form,
        'action': 'Update'
    })

@staff_member_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment deleted successfully.')
        return redirect('school_app:enrollment_list')
    
    return render(request, 'school_app/enrollment_confirm_delete.html', {
        'enrollment': enrollment
    })

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'school_app/password_reset_confirm.html'  # Specify the template to use

class EnrollmentForm(ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'enrollment_date', 'status']

class GradeForm(ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'course', 'score', 'date']

class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user

@user_passes_test(lambda u: u.is_superuser)
def create_admin(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin account created successfully.')
            return redirect('school_app:dashboard')
    else:
        form = AdminUserCreationForm()
    return render(request, 'school_app/create_admin.html', {'form': form})

class FeePaymentForm(ModelForm):
    class Meta:
        model = FeePayment
        fields = ['student', 'amount', 'payment_date', 'payment_method']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

@staff_member_required
def fee_list(request):
    payments = FeePayment.objects.all().select_related('student').order_by('-payment_date')
    return render(request, 'school_app/fee_list.html', {'payments': payments})

@staff_member_required
def fee_create(request):
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment recorded successfully.')
            return redirect('school_app:fee_list')
    else:
        form = FeePaymentForm()
    return render(request, 'school_app/fee_form.html', {
        'form': form,
        'action': 'Record'
    })

@staff_member_required
def fee_update(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk)
    if request.method == 'POST':
        form = FeePaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully.')
            return redirect('school_app:fee_list')
    else:
        form = FeePaymentForm(instance=payment)
    return render(request, 'school_app/fee_form.html', {
        'form': form,
        'action': 'Update'
    })

@staff_member_required
def fee_delete(request, pk):
    payment = get_object_or_404(FeePayment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
        return redirect('school_app:fee_list')
    return render(request, 'school_app/fee_confirm_delete.html', {'payment': payment})

class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'groups', 'user_permissions')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'groups', 'user_permissions')

@staff_member_required
def user_list(request):
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')

    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    if role_filter:
        if role_filter == 'admin':
            users = users.filter(is_superuser=True)
        elif role_filter == 'staff':
            users = users.filter(is_staff=True, is_superuser=False)
        elif role_filter == 'teacher':
            users = users.filter(is_staff=False, is_superuser=False)

    if status_filter:
        users = users.filter(is_active=(status_filter == 'active'))

    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'school_app/user_list.html', {
        'users': page_obj,
        'is_paginated': True,
        'page_obj': page_obj,
        'paginator': paginator
    })

@staff_member_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'school_app/user_detail.html', {'user': user})

@staff_member_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('school_app:user_list')
    else:
        form = UserForm()
    return render(request, 'school_app/user_form.html', {
        'form': form,
        'action': 'Create'
    })

@staff_member_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('school_app:user_list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'school_app/user_form.html', {
        'form': form,
        'action': 'Update'
    })

@staff_member_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('school_app:user_list')
    return render(request, 'school_app/user_confirm_delete.html', {'user': user})

# Announcement Views
@staff_member_required
def announcement_list(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'school_app/announcement_list.html', {'announcements': announcements})

@staff_member_required
def announcement_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        target_group = request.POST.get('target_group')
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            target_group=target_group,
            created_by=request.user
        )
        
        # Create notifications for target users
        users = User.objects.all()
        if target_group != 'ALL':
            if target_group == 'STUDENTS':
                users = users.filter(student__isnull=False)
            elif target_group == 'TEACHERS':
                users = users.filter(teacher__isnull=False)
            elif target_group == 'STAFF':
                users = users.filter(is_staff=True)
        
        for user in users:
            Notification.objects.create(
                user=user,
                type='ANNOUNCEMENT',
                title=f'New Announcement: {announcement.title}',
                message=announcement.content,
                reference_id=announcement.id,
                reference_type='Announcement'
            )
        
        messages.success(request, 'Announcement created successfully.')
        return redirect('school_app:announcement_list')
    
    return render(request, 'school_app/announcement_form.html')

# Chat Views
@login_required
def chat_list(request):
    user_rooms = ChatRoom.objects.filter(participants=request.user).annotate(
        unread_count=Count('last_message', filter=Q(chatmessage__is_read=False, chatmessage__receiver=request.user))
    ).order_by('-last_message__sent_at')
    
    return render(request, 'school_app/chat_list.html', {'chat_rooms': user_rooms})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    messages = ChatMessage.objects.filter(chat_room=room).order_by('sent_at')
    
    # Mark messages as read
    messages.filter(receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'school_app/chat_room.html', {
        'room': room,
        'messages': messages
    })

@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        room_id = data.get('room_id')
        content = data.get('content')
        receiver_id = data.get('receiver_id')
        
        room = ChatRoom.objects.get(id=room_id)
        receiver = User.objects.get(id=receiver_id)
        
        message = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            chat_room=room
        )
        
        # Update last message
        room.last_message = message
        room.save()
        
        # Create notification
        Notification.objects.create(
            user=receiver,
            type='MESSAGE',
            title=f'New message from {request.user.get_full_name() or request.user.username}',
            message=content[:100] + '...' if len(content) > 100 else content,
            reference_id=message.id,
            reference_type='ChatMessage'
        )
        
        return JsonResponse({'status': 'success', 'message_id': message.id})
    
    return JsonResponse({'status': 'error'}, status=400)

# Notification Views
@login_required
def notification_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    # Mark notifications as read
    if request.GET.get('mark_read'):
        notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'school_app/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def notification_settings(request):
    settings, created = UserNotificationSetting.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        settings.email_notifications = request.POST.get('email_notifications') == 'on'
        settings.sms_notifications = request.POST.get('sms_notifications') == 'on'
        settings.push_notifications = request.POST.get('push_notifications') == 'on'
        settings.email = request.POST.get('email')
        settings.phone_number = request.POST.get('phone_number')
        settings.quiet_hours_start = request.POST.get('quiet_hours_start')
        settings.quiet_hours_end = request.POST.get('quiet_hours_end')
        settings.save()
        
        messages.success(request, 'Notification settings updated successfully.')
        return redirect('school_app:notification_settings')
    
    return render(request, 'school_app/notification_settings.html', {'settings': settings})

def send_notification(user, notification_type, title, message, reference_id=None, reference_type=None):
    """Utility function to send notifications through various channels"""
    settings = UserNotificationSetting.objects.get_or_create(user=user)[0]
    
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        reference_id=reference_id,
        reference_type=reference_type
    )
    
    # Send email notification
    if settings.email_notifications and settings.email:
        send_mail(
            title,
            message,
            settings.EMAIL_HOST_USER,
            [settings.email],
            fail_silently=True,
        )
    
    # Send SMS notification (implement with your preferred SMS service)
    if settings.sms_notifications and settings.phone_number:
        # Implement SMS sending logic here
        pass
    
    # Send push notification (implement with your preferred push notification service)
    if settings.push_notifications:
        # Implement push notification logic here
        pass
    
    notification.is_sent = True
    notification.save()
    
    return notification

@login_required
def search(request):
    query = request.GET.get('q', '')
    results = {
        'students': [],
        'teachers': [],
        'courses': [],
        'announcements': []
    }
    
    if query:
        # Search in Students
        results['students'] = Student.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query)
        )[:5]
        
        # Search in Teachers
        results['teachers'] = Teacher.objects.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject_specialty__icontains=query)
        )[:5]
        
        # Search in Courses
        results['courses'] = Course.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:5]
        
        # Search in Announcements
        results['announcements'] = Announcement.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:5]
    
    return render(request, 'school_app/search_results.html', {
        'query': query,
        'results': results
    })

@login_required
def student_dashboard(request):
    # Get the student associated with the current user
    student = get_object_or_404(Student, user=request.user)
    
    # Get current enrollments and courses
    enrollments = Enrollment.objects.filter(
        student=student,
        status='active'
    ).select_related('course', 'course__teacher')

    # Get upcoming deadlines (assignments and exams)
    upcoming_deadlines = []
    
    # Get assignments due in the next 2 weeks
    assignments = Assignment.objects.filter(
        course__enrollments__student=student,
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timedelta(days=14)
    ).order_by('due_date')
    
    for assignment in assignments:
        upcoming_deadlines.append({
            'type': 'assignment',
            'title': assignment.title,
            'course': assignment.course.name,
            'date': assignment.due_date.strftime('%b %d'),
            'time': assignment.due_date.strftime('%I:%M %p')
        })

    # Get recent grades
    recent_grades = Grade.objects.filter(
        student=student
    ).order_by('-date')[:5]

    # Calculate GPA
    gpa = Grade.objects.filter(
        student=student
    ).aggregate(Avg('score'))['score__avg'] or 0

    # Get attendance statistics
    attendance_stats = Attendance.objects.filter(
        student=student
    ).aggregate(
        total=Count('id'),
        present=Count('id', filter=models.Q(status='PRESENT'))
    )
    
    attendance_rate = (
        (attendance_stats['present'] / attendance_stats['total'] * 100)
        if attendance_stats['total'] > 0 else 0
    )

    # Get notifications
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    # Get weekly schedule
    weekly_schedule = []
    # You would need to implement your own logic here to get the weekly schedule
    # This is just example data
    weekly_schedule = [
        {
            'day': 'Monday',
            'time': '09:00 AM',
            'course': 'Mathematics',
            'room': 'Room 101'
        },
        # Add more schedule items
    ]

    context = {
        'student': student,
        'enrollments': enrollments,
        'upcoming_deadlines': upcoming_deadlines,
        'recent_grades': recent_grades,
        'gpa': round(gpa, 2),
        'attendance_rate': round(attendance_rate, 1),
        'notifications': notifications,
        'weekly_schedule': weekly_schedule,
    }

    return render(request, 'school_app/student_dashboard.html', context)
