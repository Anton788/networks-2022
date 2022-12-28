from Users.models import User, UserCompanyRelationAuthToken, UserCompanyRelation

from funcy import first, walk
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register out own model admin, based on the default UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # inlines = (AccessGroupsInline, AchievementsInline,)

    # def get_form(self, request, obj=None, **kwargs):
    #     kwargs['widgets'] = {
    #         'nickname': forms.TextInput(attrs={'placeholder': obj.get_nickname()})
    #     }
    #     return super().get_form(request, obj, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Searching and filtering
        # self.search_fields += ('vk_id',)
        # self.list_filter += ('is_teacher',)
        # self.list_display += ('vk_id',)  # don't forget the commas

        # Editing
        def extend_fieldset(fieldset):
            name, options = fieldset
            # # if name == 'Permissions':
            #     fields = list(options['fields'])
            #     fields.insert(3, 'is_teacher')
            #     options['fields'] = tuple(fields)
            if name == 'Personal info':
                options['fields'] += (
                    'middle_name',
                    'country',
                    'city',
                    'date_of_birth',
                    'telephone',
                    'telegram_id',
                    'change_password_date',
                    'organization_account',
                )
            return (name, options)

        self.fieldsets = walk(extend_fieldset, self.fieldsets)


@admin.register(UserCompanyRelationAuthToken)
class UserCompanyRelationAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')
    search_fields = ('user', 'key', )
    autocomplete_fields = ('user', )


@admin.register(UserCompanyRelation)
class UserCompanyRelationAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role')
    search_fields = ('user', 'company', )
    autocomplete_fields = ('user', 'creator', 'company', )
