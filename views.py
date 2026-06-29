from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.db import models
from datetime import datetime, timedelta
from .models import UserProfile, Project, Task, Document, InternshipReport, Internship, InternshipAssignment, WeeklyReport, FinalReport
from .forms import DocumentUploadForm, ProfileEditForm, InternshipReportForm, InternshipReportValidationForm, InternshipForm, InternshipAssignmentForm, ProjectForm, WeeklyReportForm, WeeklyReportEvaluationForm, FinalReportForm, FinalReportEvaluationForm, TaskForm, TaskStatusUpdateForm

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'auth/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, 'Vous êtes déconnecté.')
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    # Récupérer le profil utilisateur
    try:
        profile = UserProfile.objects.get(user=request.user)
        user_role = profile.role
    except UserProfile.DoesNotExist:
        user_role = 'stagiaire'
        # Créer un profil par défaut si inexistant
        profile = UserProfile.objects.create(user=request.user, role='stagiaire')
    
    context = {
        'user': request.user,
        'user_role': user_role,
        'profile': profile,
    }
    
    # Retourner un template spécifique selon le rôle
    if user_role == 'rh':
        # Ajouter les statistiques pour RH
        total_stagiaires = User.objects.filter(profile__role='stagiaire').count()
        total_internships = Internship.objects.count()
        active_internships = Internship.objects.filter(status='active').count()
        completed_internships = Internship.objects.filter(status='completed').count()
        
        # Récupérer les dernières assignations
        recent_assignments = InternshipAssignment.objects.all().order_by('-id')[:5]
        
        context['total_stagiaires'] = total_stagiaires
        context['total_internships'] = total_internships
        context['active_internships'] = active_internships
        context['completed_internships'] = completed_internships
        context['recent_assignments'] = recent_assignments
        
        return render(request, 'dashboard_rh.html', context)
    elif user_role == 'manager':
        return render(request, 'dashboard_manager.html', context)
    elif user_role == 'encadarant':
        # Ajouter les statistiques pour mentor
        projects = Project.objects.filter(mentor=request.user)
        context['projects'] = projects
        context['total_projects'] = projects.count()
        context['active_projects'] = projects.filter(status='active').count()
        context['completed_projects'] = projects.filter(status='completed').count()
        context['total_stagiaires'] = projects.values('stagiaire').distinct().count()
        
        # Récupérer les tâches de tous les projets du mentor
        project_ids = projects.values_list('id', flat=True)
        all_tasks = Task.objects.filter(project_id__in=project_ids).order_by('-created_at')[:10]
        context['all_tasks'] = all_tasks
        context['total_tasks'] = Task.objects.filter(project_id__in=project_ids).count()
        context['pending_tasks'] = Task.objects.filter(project_id__in=project_ids, status='not_started').count()
        context['in_progress_tasks'] = Task.objects.filter(project_id__in=project_ids, status='in_progress').count()
        
        return render(request, 'dashboard_mentor.html', context)
    elif user_role == 'admin':
        return render(request, 'dashboard_admin.html', context)
    elif user_role == 'stagiaire':
        return render(request, 'dashboard_stagiaire.html', context)
    else:
        return render(request, 'dashboard.html', context)


# ============= STAGIAIRE FEATURE VIEWS =============

@login_required(login_url='login')
def project_detail_view(request):
    """Display stagiaire's project details"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get all projects for this stagiaire
    projects = Project.objects.filter(stagiaire=request.user)
    
    context = {
        'projects': projects,
        'user': request.user,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required(login_url='login')
def task_list_view(request):
    """Display tasks grouped by week"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get projects for this stagiaire
    projects = Project.objects.filter(stagiaire=request.user)
    project_ids = projects.values_list('id', flat=True)
    
    # Get all tasks for these projects
    tasks = Task.objects.filter(project_id__in=project_ids).order_by('week_number', 'due_date')
    
    # Group tasks by week
    tasks_by_week = {}
    for task in tasks:
        week = task.week_number
        if week not in tasks_by_week:
            tasks_by_week[week] = []
        tasks_by_week[week].append(task)
    
    context = {
        'tasks': tasks,
        'tasks_by_week': tasks_by_week,
        'projects': projects,
        'user': request.user,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def stagiaire_task_update_view(request, task_id):
    """Allow stagiaire to update task status"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get the task and verify it belongs to this stagiaire's project
    task = get_object_or_404(Task, pk=task_id)
    
    # Verify the task belongs to one of the stagiaire's projects
    stagiaire_projects = Project.objects.filter(stagiaire=request.user)
    if task.project not in stagiaire_projects:
        messages.error(request, 'Accès refusé. Cette tâche ne vous appartient pas.')
        return redirect('task_list')
    
    if request.method == 'POST':
        form = TaskStatusUpdateForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            status_text = dict(task.STATUS_CHOICES).get(task.status, task.status)
            messages.success(request, f'Statut de la tâche "{task.title}" mis à jour en "{status_text}"!')
            return redirect('task_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = TaskStatusUpdateForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'project': task.project,
        'user': request.user,
    }
    return render(request, 'tasks/task_update_status.html', context)


@login_required(login_url='login')
def document_list_view(request):
    """Display all documents uploaded by stagiaire"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    documents = Document.objects.filter(stagiaire=request.user)
    form = DocumentUploadForm()
    
    context = {
        'documents': documents,
        'form': form,
        'user': request.user,
    }
    return render(request, 'documents/document_list.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def document_upload_view(request):
    """Handle document upload"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('document_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('document_list')
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.stagiaire = request.user
            
            # Get stagiaire's project
            try:
                project = Project.objects.filter(stagiaire=request.user).first()
                if project:
                    document.project = project
            except Project.DoesNotExist:
                pass
            
            document.save()
            
            if document.is_final_report:
                messages.success(request, 'Document téléchargé comme rapport final avec succès!')
            else:
                messages.success(request, 'Document téléchargé avec succès!')
            return redirect('document_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('document_list')
    
    return redirect('document_list')


@login_required(login_url='login')
def report_list_view(request):
    """Display all internship reports"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    reports = InternshipReport.objects.filter(stagiaire=request.user)
    
    context = {
        'reports': reports,
        'user': request.user,
    }
    return render(request, 'reports/report_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def report_create_view(request):
    """Create or edit internship report"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get all stagiaire's projects
    projects = Project.objects.filter(stagiaire=request.user)
    
    if not projects.exists():
        messages.error(request, 'Vous n\'avez pas de projet assigné. Veuillez contacter l\'administrateur.')
        return redirect('report_list')
    
    report_id = request.GET.get('id')
    report = None
    
    if report_id:
        report = get_object_or_404(InternshipReport, id=report_id, stagiaire=request.user)
    
    if request.method == 'POST':
        form = InternshipReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            # Verify the selected project belongs to the stagiaire
            selected_project = form.cleaned_data.get('project')
            if selected_project and selected_project.stagiaire != request.user:
                messages.error(request, 'Vous ne pouvez pas créer un rapport pour ce projet.')
                return redirect('report_list')
            
            # Verify the selected task belongs to the project
            selected_task = form.cleaned_data.get('task')
            if selected_task and selected_task.project != selected_project:
                messages.error(request, 'La tâche sélectionnée ne correspond pas au projet.')
                return redirect('report_list')
            
            report = form.save(commit=False)
            report.stagiaire = request.user
            report.status = 'draft'
            report.save()
            messages.success(request, 'Rapport sauvegardé comme brouillon!')
            return redirect('report_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternshipReportForm(instance=report)
        # Filter queryset to only show stagiaire's projects
        form.fields['project'].queryset = Project.objects.filter(stagiaire=request.user)
        # Initialize task queryset - will be empty initially
        form.fields['task'].queryset = Task.objects.none()
    
    context = {
        'form': form,
        'report': report,
        'projects': projects,
        'is_edit': report is not None,
        'user': request.user,
    }
    return render(request, 'reports/report_form.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def report_submit_view(request, report_id):
    """Submit internship report"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('report_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('report_list')
    
    report = get_object_or_404(InternshipReport, id=report_id, stagiaire=request.user)
    
    if report.status == 'draft':
        report.status = 'submitted'
        report.submitted_date = datetime.now()
        report.save()
        
        # Create a review task for the mentor
        if report.project.mentor:
            due_date = datetime.now().date() + timedelta(days=5)
            Task.objects.get_or_create(
                project=report.project,
                title='Examiner rapport de stage',
                defaults={
                    'description': f'Veuillez examiner et évaluer le rapport de stage de {request.user.first_name} {request.user.last_name}.',
                    'week_number': 0,
                    'due_date': due_date,
                    'status': 'not_started'
                }
            )
        
        messages.success(request, 'Rapport soumis avec succès!')
    else:
        messages.warning(request, 'Ce rapport a déjà été soumis.')
    
    return redirect('report_list')


@login_required(login_url='login')
@require_http_methods(["GET"])
def get_project_tasks_view(request):
    """Get tasks for a project (AJAX endpoint)"""
    project_id = request.GET.get('project_id')
    
    if not project_id:
        return JsonResponse({'tasks': []})
    
    try:
        project = Project.objects.get(pk=project_id, stagiaire=request.user)
        tasks = Task.objects.filter(project=project).values('id', 'title')
        return JsonResponse({'tasks': list(tasks)})
    except Project.DoesNotExist:
        return JsonResponse({'tasks': []})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def profile_edit_view(request):
    """Edit user profile"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user, role='stagiaire')
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            # Update User fields if provided
            user = request.user
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            
            if email:
                user.email = email
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            user.save()
            
            messages.success(request, 'Profil mis à jour avec succès!')
            return redirect('profile_edit')
    else:
        form = ProfileEditForm(instance=profile)
        form.fields['email'].initial = request.user.email
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
    
    context = {
        'form': form,
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'profile/profile_edit.html', context)


# ============= HR FEATURE VIEWS =============

def check_rh_access(user):
    """Helper function to check if user is HR"""
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.role == 'rh'
    except UserProfile.DoesNotExist:
        return False


@login_required(login_url='login')
def internship_list_view(request):
    """Display all internships (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    internships = Internship.objects.all().order_by('-created_at')
    
    context = {
        'internships': internships,
        'user': request.user,
    }
    return render(request, 'internships/internship_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def internship_create_view(request):
    """Create a new internship (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            internship = form.save()
            messages.success(request, f'Stage "{internship.title}" créé avec succès!')
            return redirect('internship_detail', pk=internship.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternshipForm()
    
    context = {
        'form': form,
        'user': request.user,
        'is_create': True,
    }
    return render(request, 'internships/internship_form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def internship_detail_view(request, pk):
    """View and edit internship details (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    internship = get_object_or_404(Internship, pk=pk)
    assignments = InternshipAssignment.objects.filter(internship=internship)
    
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            internship = form.save()
            messages.success(request, f'Stage "{internship.title}" mis à jour avec succès!')
            return redirect('internship_detail', pk=internship.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternshipForm(instance=internship)
    
    context = {
        'form': form,
        'internship': internship,
        'assignments': assignments,
        'user': request.user,
        'is_create': False,
    }
    return render(request, 'internships/internship_form.html', context)


@login_required(login_url='login')
def internship_delete_view(request, pk):
    """Delete an internship (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    internship = get_object_or_404(Internship, pk=pk)
    
    if request.method == 'POST':
        title = internship.title
        internship.delete()
        messages.success(request, f'Stage "{title}" supprimé avec succès!')
        return redirect('internship_list')
    
    context = {
        'internship': internship,
        'user': request.user,
    }
    return render(request, 'internships/internship_confirm_delete.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def assignment_create_view(request, internship_pk):
    """Assign a stagiaire to an internship (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    internship = get_object_or_404(Internship, pk=internship_pk)
    
    if request.method == 'POST':
        form = InternshipAssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.internship = internship
            
            # Check if stagiaire is already assigned to this internship
            if InternshipAssignment.objects.filter(
                internship=internship,
                stagiaire=assignment.stagiaire
            ).exists():
                messages.error(request, 'Ce stagiaire est déjà assigné à ce stage.')
                return render(request, 'internships/assignment_form.html', {
                    'form': form,
                    'internship': internship,
                    'user': request.user,
                    'is_create': True,
                })
            
            assignment.save()
            messages.success(request, 'Stagiaire assigné au stage avec succès!')
            return redirect('internship_detail', pk=internship.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternshipAssignmentForm()
    
    context = {
        'form': form,
        'internship': internship,
        'user': request.user,
        'is_create': True,
    }
    return render(request, 'internships/assignment_form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def assignment_edit_view(request, pk):
    """Edit an assignment (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(InternshipAssignment, pk=pk)
    
    if request.method == 'POST':
        form = InternshipAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, 'Assignation mise à jour avec succès!')
            return redirect('internship_detail', pk=assignment.internship.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternshipAssignmentForm(instance=assignment)
    
    context = {
        'form': form,
        'assignment': assignment,
        'internship': assignment.internship,
        'user': request.user,
        'is_create': False,
    }
    return render(request, 'internships/assignment_form.html', context)


@login_required(login_url='login')
def assignment_delete_view(request, pk):
    """Delete an assignment (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    assignment = get_object_or_404(InternshipAssignment, pk=pk)
    internship_pk = assignment.internship.pk
    
    if request.method == 'POST':
        stagiaire_name = assignment.stagiaire.username
        assignment.delete()
        messages.success(request, f'Assignation de "{stagiaire_name}" supprimée avec succès!')
        return redirect('internship_detail', pk=internship_pk)
    
    context = {
        'assignment': assignment,
        'user': request.user,
    }
    return render(request, 'internships/assignment_confirm_delete.html', context)


# ============= STAGIAIRE MANAGEMENT (HR VIEW) =============

@login_required(login_url='login')
def stagiaire_list_view(request):
    """Display list of all stagiaires (HR only) with search functionality"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    # Get all users with stagiaire role
    stagiaires = User.objects.filter(
        profile__role='stagiaire'
    ).select_related('profile').order_by('first_name', 'last_name')
    
    # Search functionality
    search_query = request.GET.get('q', '').strip()
    if search_query:
        stagiaires = stagiaires.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(username__icontains=search_query) |
            models.Q(email__icontains=search_query)
        )
    
    context = {
        'stagiaires': stagiaires,
        'search_query': search_query,
        'user': request.user,
    }
    return render(request, 'stagiaires/stagiaire_list.html', context)


@login_required(login_url='login')
def stagiaire_detail_view(request, user_id):
    """Display details of a specific stagiaire (HR only)"""
    if not check_rh_access(request.user):
        messages.error(request, 'Accès refusé. Seul le RH peut accéder à cette page.')
        return redirect('dashboard')
    
    stagiaire = get_object_or_404(User, id=user_id, profile__role='stagiaire')
    profile = stagiaire.profile
    
    # Get stagiaire's projects
    projects = Project.objects.filter(stagiaire=stagiaire)
    
    # Get stagiaire's documents
    documents = Document.objects.filter(stagiaire=stagiaire)
    
    # Get stagiaire's reports
    reports = InternshipReport.objects.filter(stagiaire=stagiaire)
    
    # Get stagiaire's internship assignments
    assignments = InternshipAssignment.objects.filter(stagiaire=stagiaire)
    
    context = {
        'stagiaire': stagiaire,
        'profile': profile,
        'projects': projects,
        'documents': documents,
        'reports': reports,
        'assignments': assignments,
        'user': request.user,
    }
    return render(request, 'stagiaires/stagiaire_detail.html', context)


# ============= MENTOR FEATURE VIEWS =============

def check_mentor_access(user):
    """Helper function to check if user is a mentor"""
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.role == 'encadarant'
    except UserProfile.DoesNotExist:
        return False


@login_required(login_url='login')
def mentor_project_list_view(request):
    """Display all projects mentored by this mentor"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    projects = Project.objects.filter(mentor=request.user).order_by('-created_at')
    
    context = {
        'projects': projects,
        'user': request.user,
    }
    return render(request, 'mentor/project_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def mentor_project_create_view(request):
    """Create a new project and assign it to a stagiaire (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.mentor = request.user
            project.status = 'active'
            project.save()
            messages.success(request, f'Projet "{project.title}" créé et assigné avec succès!')
            return redirect('mentor_project_detail', pk=project.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'user': request.user,
        'is_create': True,
    }
    return render(request, 'mentor/project_form.html', context)


@login_required(login_url='login')
def mentor_project_detail_view(request, pk):
    """View project details including weekly reports (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=pk, mentor=request.user)
    weekly_reports = WeeklyReport.objects.filter(project=project).order_by('-week_start_date')
    internship_reports = InternshipReport.objects.filter(project=project).order_by('-submitted_date')
    
    # Check if final report exists
    try:
        final_report = FinalReport.objects.get(project=project)
    except FinalReport.DoesNotExist:
        final_report = None
    
    # Get documents marked as final reports
    final_documents = Document.objects.filter(project=project, is_final_report=True).order_by('-uploaded_at')
    
    context = {
        'project': project,
        'weekly_reports': weekly_reports,
        'internship_reports': internship_reports,
        'final_report': final_report,
        'final_documents': final_documents,
        'user': request.user,
    }
    return render(request, 'mentor/project_detail.html', context)


@login_required(login_url='login')
def mentor_weekly_report_list_view(request, project_pk):
    """View all weekly reports for a project (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=project_pk, mentor=request.user)
    weekly_reports = WeeklyReport.objects.filter(project=project).order_by('-week_start_date')
    
    context = {
        'project': project,
        'weekly_reports': weekly_reports,
        'user': request.user,
    }
    return render(request, 'mentor/weekly_report_list.html', context)


@login_required(login_url='login')
def mentor_weekly_report_detail_view(request, pk):
    """View and evaluate a weekly report (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    weekly_report = get_object_or_404(WeeklyReport, pk=pk)
    
    # Check if mentor owns this project
    if weekly_report.project.mentor != request.user:
        messages.error(request, 'Accès refusé. Vous n\'êtes pas le mentor de ce projet.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = WeeklyReportEvaluationForm(request.POST, instance=weekly_report)
        if form.is_valid():
            weekly_report = form.save(commit=False)
            weekly_report.approved_by = request.user
            weekly_report.approved_date = datetime.now()
            weekly_report.save()
            
            status_text = 'approuvé' if weekly_report.status == 'approved' else 'rejeté'
            messages.success(request, f'Rapport de la semaine {weekly_report.week_number} {status_text}!')
            return redirect('mentor_project_detail', pk=weekly_report.project.pk)
    else:
        form = WeeklyReportEvaluationForm(instance=weekly_report)
    
    # Get tasks assigned for this week
    tasks = Task.objects.filter(project=weekly_report.project, week_number=weekly_report.week_number)
    
    # Get documents from the stagiaire
    documents = Document.objects.filter(stagiaire=weekly_report.stagiaire)
    
    context = {
        'weekly_report': weekly_report,
        'form': form,
        'tasks': tasks,
        'documents': documents,
        'user': request.user,
    }
    return render(request, 'mentor/weekly_report_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def mentor_final_report_detail_view(request, pk):
    """View and evaluate final report (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    final_report = get_object_or_404(FinalReport, pk=pk)
    
    # Check if mentor owns this project
    if final_report.project.mentor != request.user:
        messages.error(request, 'Accès refusé. Vous n\'êtes pas le mentor de ce projet.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = FinalReportEvaluationForm(request.POST, instance=final_report)
        if form.is_valid():
            final_report = form.save(commit=False)
            final_report.approved_by = request.user
            final_report.approved_date = datetime.now()
            final_report.save()
            
            status_text = 'approuvé' if final_report.status == 'approved' else 'rejeté'
            messages.success(request, f'Rapport final {status_text}!')
            return redirect('mentor_project_detail', pk=final_report.project.pk)
    else:
        form = FinalReportEvaluationForm(instance=final_report)
    
    context = {
        'final_report': final_report,
        'form': form,
        'user': request.user,
    }
    return render(request, 'mentor/final_report_detail.html', context)


@login_required(login_url='login')
def mentor_internship_report_detail_view(request, pk):
    """View internship report details with attached files (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    internship_report = get_object_or_404(InternshipReport, pk=pk)
    
    # Check if mentor has access to this report's project
    if internship_report.project.mentor != request.user:
        messages.error(request, 'Accès refusé à ce rapport.')
        return redirect('dashboard')
    
    context = {
        'internship_report': internship_report,
        'project': internship_report.project,
        'user': request.user,
    }
    return render(request, 'mentor/internship_report_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def mentor_validate_internship_report_view(request, pk):
    """Mentor validates internship report with comments"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    internship_report = get_object_or_404(InternshipReport, pk=pk)
    
    # Check if mentor has access to this report's project
    if internship_report.project.mentor != request.user:
        messages.error(request, 'Accès refusé à ce rapport.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = InternshipReportValidationForm(request.POST, instance=internship_report)
        if form.is_valid():
            report = form.save(commit=False)
            report.validated_by = request.user
            report.validated_date = datetime.now()
            report.status = 'reviewed'
            report.save()
            
            messages.success(request, f'Rapport validé avec le statut: {report.get_validation_status_display()}')
            return redirect('mentor_project_detail', pk=internship_report.project.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = InternshipReportValidationForm(instance=internship_report)
    
    context = {
        'form': form,
        'internship_report': internship_report,
        'project': internship_report.project,
        'user': request.user,
    }
    return render(request, 'mentor/internship_report_validation.html', context)



# ============= STAGIAIRE WEEKLY REPORT VIEWS =============

@login_required(login_url='login')
def stagiaire_weekly_report_list_view(request):
    """Display all weekly reports for stagiaire's project"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get stagiaire's project
    projects = Project.objects.filter(stagiaire=request.user)
    if not projects.exists():
        messages.error(request, 'Vous n\'avez pas de projet assigné.')
        return redirect('dashboard')
    
    project = projects.first()
    weekly_reports = WeeklyReport.objects.filter(stagiaire=request.user, project=project).order_by('-week_start_date')
    
    context = {
        'project': project,
        'weekly_reports': weekly_reports,
        'user': request.user,
    }
    return render(request, 'stagiaire/weekly_report_list.html', context)


@login_required(login_url='login')
def stagiaire_weekly_report_detail_view(request, report_id):
    """Display detail of a weekly report for stagiaire"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    weekly_report = get_object_or_404(WeeklyReport, pk=report_id, stagiaire=request.user)
    
    # Get tasks assigned for this week
    tasks = Task.objects.filter(project=weekly_report.project, week_number=weekly_report.week_number)
    
    # Get documents from the stagiaire
    documents = Document.objects.filter(stagiaire=request.user)
    
    context = {
        'weekly_report': weekly_report,
        'tasks': tasks,
        'documents': documents,
        'user': request.user,
    }
    return render(request, 'stagiaire/weekly_report_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def stagiaire_weekly_report_create_view(request):
    """Create or submit weekly report (Stagiaire only)"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get stagiaire's project
    projects = Project.objects.filter(stagiaire=request.user)
    if not projects.exists():
        messages.error(request, 'Vous n\'avez pas de projet assigné.')
        return redirect('dashboard')
    
    project = projects.first()
    
    # Calculate current week number
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    current_week = today.isocalendar()[1]
    
    # Check if already submitted for this week
    existing_report = WeeklyReport.objects.filter(
        stagiaire=request.user,
        project=project,
        week_number=current_week
    ).first()
    
    if request.method == 'POST':
        form = WeeklyReportForm(request.POST, request.FILES, instance=existing_report)
        if form.is_valid():
            weekly_report = form.save(commit=False)
            weekly_report.project = project
            weekly_report.stagiaire = request.user
            weekly_report.week_number = current_week
            weekly_report.week_start_date = week_start
            weekly_report.week_end_date = week_end
            weekly_report.status = 'submitted'
            weekly_report.submitted_date = datetime.now()
            weekly_report.save()
            
            # Create a review task for the mentor
            if project.mentor:
                due_date = datetime.now().date() + timedelta(days=3)
                Task.objects.get_or_create(
                    project=project,
                    title=f'Examiner rapport hebdomadaire - Semaine {current_week}',
                    defaults={
                        'description': f'Veuillez examiner et évaluer le rapport hebdomadaire de {request.user.first_name} {request.user.last_name} pour la semaine {current_week}.',
                        'week_number': current_week,
                        'due_date': due_date,
                        'status': 'not_started'
                    }
                )
            
            messages.success(request, f'Rapport de la semaine {current_week} soumis avec succès!')
            return redirect('stagiaire_weekly_report_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = WeeklyReportForm(instance=existing_report)
    
    context = {
        'form': form,
        'project': project,
        'week_number': current_week,
        'week_start': week_start,
        'week_end': week_end,
        'user': request.user,
        'is_create': existing_report is None,
    }
    return render(request, 'stagiaire/weekly_report_form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def stagiaire_final_report_create_view(request):
    """Create or submit final report (Stagiaire only)"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get stagiaire's project
    projects = Project.objects.filter(stagiaire=request.user)
    if not projects.exists():
        messages.error(request, 'Vous n\'avez pas de projet assigné.')
        return redirect('dashboard')
    
    project = projects.first()
    
    # Get or create final report
    final_report, created = FinalReport.objects.get_or_create(project=project)
    
    if request.method == 'POST':
        form = FinalReportForm(request.POST, request.FILES, instance=final_report)
        if form.is_valid():
            final_report = form.save(commit=False)
            final_report.stagiaire = request.user
            final_report.status = 'submitted'
            final_report.submitted_date = datetime.now()
            final_report.save()
            
            # Create a review task for the mentor
            if project.mentor:
                due_date = datetime.now().date() + timedelta(days=5)
                Task.objects.get_or_create(
                    project=project,
                    title='Examiner rapport final',
                    defaults={
                        'description': f'Veuillez examiner et évaluer le rapport final de {request.user.first_name} {request.user.last_name}.',
                        'week_number': 0,  # Final report is not tied to a specific week
                        'due_date': due_date,
                        'status': 'not_started'
                    }
                )
            
            messages.success(request, 'Rapport final soumis avec succès!')
            return redirect('stagiaire_final_report_detail')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = FinalReportForm(instance=final_report)
    
    context = {
        'form': form,
        'project': project,
        'final_report': final_report,
        'user': request.user,
    }
    return render(request, 'stagiaire/final_report_form.html', context)


@login_required(login_url='login')
def stagiaire_final_report_detail_view(request):
    """View final report status (Stagiaire only)"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'stagiaire':
            messages.error(request, 'Accès refusé.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil utilisateur non trouvé.')
        return redirect('dashboard')
    
    # Get stagiaire's project
    projects = Project.objects.filter(stagiaire=request.user)
    if not projects.exists():
        messages.error(request, 'Vous n\'avez pas de projet assigné.')
        return redirect('dashboard')
    
    project = projects.first()
    
    try:
        final_report = FinalReport.objects.get(project=project)
    except FinalReport.DoesNotExist:
        final_report = None
    
    context = {
        'project': project,
        'final_report': final_report,
        'user': request.user,
    }
    return render(request, 'stagiaire/final_report_detail.html', context)


# ============= MENTOR TASK MANAGEMENT VIEWS =============

@login_required(login_url='login')
def mentor_task_list_view(request, project_pk):
    """View all tasks for a project (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=project_pk, mentor=request.user)
    tasks = Task.objects.filter(project=project).order_by('week_number', 'due_date')
    
    context = {
        'project': project,
        'tasks': tasks,
        'user': request.user,
    }
    return render(request, 'mentor/task_list.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def mentor_task_create_view(request, project_pk):
    """Create a new task (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    project = get_object_or_404(Project, pk=project_pk, mentor=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, f'Tâche "{task.title}" créée avec succès!')
            return redirect('mentor_task_list', project_pk=project.pk)
    else:
        form = TaskForm()
    
    context = {
        'form': form,
        'project': project,
        'is_create': True,
        'user': request.user,
    }
    return render(request, 'mentor/task_form.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def mentor_task_edit_view(request, pk):
    """Edit a task (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    task = get_object_or_404(Task, pk=pk)
    
    # Check if mentor owns this project
    if task.project.mentor != request.user:
        messages.error(request, 'Accès refusé. Vous n\'êtes pas le mentor de ce projet.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Tâche "{task.title}" mise à jour avec succès!')
            return redirect('mentor_task_list', project_pk=task.project.pk)
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'project': task.project,
        'is_edit': True,
        'user': request.user,
    }
    return render(request, 'mentor/task_form.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mentor_task_delete_view(request, pk):
    """Delete a task (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    
    # Check if mentor owns this project
    if task.project.mentor != request.user:
        messages.error(request, 'Accès refusé. Vous n\'êtes pas le mentor de ce projet.')
        return redirect('dashboard')
    
    task_title = task.title
    task.delete()
    messages.success(request, f'Tâche "{task_title}" supprimée avec succès!')
    return redirect('mentor_task_list', project_pk=project_pk)


@login_required(login_url='login')
def mentor_all_tasks_view(request):
    """View all tasks for mentor's projects"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    # Get all projects for this mentor
    projects = Project.objects.filter(mentor=request.user)
    project_ids = projects.values_list('id', flat=True)
    
    # Get all tasks for these projects
    tasks = Task.objects.filter(project_id__in=project_ids).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    
    context = {
        'tasks': tasks,
        'projects': projects,
        'status_filter': status_filter,
        'user': request.user,
    }
    return render(request, 'mentor/all_tasks.html', context)


# ============= MENTOR INTERNSHIP REPORT VALIDATION VIEWS =============

@login_required(login_url='login')
def mentor_internship_report_validate_view(request, pk):
    """View to validate internship report (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    internship_report = get_object_or_404(InternshipReport, pk=pk)
    
    # Check if mentor has access to this report's project
    if internship_report.project.mentor != request.user:
        messages.error(request, 'Accès refusé à ce rapport.')
        return redirect('dashboard')
    
    # Check if report is submitted
    if internship_report.status != 'submitted':
        messages.error(request, 'Ce rapport doit être soumis pour être validé.')
        return redirect('mentor_internship_report_detail', pk=pk)
    
    context = {
        'internship_report': internship_report,
        'project': internship_report.project,
        'user': request.user,
    }
    return render(request, 'mentor/internship_report_validate.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mentor_internship_report_validate_submit_view(request, pk):
    """Submit validation for internship report (Mentor only)"""
    if not check_mentor_access(request.user):
        messages.error(request, 'Accès refusé. Seul un mentor peut accéder à cette page.')
        return redirect('dashboard')
    
    internship_report = get_object_or_404(InternshipReport, pk=pk)
    
    # Check if mentor has access to this report's project
    if internship_report.project.mentor != request.user:
        messages.error(request, 'Accès refusé à ce rapport.')
        return redirect('dashboard')
    
    validation_status = request.POST.get('validation_status')
    validation_comments = request.POST.get('validation_comments', '')
    
    # Validate inputs
    if validation_status not in ['approved', 'rejected']:
        messages.error(request, 'Statut de validation invalide.')
        return redirect('mentor_internship_report_validate', pk=pk)
    
    # Update report validation
    internship_report.validation_status = validation_status
    internship_report.validation_comments = validation_comments
    internship_report.validated_by = request.user
    internship_report.validated_date = datetime.now()
    internship_report.status = 'reviewed'
    internship_report.save()
    
    if validation_status == 'approved':
        messages.success(request, 'Rapport approuvé avec succès!')
    else:
        messages.warning(request, 'Rapport rejeté. Le stagiaire a été notifié.')
    
    return redirect('mentor_internship_report_detail', pk=pk)



