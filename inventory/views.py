from django.shortcuts import render
from inventory.services import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from inventory.serializers import ComponentSerializer

from users import permissions


# Create your views here.

class ChangeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        unique_code = request.data.get('unique_code')
        location = request.data.get('location')

        try:
            result = change_location(unique_code, location)
            return Response(result, status=200)

        # if user provided inappropriate data
        except ValueError as e:
            return Response({
                "message":str(e)
            }, status=400)

        # if user provided data that not exist in database
        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)


class ReleasedComponentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        unique_code = request.data.get('unique_code')
        department = request.data.get('department')

        try:
            result = release_component(unique_code, department)
            return Response(result, status=201)

        # if user provided inappropriate data
        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)

        # if user provided data that not exist in database
        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)


class CheckLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        location = request.query_params.get('location_name')

        try:
            components = check_location(location)
            return Response({
                "message":f"All components on location {location}",

                # Function check_component returns QuerySet of components so we have to convert it to list
                "components":list(components)
            },status=200)



        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)


        except NotFound as e:
            return Response({
                "message": str(e)
            },status=404)

class CheckComponentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ComponentSerializer

    def get(self, request):
        code = request.query_params.get('code')

        try:
            components = check_component(code)
            serializer = self.serializer_class(components, many=True)
            return Response({
                "message":f'All locations for component {code}',
                'components':serializer.data,
            }, status=200)

        except ValueError as e:
            return Response({
                "message":str(e)

            },status=400)

        except NotFound as e:
            return Response({
                "message": str(e)
            },status=404)


class CheckComponentGroupedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code')

        try:
            components = check_component_grouped(code)
            return Response({
                "message":f'All locations for component {code}',
                "components":list(components)
            }, status=200)

        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)

        except NotFound as e:
            return Response({
                "message": str(e)
            },status=404)


class ShowQuantityInDepartmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code')
        department = request.query_params.get('department')

        try:
            total_boxes, total_quantity = component_quantity_at_department(code, department)
            return Response({
                'code':f'{code}',
                'department':f'{department}',
                'total_quantity': total_quantity,
                'total_boxes': total_boxes,
            }, status=200)

        except ValueError as e:
            return Response({
                "message":str(e)
            }, status=400)

        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)

class ShowQuantityInStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code')

        try:
            total_boxes, total_quantity = component_quantity_at_stock(code)
            return Response({
                'code':f'{code}',
                'total_boxes': total_boxes,
                'total_quantity': total_quantity,
            }, status=200)

        except ValueError as e:
            return Response({
                "message":str(e)
            }, status=400)

        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)


class UndoComponentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        unique_code = request.data.get('unique_code')
        location = request.data.get('location')

        try:
            result = undo_component(unique_code, location)
            return Response(result, status=201)

        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)

        except NotFound as e:
            return Response({
                "message": str(e)
            },status=404)