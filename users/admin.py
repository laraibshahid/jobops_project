from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django import forms
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active', 'is_staff', 'is_superuser')


class BulkPasswordChangeForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords don't match.")
        return cleaned_data


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'created_at', 'change_password_link')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    actions = ['bulk_change_password']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'phone'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/change-password/',
                self.admin_site.admin_view(self.change_password_view),
                name='users_user_change_password',
            ),
        ]
        return custom_urls + urls
    
    def change_password_view(self, request, user_id):
        """Custom view for changing user password"""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return HttpResponseRedirect(reverse('admin:users_user_changelist'))
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password and confirm_password:
                if new_password == confirm_password:
                    if len(new_password) >= 8:
                        user.set_password(new_password)
                        user.save()
                        messages.success(request, f'Password successfully changed for user {user.username}.')
                        return HttpResponseRedirect(reverse('admin:users_user_change', args=[user_id]))
                    else:
                        messages.error(request, 'Password must be at least 8 characters long.')
                else:
                    messages.error(request, 'Passwords do not match.')
            else:
                messages.error(request, 'Please provide both new password and confirmation.')
        
        # Render password change form
        context = {
            'title': f'Change Password for {user.username}',
            'user': user,
            'opts': self.model._meta,
            'has_change_permission': True,
        }
        return self.admin_site.admin_view(self.admin_site.admin_view)(
            request, 'admin/users/user/change_password.html', context
        )
    
    def change_password_link(self, obj):
        """Display a link to change password"""
        if obj.pk:
            url = reverse('admin:users_user_change_password', args=[obj.pk])
            return format_html('<a href="{}" class="button">Change Password</a>', url)
        return '-'
    change_password_link.short_description = 'Password Actions'
    
    def bulk_change_password(self, request, queryset):
        """Admin action to change passwords for multiple users"""
        if 'apply' in request.POST:
            form = BulkPasswordChangeForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                count = 0
                for user in queryset:
                    user.set_password(new_password)
                    user.save()
                    count += 1
                
                self.message_user(
                    request,
                    f'Successfully changed passwords for {count} users.',
                    messages.SUCCESS
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BulkPasswordChangeForm()
        
        context = {
            'title': 'Change Password for Selected Users',
            'form': form,
            'queryset': queryset,
            'opts': self.model._meta,
            'action': 'bulk_change_password',
        }
        return self.admin_site.admin_view(self.admin_site.admin_view)(
            request, 'admin/users/user/bulk_change_password.html', context
        )
    bulk_change_password.short_description = "Change password for selected users"
    
    def get_list_display(self, request):
        """Add password change link to list display"""
        list_display = list(super().get_list_display(request))
        if 'change_password_link' not in list_display:
            list_display.append('change_password_link')
        return list_display
