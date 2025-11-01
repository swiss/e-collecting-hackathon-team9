from django.contrib import admin
from django.utils import timezone
from django.db.models import Count, Q
from unfold.admin import ModelAdmin
from .models import Municipality, Initiative, Participant, Signature


@admin.register(Municipality)
class MunicipalityAdmin(ModelAdmin):
    list_display = ['name', 'canton', 'bfs_number', 'postal_code']
    list_filter = ['canton']
    search_fields = ['name', 'bfs_number', 'canton']
    ordering = ['name']

    def has_add_permission(self, request):
        # Only superusers can add municipalities
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Only superusers can change municipalities
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete municipalities
        return request.user.is_superuser


@admin.register(Initiative)
class InitiativeAdmin(ModelAdmin):
    list_display = ['title', 'status', 'creator', 'created_at', 'total_signatures', 'get_progress']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_signatures', 'get_progress', 'signatures_by_municipality']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'url', 'banner_image', 'status')
        }),
        ('Collection Period', {
            'fields': ('collection_start_date', 'collection_end_date', 'target_signatures')
        }),
        ('Metadata', {
            'fields': ('creator', 'created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_signatures', 'get_progress', 'signatures_by_municipality'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Initiative creators only see their own initiatives
        if request.user.has_perm('core.can_create_initiative'):
            return qs.filter(creator=request.user)
        return qs.none()

    def has_add_permission(self, request):
        # Only users with can_create_initiative permission
        return request.user.has_perm('core.can_create_initiative')

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.creator == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.creator = request.user
        super().save_model(request, obj, form, change)

    def total_signatures(self, obj):
        return obj.get_total_signatures()
    total_signatures.short_description = 'Total Accepted Signatures'

    def get_progress(self, obj):
        percentage = obj.get_progress_percentage()
        return f"{percentage}% ({obj.get_total_signatures()}/{obj.target_signatures})"
    get_progress.short_description = 'Progress'

    def signatures_by_municipality(self, obj):
        results = obj.get_signatures_by_municipality()
        if not results:
            return "No accepted signatures yet"
        output = "<table style='width:100%'><tr><th>Municipality</th><th>Count</th></tr>"
        for result in results:
            output += f"<tr><td>{result['municipality__name']} ({result['municipality__canton']})</td><td>{result['count']}</td></tr>"
        output += "</table>"
        return output
    signatures_by_municipality.short_description = 'Signatures by Municipality'
    signatures_by_municipality.allow_tags = True


@admin.register(Participant)
class ParticipantAdmin(ModelAdmin):
    list_display = ['get_full_name', 'ahv_number', 'get_birth_date', 'created_at']
    search_fields = ['swiyu_profile__given_name', 'swiyu_profile__family_name', 'user__username', 'ahv_number']
    readonly_fields = ['user', 'swiyu_profile', 'ahv_number', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.swiyu_profile.given_name} {obj.swiyu_profile.family_name}"
    get_full_name.short_description = 'Full Name'

    def get_birth_date(self, obj):
        return obj.swiyu_profile.birth_date
    get_birth_date.short_description = 'Birth Date'

    def has_add_permission(self, request):
        # Participants are created automatically through Swiyu login
        return False

    def has_change_permission(self, request, obj=None):
        # Read-only
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete
        return request.user.is_superuser


@admin.register(Signature)
class SignatureAdmin(ModelAdmin):
    list_display = ['get_participant_name', 'initiative', 'municipality', 'status', 'signed_at']
    list_filter = ['status', 'municipality__canton', 'signed_at']
    search_fields = ['participant__swiyu_profile__given_name', 'participant__swiyu_profile__family_name', 'initiative__title']
    readonly_fields = ['participant', 'initiative', 'given_name', 'family_name', 'birth_date', 'address', 'id_number', 'signed_at', 'updated_at']
    actions = ['accept_signatures', 'reject_signatures']

    fieldsets = (
        ('Signature Information', {
            'fields': ('initiative', 'participant', 'municipality', 'status')
        }),
        ('Personal Data', {
            'fields': ('given_name', 'family_name', 'birth_date', 'address', 'id_number')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes')
        }),
        ('Timestamps', {
            'fields': ('signed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        # Municipality reviewers only see signatures from their municipalities
        if request.user.has_perm('core.can_review_signatures'):
            # Get municipalities this user can review (based on group membership)
            user_groups = request.user.groups.values_list('name', flat=True)
            reviewer_municipalities = []

            for group_name in user_groups:
                if group_name.startswith('Municipality_') and group_name.endswith('_Reviewers'):
                    # Extract municipality name from group name
                    # Format: Municipality_{name}_Reviewers
                    mun_name = group_name[13:-10]  # Remove prefix and suffix
                    reviewer_municipalities.append(mun_name)

            if reviewer_municipalities:
                return qs.filter(municipality__name__in=reviewer_municipalities)

        return qs.none()

    def has_add_permission(self, request):
        # Signatures are created through the public signing flow
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        # Municipality reviewers can change signatures in their municipalities
        if request.user.has_perm('core.can_review_signatures') and obj:
            user_groups = request.user.groups.values_list('name', flat=True)
            for group_name in user_groups:
                if group_name.startswith('Municipality_') and group_name.endswith('_Reviewers'):
                    mun_name = group_name[13:-10]
                    if obj.municipality.name == mun_name:
                        return True

        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete
        return request.user.is_superuser

    def get_participant_name(self, obj):
        return str(obj.participant)
    get_participant_name.short_description = 'Participant'

    def accept_signatures(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='accepted',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} signature(s) accepted.')
    accept_signatures.short_description = 'Accept selected signatures'

    def reject_signatures(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'{updated} signature(s) rejected.')
    reject_signatures.short_description = 'Reject selected signatures'
