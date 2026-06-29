from django import forms
from django.contrib.auth.models import User
from .models import Document, InternshipReport, UserProfile, Internship, InternshipAssignment, Project, WeeklyReport, FinalReport, Task


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'description', 'is_final_report']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du document'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '*/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optionnel)'
            }),
            'is_final_report': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class ProfileEditForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Prénom'
    }))
    last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom'
    }))
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'department']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Département'
            }),
        }


class InternshipReportForm(forms.ModelForm):
    class Meta:
        model = InternshipReport
        fields = ['project', 'task', 'title', 'description', 'achievements', 'lessons_learned', 'recommendation', 'attachment', 'screenshot']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'form-control',
            }),
            'task': forms.Select(attrs={
                'class': 'form-control',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du rapport'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description générale du stage'
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Réalisations et contributions'
            }),
            'lessons_learned': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Compétences acquises et leçons apprises'
            }),
            'recommendation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Recommandations et suggestions (optionnel)'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '*/*'
            }),
            'screenshot': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class InternshipReportValidationForm(forms.ModelForm):
    """Form for mentor to validate internship reports"""
    class Meta:
        model = InternshipReport
        fields = ['validation_status', 'validation_comments']
        widgets = {
            'validation_status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'validation_comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaires de validation (optionnel)'
            }),
        }


class InternshipForm(forms.ModelForm):
    """Form to create and edit internship positions"""
    class Meta:
        model = Internship
        fields = ['title', 'description', 'department', 'start_date', 'end_date', 'requirements', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du stage'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du stage'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Département'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prérequis et compétences requises'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class InternshipAssignmentForm(forms.ModelForm):
    """Form to assign stagiaires to internships and assign mentors"""
    stagiaire = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='stagiaire'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Sélectionner un stagiaire'
        }),
        label="Stagiaire"
    )
    
    mentor = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='encadarant'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Sélectionner un mentor'
        }),
        label="Mentor",
        required=False
    )
    
    class Meta:
        model = InternshipAssignment
        fields = ['stagiaire', 'mentor', 'start_date', 'end_date', 'status', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes additionnelles (optionnel)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter stagiaires and mentors properly
        try:
            self.fields['stagiaire'].queryset = User.objects.filter(profile__role='stagiaire')
        except:
            pass
        
        try:
            self.fields['mentor'].queryset = User.objects.filter(profile__role='encadarant')
        except:
            pass


class ProjectForm(forms.ModelForm):
    """Form for mentor to create projects"""
    stagiaire = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='stagiaire'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Sélectionner un stagiaire'
        }),
        label="Stagiaire"
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'stagiaire', 'start_date', 'end_date', 'objectives', 'deliverables']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du projet'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description du projet'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'objectives': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objectifs du projet'
            }),
            'deliverables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Livrables attendus'
            }),
        }


class WeeklyReportForm(forms.ModelForm):
    """Form for stagiaires to submit weekly reports"""
    class Meta:
        model = WeeklyReport
        fields = ['work_done', 'challenges', 'next_steps', 'screenshot', 'attachment']
        widgets = {
            'work_done': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez le travail effectué cette semaine'
            }),
            'challenges': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Défis rencontrés (optionnel)'
            }),
            'next_steps': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Prochaines étapes (optionnel)'
            }),
            'screenshot': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'placeholder': 'Capture d\'écran (optionnel)'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '*/*',
                'placeholder': 'Document joint (optionnel)'
            }),
        }


class WeeklyReportEvaluationForm(forms.ModelForm):
    """Form for mentor to evaluate weekly reports"""
    class Meta:
        model = WeeklyReport
        fields = ['status', 'mentor_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mentor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaires et remarques du mentor'
            }),
        }


class FinalReportForm(forms.ModelForm):
    """Form for stagiaires to submit final report"""
    class Meta:
        model = FinalReport
        fields = ['summary', 'achievements', 'lessons_learned', 'recommendations', 'pdf_file']
        widgets = {
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Résumé du stage'
            }),
            'achievements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Réalisations et contributions'
            }),
            'lessons_learned': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Compétences acquises et leçons apprises'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Recommandations et suggestions (optionnel)'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
        }


class FinalReportEvaluationForm(forms.ModelForm):
    """Form for mentor to evaluate final report"""
    class Meta:
        model = FinalReport
        fields = ['status', 'mentor_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'mentor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaires et remarques du mentor'
            }),
        }


class TaskForm(forms.ModelForm):
    """Form for mentor to create and edit tasks"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'week_number', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la tâche'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la tâche'
            }),
            'week_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de la semaine',
                'min': '1'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


class TaskStatusUpdateForm(forms.ModelForm):
    """Form for stagiaires to update task status"""
    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

