from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class Municipality(models.Model):
    """Swiss municipality"""

    bfs_number = models.IntegerField(unique=True, db_index=True, help_text="Official BFS number")
    name = models.CharField(max_length=255, help_text="Municipality name (Gemeindename)")
    canton = models.CharField(max_length=2, help_text="Canton abbreviation (e.g., ZH, BE)")
    postal_code = models.CharField(max_length=10, blank=True, help_text="Primary postal code")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Municipality"
        verbose_name_plural = "Municipalities"
        ordering = ['name']
        indexes = [
            models.Index(fields=['bfs_number']),
            models.Index(fields=['canton', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.canton})"


class Initiative(models.Model):
    """Referendum/Initiative"""

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=500)
    description = models.TextField()
    url = models.URLField(max_length=500, blank=True, help_text="External URL with more information")
    banner_image = models.ImageField(upload_to='initiative_banners/', blank=True, null=True, help_text="Optional banner image")
    initiative_committee = models.TextField(blank=True, help_text="Initiative committee members and their right to withdraw")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Collection period
    collection_start_date = models.DateTimeField(null=True, blank=True, help_text="When signature collection starts")
    collection_end_date = models.DateTimeField(null=True, blank=True, help_text="When signature collection ends")

    # Target signatures required
    target_signatures = models.IntegerField(default=0, help_text="Number of signatures required")

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_initiatives')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Initiative"
        verbose_name_plural = "Initiatives"
        ordering = ['-created_at']
        permissions = [
            ('can_create_initiative', 'Can create initiatives'),
            ('can_view_initiative_totals', 'Can view initiative signature totals'),
        ]

    def __str__(self):
        return self.title

    def is_collecting(self):
        """Check if initiative is currently in collection period"""
        from django.utils import timezone
        now = timezone.now()

        if self.status != 'active':
            return False

        if self.collection_start_date and now < self.collection_start_date:
            return False

        if self.collection_end_date and now > self.collection_end_date:
            return False

        return True

    def get_total_signatures(self):
        """Get total accepted signatures"""
        return self.signatures.filter(status='accepted').count()

    def get_progress_percentage(self):
        """Get signature collection progress as percentage"""
        if self.target_signatures <= 0:
            return 0
        total = self.get_total_signatures()
        return min(100, int((total / self.target_signatures) * 100))

    def get_signatures_by_municipality(self):
        """Get accepted signatures grouped by municipality"""
        return (
            self.signatures
            .filter(status='accepted')
            .values('municipality__name', 'municipality__canton')
            .annotate(count=models.Count('id'))
            .order_by('municipality__name')
        )


class Participant(models.Model):
    """Citizen participating in signature collection (linked to Swiyu profile)"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participant_profile')

    # Links to Swiyu profile
    swiyu_profile = models.ForeignKey('swiyu.SwiyuUserProfile', on_delete=models.PROTECT)

    # AHV (Social Security) Number
    ahv_number = models.CharField(max_length=16, blank=True, null=True, db_index=True, help_text="Swiss AHV/AVS social security number")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Participant"
        verbose_name_plural = "Participants"
        indexes = [
            models.Index(fields=['ahv_number']),
        ]

    def __str__(self):
        return f"{self.swiyu_profile.given_name} {self.swiyu_profile.family_name}"


class Signature(models.Model):
    """Signature on an initiative"""

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='signatures')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='signatures')
    municipality = models.ForeignKey(Municipality, on_delete=models.PROTECT, related_name='signatures')

    # Signature data (collected at signing time)
    given_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    birth_date = models.DateField()

    # Address fields (Swiss official format)
    street_and_number = models.CharField(max_length=255, blank=True, help_text="Strasse und Hausnummer")
    postal_code = models.CharField(max_length=10, blank=True, help_text="PLZ")

    # Legacy address field (for backwards compatibility)
    address = models.TextField(blank=True)
    id_number = models.CharField(max_length=100, blank=True, help_text="National ID or similar")

    # Review status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_signatures')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Timestamps
    signed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Signature"
        verbose_name_plural = "Signatures"
        ordering = ['-signed_at']
        unique_together = [('initiative', 'participant')]
        indexes = [
            models.Index(fields=['initiative', 'status']),
            models.Index(fields=['municipality', 'status']),
            models.Index(fields=['participant', 'initiative']),
        ]
        permissions = [
            ('can_review_signatures', 'Can review signatures'),
        ]

    def __str__(self):
        return f"{self.participant} signed {self.initiative.title} ({self.status})"

    def clean(self):
        # Ensure participant can only sign once per initiative
        if not self.pk:  # Only check on creation
            existing = Signature.objects.filter(
                initiative=self.initiative,
                participant=self.participant
            ).exists()
            if existing:
                raise ValidationError("Participant has already signed this initiative.")


# Signal handlers
@receiver(post_save, sender=Municipality)
def create_municipality_group(sender, instance, created, **kwargs):
    """Automatically create a Django group for each municipality"""
    if created:
        # Create group with naming pattern: municipality_<name>
        group_name = f"municipality_{instance.name.lower().replace(' ', '_').replace('-', '_')}"
        Group.objects.get_or_create(name=group_name)
