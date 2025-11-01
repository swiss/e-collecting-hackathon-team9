from django.db import models
from django.contrib.auth.models import User
import uuid


class SwiyuVerification(models.Model):
    """Track Swiyu verification requests"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification_id = models.CharField(max_length=255, unique=True, db_index=True)
    verification_url = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Store verified claims when completed
    verified_claims = models.JSONField(null=True, blank=True)
    error_code = models.CharField(max_length=100, null=True, blank=True)

    # Link to user if this is for login
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['verification_id']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Verification {self.verification_id} - {self.status}"


class SwiyuUserProfile(models.Model):
    """Store Swiyu E-ID claims associated with user"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='swiyu_profile')

    # Swiss E-ID claims
    given_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=255, blank=True, default='')

    # Metadata
    eid_hash = models.CharField(max_length=64, unique=True, db_index=True)  # Hash of E-ID for matching
    verified_at = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Swiyu User Profile"
        verbose_name_plural = "Swiyu User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.given_name} {self.family_name}"
