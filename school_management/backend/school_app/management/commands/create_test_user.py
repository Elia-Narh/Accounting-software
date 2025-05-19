from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create a test user'

    def handle(self, *args, **kwargs):
        User.objects.create_user(username='new_testuser', password='testpassword')
        self.stdout.write(self.style.SUCCESS('Successfully created test user'))
