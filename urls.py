from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('', views.dashboard_view, name='home'),
    
    # Stagiaire Feature URLs
    path('projects/', views.project_detail_view, name='project_detail'),
    path('tasks/', views.task_list_view, name='task_list'),
    path('tasks/<int:task_id>/update-status/', views.stagiaire_task_update_view, name='task_update_status'),
    path('documents/', views.document_list_view, name='document_list'),
    path('documents/upload/', views.document_upload_view, name='document_upload'),
    path('reports/', views.report_list_view, name='report_list'),
    path('reports/create/', views.report_create_view, name='report_create'),
    path('reports/<int:report_id>/submit/', views.report_submit_view, name='report_submit'),
    path('api/project-tasks/', views.get_project_tasks_view, name='get_project_tasks'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # HR Feature URLs - Internship Management
    path('internships/', views.internship_list_view, name='internship_list'),
    path('internships/create/', views.internship_create_view, name='internship_create'),
    path('internships/<int:pk>/', views.internship_detail_view, name='internship_detail'),
    path('internships/<int:pk>/delete/', views.internship_delete_view, name='internship_delete'),
    
    # HR Feature URLs - Assignment Management
    path('internships/<int:internship_pk>/assign/', views.assignment_create_view, name='assignment_create'),
    path('assignments/<int:pk>/edit/', views.assignment_edit_view, name='assignment_edit'),
    path('assignments/<int:pk>/delete/', views.assignment_delete_view, name='assignment_delete'),
    
    # HR Feature URLs - Stagiaire Management
    path('stagiaires/', views.stagiaire_list_view, name='stagiaire_list'),
    path('stagiaires/<int:user_id>/', views.stagiaire_detail_view, name='stagiaire_detail'),
    
    # Mentor Feature URLs - Project Management
    path('mentor/projects/', views.mentor_project_list_view, name='mentor_project_list'),
    path('mentor/projects/create/', views.mentor_project_create_view, name='mentor_project_create'),
    path('mentor/projects/<int:pk>/', views.mentor_project_detail_view, name='mentor_project_detail'),
    
    # Mentor Feature URLs - Task Management
    path('mentor/projects/<int:project_pk>/tasks/', views.mentor_task_list_view, name='mentor_task_list'),
    path('mentor/projects/<int:project_pk>/tasks/create/', views.mentor_task_create_view, name='mentor_task_create'),
    path('mentor/tasks/<int:pk>/edit/', views.mentor_task_edit_view, name='mentor_task_edit'),
    path('mentor/tasks/<int:pk>/delete/', views.mentor_task_delete_view, name='mentor_task_delete'),
    path('mentor/tasks/', views.mentor_all_tasks_view, name='mentor_all_tasks'),
    
    # Mentor Feature URLs - Weekly Report Evaluation
    path('mentor/projects/<int:project_pk>/weekly-reports/', views.mentor_weekly_report_list_view, name='mentor_weekly_report_list'),
    path('mentor/weekly-reports/<int:pk>/', views.mentor_weekly_report_detail_view, name='mentor_weekly_report_detail'),
    
    # Mentor Feature URLs - Final Report Evaluation
    path('mentor/final-reports/<int:pk>/', views.mentor_final_report_detail_view, name='mentor_final_report_detail'),
    
    # Mentor Feature URLs - Internship Report View
    path('mentor/internship-reports/<int:pk>/', views.mentor_internship_report_detail_view, name='mentor_internship_report_detail'),
    path('mentor/internship-reports/<int:pk>/validate/', views.mentor_validate_internship_report_view, name='mentor_internship_report_validate'),
    
    # Stagiaire Feature URLs - Weekly Reports
    path('stagiaire/weekly-reports/', views.stagiaire_weekly_report_list_view, name='stagiaire_weekly_report_list'),
    path('stagiaire/weekly-reports/<int:report_id>/', views.stagiaire_weekly_report_detail_view, name='stagiaire_weekly_report_detail'),
    path('stagiaire/weekly-reports/create/', views.stagiaire_weekly_report_create_view, name='stagiaire_weekly_report_create'),
    
    # Stagiaire Feature URLs - Final Report
    path('stagiaire/final-report/create/', views.stagiaire_final_report_create_view, name='stagiaire_final_report_create'),
    path('stagiaire/final-report/', views.stagiaire_final_report_detail_view, name='stagiaire_final_report_detail'),
]
