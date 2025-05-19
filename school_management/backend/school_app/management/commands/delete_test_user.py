from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Delete the test user'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(username='testuser')
            user.delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted test user'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('Test user does not exist'))
