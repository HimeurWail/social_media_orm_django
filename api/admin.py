from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'bio', 'nb_followers', 'nb_followings', 'nb_posts', 'profile_picture', 'created_at')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)