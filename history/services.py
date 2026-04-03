
from rest_framework.exceptions import NotFound
from django.db import transaction
from history.models import ComponentHistory



def history(code, unique_code, user_name, action):
    """
    Return whole history of components filter by provided field, allow fields : (code, unique_code, user_name)
    user have to choose only one.User also can choose action of components allowed actions :
    ('change_location', 'component_release', 'component_undo') user can omit this filed.
    Queryset is order by the mose recent date
    """

    # if user didn't provide any actions we take all ComponentHistory
    queryset = ComponentHistory.objects.all()

    # checking if user provided correct action
    if action:
        allow_actions = ['change_location', 'component_release', 'component_undo']
        if action not in allow_actions:
            raise NotFound('Wrong action')
        queryset = queryset.filter(action=action)


    if code:
        history_by_code = queryset.filter(code=code).order_by('-date')
        if not history_by_code.exists():
            raise NotFound(f'History of code {code} not found')

        return {
            'message': f'History of code {code}',
            'history': history_by_code
        }



    if unique_code:
        history_by_unique_code = queryset.filter(unique_code=unique_code).order_by('-date')
        if not history_by_unique_code.exists():
            raise NotFound(f'History of unique code {unique_code} not found')

        return {
            'message':f'History of unique code {unique_code}',
            'history':history_by_unique_code
        }


    if user_name:
        history_by_user_name = queryset.filter(full_name=user_name).order_by('-date')
        if not history_by_user_name.exists():
            raise NotFound(f'History of user name {user_name} not found')

        return {
            'message':f'History of user {user_name}',
            'history': history_by_user_name
        }



    raise ValueError('code, unique_code, user_name you have to provided one of this filed')


