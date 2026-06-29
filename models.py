from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
     
        ('rh', 'Ressource Humaine'),

        ('encadarant', 'mentor'),
        ('stagiaire', 'Stagiaire'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='stagiaire')
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('completed', 'Complété'),
    ]
    
    stagiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    manager = models.CharField(max_length=200, blank=True, null=True)
    objectives = models.TextField(blank=True)
    deliverables = models.TextField(blank=True)
    progress = models.IntegerField(default=0)  # 0-100
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.stagiaire.username}"


class Task(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Non commencé'),
        ('in_progress', 'En cours'),
        ('completed', 'Complété'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    week_number = models.IntegerField()  # For weekly tracking
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['week_number', 'due_date']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"


class Document(models.Model):
    stagiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/%Y/%m/')
    description = models.TextField(blank=True)
    is_final_report = models.BooleanField(default=False, help_text="Marquer comme rapport final")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.stagiaire.username}"


class InternshipReport(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('reviewed', 'Examiné'),
    ]
    
    VALIDATION_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    stagiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internship_reports')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    title = models.CharField(max_length=200)
    description = models.TextField()
    achievements = models.TextField()
    lessons_learned = models.TextField()
    recommendation = models.TextField(blank=True)
    attachment = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    screenshot = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Validation fields
    validation_status = models.CharField(max_length=20, choices=VALIDATION_CHOICES, default='pending')
    validation_comments = models.TextField(blank=True)
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validated_reports')
    validated_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Rapport de stage"
        verbose_name_plural = "Rapports de stage"
        ordering = ['-submitted_date']
    
    def __str__(self):
        return f"{self.title} - {self.stagiaire.username}"


class Internship(models.Model):
    """Model to manage internship positions"""
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('assigned', 'Assigné'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    department = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Stage"
        verbose_name_plural = "Stages"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.department}"


class InternshipAssignment(models.Model):
    """Model to assign stagiaires to internships"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Rejeté'),
        ('completed', 'Complété'),
    ]
    
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='assignments')
    stagiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='internship_assignments')
    mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_stagiaires')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Assignation de stage"
        verbose_name_plural = "Assignations de stages"
        ordering = ['-assigned_date']
        unique_together = ('internship', 'stagiaire')
    
    def __str__(self):
        return f"{self.stagiaire.username} - {self.internship.title}"


class WeeklyReport(models.Model):
    """Model for weekly reports submitted by stagiaires"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='weekly_reports')
    stagiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_reports')
    week_number = models.IntegerField()
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    
    # Report content
    work_done = models.TextField()  # What was done
    challenges = models.TextField(blank=True)  # Challenges faced
    next_steps = models.TextField(blank=True)  # Next steps
    screenshot = models.FileField(upload_to='weekly_reports/%Y/%m/', null=True, blank=True)
    attachment = models.FileField(upload_to='weekly_reports/%Y/%m/', null=True, blank=True)
    
    # Status and validation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_date = models.DateTimeField(null=True, blank=True)
    
    # Mentor validation
    mentor_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_weekly_reports')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rapport Hebdomadaire"
        verbose_name_plural = "Rapports Hebdomadaires"
        ordering = ['-week_start_date']
        unique_together = ('project', 'week_number')
    
    def __str__(self):
        return f"Semaine {self.week_number} - {self.stagiaire.username} ({self.project.title})"


class FinalReport(models.Model):
    """Model for final internship report at the end of stage"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('submitted', 'Soumis'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='final_report')
    stagiaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='final_reports')
    
    # Report content
    summary = models.TextField()
    achievements = models.TextField()
    lessons_learned = models.TextField()
    recommendations = models.TextField(blank=True)
    
    # PDF file
    pdf_file = models.FileField(upload_to='final_reports/%Y/%m/', null=True, blank=True)
    
    # Status and validation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_date = models.DateTimeField(null=True, blank=True)
    
    # Mentor validation
    mentor_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_final_reports')
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rapport Final"
        verbose_name_plural = "Rapports Finaux"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rapport Final - {self.stagiaire.username} ({self.project.title})"

