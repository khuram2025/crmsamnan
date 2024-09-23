# crm/api.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Customer
from .serializers import CustomerSerializer
from rest_framework import viewsets
from .models import Technician

from rest_framework.permissions import IsAuthenticated

CustomUser = get_user_model()

class CustomerCreateAPI(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        create_account = serializer.validated_data.pop('create_account', False)
        customer = serializer.save(created_by=self.request.user, creation_method='API')
        
        if create_account:
            # Create a CustomUser for this customer
            password = CustomUser.objects.make_random_password()
            user = CustomUser.objects.create_user(
                mobile=customer.mobile_number,
                password=password
            )
            customer.user = user
            customer.save()
            
            # You might want to send this password to the customer via SMS
            # For now, we'll just include it in the response
            return Response({
                "message": "Customer created successfully with an account",
                "temporary_password": password
            })
        else:
            return Response({
                "message": "Customer created successfully without an account"
            })

class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        create_account = serializer.validated_data.pop('create_account', False)
        technician = serializer.save(created_by=self.request.user)
        
        if create_account:
            password = CustomUser.objects.make_random_password()
            user = CustomUser.objects.create_user(
                mobile=technician.mobile_number,
                password=password
            )
            technician.user = user
            technician.save()
            
            # You might want to send this password to the technician via SMS
            # For now, we'll just include it in the response
            self.response_data = {
                "message": "Technician created successfully with an account",
                "temporary_password": password
            }
        else:
            self.response_data = {
                "message": "Technician created successfully without an account"
            }

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data.update(self.response_data)
        return response

# crm/api.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Schedule, TechnicianSchedule
from .serializers import ScheduleSerializer, TechnicianScheduleSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        schedule = serializer.save(created_by=self.request.user)
        self.create_slots(schedule)

    def perform_update(self, serializer):
        schedule = serializer.save()
        schedule.slots.all().delete()
        self.create_slots(schedule)

    def create_slots(self, schedule):
        from .views import create_slots
        create_slots(schedule)

class TechnicianScheduleViewSet(viewsets.ModelViewSet):
    queryset = TechnicianSchedule.objects.all()
    serializer_class = TechnicianScheduleSerializer
    permission_classes = [IsAuthenticated]

# crm/api.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        technician_id = request.query_params.get('technician')
        date = request.query_params.get('date')

        if not technician_id or not date:
            return Response({'error': 'Both technician and date are required.'}, status=400)

        # Use the same logic as in the get_available_slots view
        # Return available slots for the given technician and date

    def perform_create(self, serializer):
        serializer.save()
        # You might want to add additional logic here, such as sending notifications