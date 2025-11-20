from django.urls import path
from .views import (
    CustomLoginView, UserRegistrationView, TrainerListView, 
    TrainerSlotsView, CreateBookingView, LearnerBookingsView,
    CreateTrainerSlotView, TrainerScheduleView, UserProfileView # <-- New
)

urlpatterns = [
    path('signup/', UserRegistrationView.as_view()),
    path('login/', CustomLoginView.as_view()),
    path('trainers/', TrainerListView.as_view()),
    path('trainers/<int:trainer_id>/slots/', TrainerSlotsView.as_view()),
    path('book/', CreateBookingView.as_view()),
    path('my-bookings/', LearnerBookingsView.as_view()),
    path('trainer/add-slot/', CreateTrainerSlotView.as_view()),
    path('trainer/schedule/', TrainerScheduleView.as_view()),
    
    # New Profile Link
    path('profile/', UserProfileView.as_view()),
]