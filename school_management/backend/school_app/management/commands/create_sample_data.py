from django.core.management.base import BaseCommand
from django.utils import timezone
from school_app.models import Student, Teacher, Course, Enrollment, Grade, Attendance
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Creates sample data for the school management system'

    def handle(self, *args, **kwargs):
        # Create sample students
        students = []
        for i in range(50):
            student = Student.objects.create(
                name=f'Student {i+1}',
                email=f'student{i+1}@example.com',
                date_of_birth=timezone.now() - timedelta(days=365*18 + random.randint(0, 365*2))
            )
            students.append(student)
        self.stdout.write(self.style.SUCCESS('Created 50 students'))

        # Create sample teachers
        teachers = []
        subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 'History', 'Literature', 'Computer Science']
        for i in range(10):
            teacher = Teacher.objects.create(
                name=f'Teacher {i+1}',
                email=f'teacher{i+1}@example.com',
                subject_specialty=random.choice(subjects)
            )
            teachers.append(teacher)
        self.stdout.write(self.style.SUCCESS('Created 10 teachers'))

        # Create sample courses
        courses = []
        for i in range(20):
            course = Course.objects.create(
                name=f'Course {i+1}',
                description=f'Description for Course {i+1}',
                teacher=random.choice(teachers)
            )
            courses.append(course)
        self.stdout.write(self.style.SUCCESS('Created 20 courses'))

        # Create sample enrollments
        for student in students:
            # Each student enrolls in 3-5 random courses
            for course in random.sample(courses, random.randint(3, 5)):
                enrollment_date = timezone.now() - timedelta(days=random.randint(0, 180))
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    enrollment_date=enrollment_date,
                    created_at=enrollment_date
                )
        self.stdout.write(self.style.SUCCESS('Created enrollments'))

        # Create sample grades
        for enrollment in Enrollment.objects.all():
            # Create 2-4 grades per enrollment
            for _ in range(random.randint(2, 4)):
                Grade.objects.create(
                    student=enrollment.student,
                    course=enrollment.course,
                    score=random.uniform(60.0, 100.0),
                    date=timezone.now() - timedelta(days=random.randint(0, 90))
                )
        self.stdout.write(self.style.SUCCESS('Created grades'))

        # Create sample attendance records
        statuses = ['PRESENT', 'ABSENT', 'LATE']
        for enrollment in Enrollment.objects.all():
            # Create attendance records for the past 30 days
            for i in range(30):
                if random.random() < 0.8:  # 80% chance of having an attendance record
                    Attendance.objects.create(
                        student=enrollment.student,
                        course=enrollment.course,
                        date=timezone.now() - timedelta(days=i),
                        status=random.choices(statuses, weights=[0.8, 0.1, 0.1])[0]
                    )
        self.stdout.write(self.style.SUCCESS('Created attendance records'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample data')) 