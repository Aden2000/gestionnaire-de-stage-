from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Project, Task, Document, InternshipReport

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fields = ('role', 'department', 'phone', 'address')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'created_at')
    list_filter = ('role', 'department', 'created_at')
    search_fields = ('user__username', 'user__email', 'department')
    readonly_fields = ('created_at', 'updated_at')


# Register Project
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'stagiaire',  'status', 'progress', 'start_date', 'end_date')
    list_filter = ('status', 'created_at', 'start_date')
    search_fields = ('title', 'stagiaire__username',  'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('stagiaire', 'title', 'description')
        }),
        ('Détails du projet', {
            'fields': ('objectives', 'deliverables', 'manager', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Suivi', {
            'fields': ('progress', 'created_at', 'updated_at')
        }),
    )


# Register Task
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'week_number', 'due_date')
    list_filter = ('status', 'week_number', 'due_date', 'created_at')
    search_fields = ('title', 'project__title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('week_number', 'due_date')


# Register Document
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'stagiaire', 'uploaded_at', 'file')
    list_filter = ('uploaded_at', 'stagiaire')
    search_fields = ('title', 'stagiaire__username', 'description')
    readonly_fields = ('uploaded_at',)


# Register InternshipReport
@admin.register(InternshipReport)
class InternshipReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'stagiaire', 'status', 'submitted_date')
    list_filter = ('status', 'submitted_date', 'stagiaire')
    search_fields = ('title', 'stagiaire__username', 'description')
    readonly_fields = ('submitted_date',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('stagiaire', 'project', 'title', 'status')
        }),
        ('Contenu du rapport', {
            'fields': ('description', 'achievements', 'lessons_learned', 'recommendation')
        }),
        ('Dates', {
            'fields': ('submitted_date',)
        }),
    )
