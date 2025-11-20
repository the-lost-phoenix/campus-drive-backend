from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import User, TrainerProfile, TimeSlot, Booking, LearnerProfile, Review
from .serializers import (
    UserRegistrationSerializer, TrainerListSerializer, 
    TimeSlotSerializer, BookingSerializer, ReviewSerializer
)

# --- AUTHENTICATION ---

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'is_learner': user.is_learner,
                'is_trainer': user.is_trainer
            })
        else:
            return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


# --- PROFILE MANAGEMENT (UPDATED) ---

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "first_name": user.first_name,
            "email": user.email,
            "phone": user.phone_number,
            "role": "Trainer" if user.is_trainer else "Learner",
            # Get Profile Pic URL
            "profile_pic": user.trainer_profile.profile_pic.url if user.is_trainer and user.trainer_profile.profile_pic else (
                           user.learner_profile.profile_pic.url if user.is_learner and user.learner_profile.profile_pic else None)
        }
        
        if user.is_trainer:
            data['car_model'] = user.trainer_profile.car_model
            data['hourly_rate'] = user.trainer_profile.hourly_rate
            data['upi_id'] = user.trainer_profile.upi_id
            data['is_verified'] = user.trainer_profile.is_verified
            # Get DL Image URL
            data['dl_image'] = user.trainer_profile.dl_image.url if user.trainer_profile.dl_image else None
            
        return Response(data)

    def patch(self, request):
        user = request.user
        # Update Basic Info
        if 'first_name' in request.data: user.first_name = request.data['first_name']
        if 'phone' in request.data: user.phone_number = request.data['phone']
        if 'email' in request.data: user.email = request.data['email']
        user.save()

        profile = None
        if user.is_trainer:
            profile = user.trainer_profile
            if 'car_model' in request.data: profile.car_model = request.data['car_model']
            if 'hourly_rate' in request.data: profile.hourly_rate = request.data['hourly_rate']
            if 'upi_id' in request.data: profile.upi_id = request.data['upi_id']
            
            # Handle DL Upload
            if 'dl_image' in request.FILES:
                profile.dl_image = request.FILES['dl_image']

        elif user.is_learner:
            profile = user.learner_profile
        
        # Handle Profile Pic Upload
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
            
        if profile:
            profile.save()
        
        return Response({"status": "updated"})


# --- LEARNER FEATURES ---

class TrainerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TrainerListSerializer
    def get_queryset(self):
        return TrainerProfile.objects.filter(is_verified=True)

class TrainerSlotsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimeSlotSerializer
    def get_queryset(self):
        trainer_id = self.kwargs['trainer_id']
        return TimeSlot.objects.filter(trainer_id=trainer_id, is_booked=False)

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        slot_id = request.data.get('slot_id')
        try:
            slot = TimeSlot.objects.get(id=slot_id)
            if slot.is_booked:
                return Response({"error": "Slot already booked!"}, status=status.HTTP_400_BAD_REQUEST)
            
            learner = request.user.learner_profile
            booking = Booking.objects.create(learner=learner, slot=slot, status='CONFIRMED')
            
            slot.is_booked = True
            slot.save()
            
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LearnerBookingsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    def get_queryset(self):
        try:
            return Booking.objects.filter(learner=self.request.user.learner_profile).order_by('-created_at')
        except:
            return []

class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            booking_id = request.data.get('booking_id')
            booking = Booking.objects.get(id=booking_id)
            if booking.learner.user != request.user:
                return Response({"error": "Unauthorized"}, status=403)
            
            Review.objects.create(
                trainer=booking.slot.trainer,
                learner=booking.learner,
                rating=request.data.get('rating'),
                comment=request.data.get('comment')
            )
            return Response({"status": "Review Added"})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


# --- TRAINER FEATURES ---

class CreateTrainerSlotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_trainer:
            return Response({"error": "Only trainers can add slots"}, status=403)
            
        try:
            trainer_profile = request.user.trainer_profile
            date = request.data.get('date')
            time = request.data.get('time')
            
            slot = TimeSlot.objects.create(
                trainer=trainer_profile,
                date=date,
                time=time,
                is_booked=False
            )
            return Response(TimeSlotSerializer(slot).data, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class TrainerScheduleView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimeSlotSerializer

    def get_queryset(self):
        if not self.request.user.is_trainer:
            return []
        return TimeSlot.objects.filter(trainer=self.request.user.trainer_profile).order_by('date', 'time')

class CompleteBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            slot = TimeSlot.objects.get(id=request.data.get('slot_id'))
            if slot.trainer.user != request.user: return Response({"error": "Not your slot"}, status=403)
            booking = slot.booking
            booking.status = 'COMPLETED'
            booking.save()
            return Response({"status": "Completed"})
        except: return Response({"error": "Error"}, status=400)