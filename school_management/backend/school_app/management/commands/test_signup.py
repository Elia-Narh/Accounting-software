from django.core.management.base import BaseCommand
from django.test import Client

class Command(BaseCommand):
    help = 'Test the signup functionality'

    def handle(self, *args, **kwargs):
        client = Client()
        response = client.post('/signup/', {'username': 'new_testuser', 'password1': 'testpassword', 'password2': 'testpassword'})
        self.stdout.write(self.style.SUCCESS(f'Signup response status code: {response.status_code}'))
