from django.core.management.base import BaseCommand

from inventory.models import Location


class Command(BaseCommand):

    def handle(self, *args, **options):
        ''' This command generates all necessary locations throughout the warehouse.'''

        names = ['A', 'B', 'C', 'D', 'E', 'F']

        for name in names:
            for number in range(10,14):
                for row in range(0,9+1):
                    for height in range(1,4+1):

                        if number == 10 and row == 0:
                            continue
                        else:
                            location = (f'{name}{number}{row}0{height}')
                            Location.objects.create(name=location)


