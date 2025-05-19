from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    subject_specialty = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.name} enrolled in {self.course.name}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('P', 'Present'), ('A', 'Absent')])

    class Meta:
        verbose_name = "Attendance"
        verbose_name_plural = "Attendances"
        unique_together = ('student', 'course', 'date')  # Ensure a student can only have one attendance record per course per day

    def __str__(self):
        return f"{self.student} - {self.course} on {self.date}: {self.status}"

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Set default value
    date = models.DateField(default=timezone.now)  # Set default value

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"
        unique_together = ('student', 'course', 'date')  # Ensure a student can only have one grade record per course per day

    def __str__(self):
        return f"{self.student} - {self.course}: {self.score} on {self.date}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    due_date = models.DateField()

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        ordering = ["due_date"]  # Sort assignments by due date

    def __str__(self):
        return f"{self.title} for {self.course}"

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(default=timezone.now)  # Set default value

    class Meta:
        verbose_name = "Exam Result"
        verbose_name_plural = "Exam Results"
        unique_together = ('student', 'course', 'date')  # Ensure a student can only have one exam result per course per day

    def __str__(self):
        return f"{self.student} - {self.course}: {self.score} on {self.date}"

class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Fee Payment"
        verbose_name_plural = "Fee Payments"

    def __str__(self):
        return f"{self.student} - {self.amount} on {self.payment_date}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('FEE_DUE', 'Fee Due'),
        ('ATTENDANCE', 'Attendance'),
        ('ANNOUNCEMENT', 'Announcement'),
        ('MESSAGE', 'New Message'),
        ('GRADE', 'Grade Posted'),
        ('SYSTEM', 'System Notification')
    ]

    DELIVERY_METHODS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
        ('ALL', 'All Methods')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    title = models.CharField(max_length=200, default='System Notification')
    message = models.TextField()
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHODS, default='ALL')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    reference_id = models.IntegerField(null=True, blank=True)  # To store related object ID
    reference_type = models.CharField(max_length=50, null=True, blank=True)  # To store related object type

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.type} notification for {self.user}'

class UserNotificationSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'Notification settings for {self.user}'

class Message(models.Model):
    sender = models.ForeignKey(Student, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Student, related_name='received_messages', on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.sent_at}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    target_group = models.CharField(max_length=20, choices=[
        ('ALL', 'All Users'),
        ('STUDENTS', 'Students Only'),
        ('TEACHERS', 'Teachers Only'),
        ('STAFF', 'Staff Only')
    ])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f'Message from {self.sender} to {self.receiver} at {self.sent_at}'

class ChatRoom(models.Model):
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_room')
    is_group_chat = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True, blank=True)  # For group chats

    def __str__(self):
        if self.is_group_chat and self.name:
            return self.name
        return f'Chat between {", ".join(str(p) for p in self.participants.all()[:3])}'

class SchoolEvent(models.Model):
    EVENT_TYPES = [
        ('CONFERENCE', 'Parent-Teacher Conference'),
        ('MEETING', 'School Meeting'),
        ('ACTIVITY', 'School Activity'),
        ('HOLIDAY', 'School Holiday'),
        ('OTHER', 'Other Event')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=7, default='#3788d8')  # Default to blue

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title
