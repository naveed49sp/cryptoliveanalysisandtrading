from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "A command to add data from dataframe to the database"

    def handle(self, *args, **options):
        print("hello world")
