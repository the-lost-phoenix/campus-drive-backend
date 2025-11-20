from rest_framework import serializers
from .models import User, LearnerProfile, TrainerProfile, TimeSlot, Booking, Review

# 1. REGISTRATION SERIALIZER
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)
    # New: Accept Real Name
    first_name = serializers.CharField(required=True)
    # New: Accept UPI ID (only for trainers, optional for learners)
    upi_id = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password', 'is_learner', 'is_trainer', 'phone_number', 'upi_id']

    def create(self, validated_data):
        # Extract upi_id so it doesn't break User creation
        upi_id = validated_data.pop('upi_id', '')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_learner=validated_data.get('is_learner', False),
            is_trainer=validated_data.get('is_trainer', False),
            phone_number=validated_data['phone_number']
        )
        
        if user.is_trainer:
            TrainerProfile.objects.create(
                user=user, 
                dl_number="PENDING", 
                car_model="Not Set", 
                upi_id=upi_id 
            )
        elif user.is_learner:
            LearnerProfile.objects.create(user=user)
            
        return user

# 2. TRAINER LIST SERIALIZER
class TrainerListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    phone = serializers.CharField(source='user.phone_number')
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = TrainerProfile
        fields = ['id', 'username', 'first_name', 'phone', 'car_model', 'hourly_rate', 'bio', 'is_verified', 'average_rating', 'profile_pic', 'upi_id']

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        return sum([r.rating for r in reviews]) / len(reviews) if reviews else 0

# 3. SLOT SERIALIZER
class TimeSlotSerializer(serializers.ModelSerializer):
    # Show Student Name & Phone to the Trainer
    booked_by = serializers.CharField(source='booking.learner.user.first_name', read_only=True, default=None)
    student_phone = serializers.CharField(source='booking.learner.user.phone_number', read_only=True, default=None)

    class Meta:
        model = TimeSlot
        fields = ['id', 'date', 'time', 'is_booked', 'booked_by', 'student_phone']

# 4. BOOKING SERIALIZER
class BookingSerializer(serializers.ModelSerializer):
    slot_info = TimeSlotSerializer(source='slot', read_only=True)
    trainer_name = serializers.CharField(source='slot.trainer.user.first_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'slot', 'slot_info', 'trainer_name', 'status', 'created_at']

# 5. REVIEW SERIALIZER
class ReviewSerializer(serializers.ModelSerializer):
    learner_name = serializers.CharField(source='learner.user.first_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'learner_name', 'rating', 'comment', 'created_at']