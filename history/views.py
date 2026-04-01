
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from history.models import ComponentHistory
from history.serializers import HistorySerializer
# Create your views here.


class ComponentHistoryByCodeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HistorySerializer

    def get(self, request):
        code = request.query_params.get('code')
        action = request.query_params.get('action')

        queryset = ComponentHistory.objects.filter(code=code)

        if action:
            queryset = queryset.filter(action=action)

        if not queryset.exists():
            raise NotFound(f'Invalid code or action')

        return Response({
            'message':f'History of code {code}',
            'history':self.serializer_class(queryset, many=True).data
        })