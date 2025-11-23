from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import DemoForm
from .serializers import DemoFormSerializer
from rest_framework.views import APIView


class CreateDemoView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = DemoFormSerializer(data=request.data)
        if serializer.is_valid():
            val_data = serializer.validated_data
            MAPP = {
                1: 'Управляющая компания',
                2: 'Застройщик',
                3: 'Охранное предприятие',
                4: 'Другое',   
            }
            val_data['org_type'] = MAPP.get(val_data['organisation_type'])
            del val_data['organisation_type']
            demo = DemoForm.objects.create(**val_data)
            return Response(DemoFormSerializer(demo).data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)