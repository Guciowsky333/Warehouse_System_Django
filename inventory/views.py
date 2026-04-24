from django.shortcuts import render
from inventory.services import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from inventory.serializers import *
from users.permissions import IsManager
from rest_framework.pagination import PageNumberPagination
from users import permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import serializers


# Create your views here.

class ChangeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Change Location component',
        description="""
        Changes the warehouse location of a component by its unique code.
    
        Business rules:
        - Fields unique_code and location_name are required
        - Component must exist in warehouse
        - Component cannot already be released to production
        - Target location must exist
        - Target location max weight cannot exceed 800 kg
        - Target location can not be EXTC because it is a special location to accepting components on storge
        - Authentication required
        """,
        request=ChangeLocationSerializer,
        responses={
            200: OpenApiResponse(description='Changed location successfully'),
            400: OpenApiResponse(description='Validation error / location overweight / component already released / EXTC location'),
            404: OpenApiResponse(description='Component or Location not found'),
            401: OpenApiResponse(description='Permission denied'),
        }
    )

    def patch(self, request):
        serializer = ChangeLocationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unique_code = serializer.validated_data['unique_code']
        location_name = serializer.validated_data['location_name']
        user = request.user

        try:
            result = change_location(unique_code, location_name, user)
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

    @extend_schema(
        summary='Release component',
        description="""
        Release component by its unique code from the warehouse to 
        specified department on production.
        
        Business rules:
        - Fields unique_code and department are required
        - Component must exist in warehouse
        - Component cannot already be released to production
        - Specified department must be in allow departments (5000, 5500, 5800, 6000)
        - Authentication required
        """,
        request=ReleasedComponentSerializer,
        responses={
            201 : OpenApiResponse(description='Release component successfully'),
            400 : OpenApiResponse(description='Validation error / wrong department / component already released'),
            404: OpenApiResponse(description='Component not found'),
            401: OpenApiResponse(description='Permission denied'),
        }
    )

    def post(self, request):
        serializer = ReleasedComponentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        unique_code = serializer.validated_data['unique_code']
        department = serializer.validated_data['department']
        user = request.user

        try:
            result = release_component(unique_code, department, user)
            return Response(result, status=201)


        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)


        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)


class CheckLocationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Check location',
        description="""
        Returns all components in specified location grouped by code
        order by total quantity
        
        Business rules:
        - Field location is required
        - Location must exist in the warehouse
        - Authentication required
        """,
        parameters=[
            OpenApiParameter(name='location_name',type=str, required=True)
        ],
        responses={
            200 : OpenApiResponse(description='List of all components on specified location'),
            400 : OpenApiResponse(description='Location is required'),
            404: OpenApiResponse(description='Location not found'),
            401: OpenApiResponse(description='Permission denied'),
        }

    )

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

    @extend_schema(
        summary='Check stock of component',
        description="""
        Returns all single object of component and its location with specified code sorted by FIFO
        (First in First out)
        
        Business rules:
        - Field code is required
        - Specified code must exist in warehouse
        - Authentication required
        """,
        parameters=[
            OpenApiParameter(name='code',type=str, required=True)
        ],
        responses={
            200 : OpenApiResponse(description='List of all components with specified code sorted by FIFO'),
            400 : OpenApiResponse(description='Code is required'),
            404: OpenApiResponse(description='Code not found'),
            401: OpenApiResponse(description='Permission denied'),
        }
    )

    def get(self, request):
        code = request.query_params.get('code')

        try:
            # We use pagination here because in the stock we can have a lot of components
            queryset = check_component(code)

            paginator = PageNumberPagination()
            paginator.page_size = 10

            # List all components sorted by FIFO
            page = paginator.paginate_queryset(queryset, request)

            serializer = self.serializer_class(page, many=True)

            return paginator.get_paginated_response(serializer.data)

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

    @extend_schema(
        summary='Check stock of component',
        description="""
        Returns all locations of components with specified code grouped by location sorted by
        total_quantity descending on this location 
        
        Business rules:
        - Field code is required
        - Specified code must exist in warehouse
        - Authentication required
        """,
        parameters=[
            OpenApiParameter(name='code',type=str, required=True)
        ],
        responses={
            200: OpenApiResponse(description='List of all components with specified code grouped by location sorted by total quantity'),
            400 : OpenApiResponse(description='Code is required'),
            404: OpenApiResponse(description='Code not found'),
            401: OpenApiResponse(description='Permission denied'),
        }
    )

    def get(self, request):
        code = request.query_params.get('code')

        try:
            components = check_component_grouped(code)
            return Response({
                "message": f'All locations for component {code}',
                "components": list(components)
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

    @extend_schema(
        summary='Show quantity of component in department',
        description="""
        Returns total quantity and total boxes of component with specified code on specified department
        
        business rules:
        - Field code and department are required
        - Specified department must be in allow departments (5000, 5500, 5800, 6000)
        - Specified code must exist in ReleasedComponent objects
        - Authentication required
        """,
        parameters=[
            OpenApiParameter(name='code',type=str, required=True),
            OpenApiParameter(name='department',type=str, required=True)
        ],
        responses={
            200: OpenApiResponse(description='Total quantity of component in department'),
            400 : OpenApiResponse(description='Code and department are required / wrong department'),
            404: OpenApiResponse(description='Code not found'),
            401: OpenApiResponse(description='Permission denied'),
        }
    )

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

    @extend_schema(
        summary='Show quantity of component in stock',
        description="""
        Returns total quantity and total boxes of component with specified code in stock
        
        business rules:
        - Field code is required
        - Specified code must exist in warehouse
        - Authentication required
        """,
        parameters=[
            OpenApiParameter(name='code',type=str, required=True),
        ],
        responses = {
            200: OpenApiResponse(description='Total quantity of component in stock'),
            400 : OpenApiResponse(description='Code is required'),
            404: OpenApiResponse(description='Code not found'),
            401: OpenApiResponse(description='Permission denied'),
        }
    )

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
        user = request.user

        try:
            result = undo_component(unique_code, location, user)
            return Response(result, status=201)

        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)

        except NotFound as e:
            return Response({
                "message": str(e)
            },status=404)


class ReceivingComponentView(APIView):

    # only users with the manager role can receive components in the warehous
    permission_classes = [IsAuthenticated, IsManager]
    def post(self, request):
        code = request.data.get('code')
        quantity = request.data.get('quantity')
        weight = request.data.get('weight')

        try:
            result = receiving_the_component_into_the_warehouse(code, weight, quantity)
            return Response(result,status=201)

        except ValueError as e:
            return Response({
                'message':str(e)
            },status=400)