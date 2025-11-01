from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

admin.site.site_header = "Prosignum Administration"
admin.site.site_title = "Prosignum Admin"
admin.site.index_title = "Prosignum Management"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('swiyu/', include('swiyu.urls')),
]

urlpatterns += i18n_patterns(
    path('', core_views.home, name='home'),
    path('profile/', core_views.profile, name='profile'),
    path('initiative/<int:initiative_id>/sign/', core_views.sign_initiative, name='sign_initiative'),
    path('logout/', core_views.logout_view, name='logout'),
    path('legal/', core_views.legal_notice, name='legal'),
    path('impressum/', core_views.impressum, name='impressum'),
    path('contact/', core_views.contact, name='contact'),
    prefix_default_language=True,
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
