from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TrainerProfile, LearnerProfile, TimeSlot, Booking

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('is_learner', 'is_trainer', 'phone_number')}),
    )
    list_display = ('username', 'is_learner', 'is_trainer')

admin.site.register(User, CustomUserAdmin)
admin.site.register(TrainerProfile)
admin.site.register(LearnerProfile)
admin.site.register(TimeSlot) # <-- Added
admin.site.register(Booking)  # <-- Added