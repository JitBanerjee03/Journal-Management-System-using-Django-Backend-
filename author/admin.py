from django.contrib import admin
from .models import Author

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_first_name', 'get_last_name', 'get_email', 'phone_number', 'country', 'get_is_active')
    list_filter = ('user__is_active', 'country', 'reviewer_interest')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_is_active(self, obj):
        return obj.user.is_active
    get_is_active.short_description = 'Active Status'

admin.site.register(Author, AuthorAdmin)
