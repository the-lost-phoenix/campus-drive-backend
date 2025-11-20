from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_learner = models.BooleanField(default=False)
    is_trainer = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15) 
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class TrainerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer_profile')
    
    # --- IMAGES ---
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    dl_image = models.ImageField(upload_to='dl_scans/', blank=True, null=True) # <--- THIS WAS MISSING
    
    # --- DETAILS ---
    dl_number = models.CharField(max_length=50, default="PENDING")
    upi_id = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. name@okaxis")
    is_verified = models.BooleanField(default=False)
    car_model = models.CharField(max_length=100, default="Not Set")
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, default=500.00)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Trainer: {self.user.username}"

class LearnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    college_id_image = models.ImageField(upload_to='college_ids/', blank=True, null=True)
    
    def __str__(self):
        return f"Learner: {self.user.username}"

class TimeSlot(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('trainer', 'date', 'time')

    def __str__(self):
        return f"{self.trainer.user.username} - {self.date} at {self.time}"

class Booking(models.Model):
    STATUS_CHOICES = (('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'))
    learner = models.ForeignKey(LearnerProfile, on_delete=models.CASCADE, related_name='bookings')
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking: {self.learner.user.username} -> {self.slot}"

class Review(models.Model):
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE, related_name='reviews')
    learner = models.ForeignKey(LearnerProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ for {self.trainer.user.username}"