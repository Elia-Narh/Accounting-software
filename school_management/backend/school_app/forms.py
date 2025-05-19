from django import forms
from .models import Course, Enrollment, Teacher, Student, Grade

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'email']  # Removed 'subject' field




class EnrollmentForm(forms.ModelForm):
    # enrollment_date = forms.DateField(required=False)  # Re-add enrollment_date field


    class Meta:
        model = Enrollment
        fields = ['student', 'course']  # Removed 'enrollment_date' field



class CourseForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all())  # Use queryset for dynamic choices

    class Meta:
        model = Course
        fields = ['name', 'teacher', 'start_date', 'end_date']  # Use existing fields in the Course model


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'date_of_birth', 'status']


class GradeForm(forms.ModelForm):
    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score < 0 or score > 100:
            raise forms.ValidationError("Score must be between 0 and 100.")
        return score

    class Meta:
        model = Grade
        fields = ['student', 'course', 'score', 'date']
