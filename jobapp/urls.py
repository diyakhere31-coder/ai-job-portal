# jobapp/urls.py
from django.urls import path
from jobapp import views

urlpatterns = [
    # ---------------- HOME ----------------
    path('', views.home, name='home'),

    # ---------------- USER AUTH ----------------
    path('register/', views.user_registration, name='user_registration'),
    path('user-login/', views.user_login, name='user_login'),
    path('user-logout/', views.user_logout, name='user_logout'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('user/profile/edit/', views.edit_profile, name='edit_profile'),  # ✅ new line
    path('list_of_all_jobs/', views.list_of_all_jobs, name='list_of_all_jobs'),


    # ---------------- ADMIN AUTH ----------------
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_users/', views.admin_users, name='admin_users'),
    path('admin_recruiters/', views.admin_recruiters, name='admin_recruiters'),
    # path('admin_add/', views.admin_add, name='admin_add'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('admin_jobs/', views.admin_jobs, name='admin_jobs'),
    # path('admin/applicants/', views.applicants_list, name='applicants_list'),
    path('admin_register/', views.admin_register, name='admin_register'),
    path("admin_profile/", views.admin_profile, name="admin_profile"),
    path("admin_edit_profile/", views.admin_edit_profile, name="admin_edit_profile"),
    path("admin_delete_user/<int:user_id>/", views.admin_delete_user, name="admin_delete_user"),
    path("admin_edit_user/<int:user_id>/", views.admin_edit_user, name="admin_edit_user"),
    path("admin_view_recruiter/<int:recruiter_id>/", views.admin_view_recruiter, name="admin_view_recruiter"),
    path("admin_delete_recruiter/<int:recruiter_id>/", views.admin_delete_recruiter, name="admin_delete_recruiter"),
    path("admin_applicants/", views.admin_applicants, name="admin_applicants"),
    path("admin_applicant/<int:app_id>/", views.admin_view_applicant, name="admin_view_applicant"),
    path("admin_applicant/update/<int:app_id>/<str:status>/", views.admin_update_application, name="admin_update_application"),
    path("admin_applicant/delete/<int:app_id>/", views.admin_delete_application, name="admin_delete_application"),

 # ---------------- IT JOBS ----------------
    path('create-it-jobs/', views.create_it_jobs, name='create_it_jobs'),
    path('list_of_it_jobs/', views.list_of_it_jobs, name='list_of_it_jobs'),
    path('update-it/<int:job_id>/', views.update_it_job, name='update_it_job'),
    path('delete-it/<int:job_id>/', views.delete_it_job, name='delete_it_job'),
    path('it-job/<int:id>/', views.it_job_detail, name='it_job_detail'),
    path('apply_it_job/<int:id>/', views.apply_it_job, name='apply_it_job'),
    path(
        'application_detail_user/<int:app_id>/',
        views.application_detail_user,
        name='application_detail_user'
    ),


    # ---------------- MECHANICAL JOBS ----------------
    path('create-mechanical-jobs/', views.create_mechanical_jobs, name='create_mechanical_jobs'),
    path('list_of_mech_jobs/', views.list_of_mechanical_jobs, name='list_of_mech_jobs'),
    path('update-mech/<int:job_id>/', views.update_mechanical_job, name='update_mech_job'),
    path('delete-mech/<int:job_id>/', views.delete_mechanical_job, name='delete_mech_job'),
    path('mech-job/<int:id>/', views.mech_job_detail, name='mech_job_detail'),
    path('apply_mech_job/<int:id>/', views.apply_mech_job, name='apply_mech_job'),

    # ---------------- CIVIL JOBS ----------------
    path('create-civil-jobs/', views.create_civil_jobs, name='create_civil_jobs'),
    path('list_of_civil_jobs/', views.list_of_civil_jobs, name='list_of_civil_jobs'),
    path('update-civil/<int:job_id>/', views.update_civil_jobs, name='update_civil_jobs'),
    path('delete-civil/<int:job_id>/', views.delete_civil_jobs, name='delete_civil_jobs'),
    path('civil-job/<int:id>/', views.civil_job_detail, name='civil_job_detail'),
    path('apply_civil_job/<int:id>/', views.apply_civil_job, name='apply_civil_job'),
    path('apply_other_job/<int:job_id>/', views.apply_other_job, name='apply_other_job'),

    # ---------------- RECRUITER ----------------
    path('recruiter_register/', views.recruiter_register, name='recruiter_register'),
    path('recruiter_login/', views.recruiter_login, name='recruiter_login'),
    path('recruiter_logout/', views.recruiter_logout, name='recruiter_logout'),
    path('recruiter_dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),

    path('jobs/', views.all_jobs, name='all_jobs'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),

    # ---------------- STATIC ----------------
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    # path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('create_all_jobs/', views.create_all_jobs, name='create_all_jobs'),
    path('recruiter_manage_jobs/', views.recruiter_manage_jobs, name='recruiter_manage_jobs'),
    path('job_detail_it/<int:id>/', views.it_job_detail, name='job_detail_it'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('job_detail_mech/<int:id>/', views.mech_job_detail, name='job_detail_mech'),
    path('job_detail_civil/<int:id>/', views.civil_job_detail, name='job_detail_civil'),
    
    path('edit_job/<str:job_type>/<int:job_id>/', views.edit_job, name='edit_job'),
    path('edit_it_job/<int:job_id>/', views.edit_job, name='edit_it_job'),
    path('edit_mech_job/<int:job_id>/', views.edit_job, name='edit_mech_job'),
    path('edit_civil_job/<int:job_id>/', views.edit_job, name='edit_civil_job'),
    path('apply_success_it/', views.apply_success_it, name='apply_success_it'),
    path('apply_success_mech/', views.apply_success_mech, name='apply_success_mech'),
    path('apply_success_civil/', views.apply_success_civil, name='apply_success_civil'),
    path('applicants_list/', views.applicants_list, name='applicants_list'),
    path('applicant_list/<int:app_id>/<str:status>/',
         views.update_application_status,
         name='update_application_status'),
    path('approve/<int:app_id>/', views.approve_application, name='approve_application'),
    path('reject/<int:app_id>/', views.reject_application, name='reject_application'),
    path('application_confirmation/', views.application_confirmation, name='application_confirmation'),
    path('delete_application/<int:id>/', views.delete_application, name='delete_application'),
    path('application_detail/<int:id>/', views.application_detail, name='application_detail'),
    path('recruiter_profile/', views.recruiter_profile, name='recruiter_profile'),
    path('user_applied_jobs/', views.user_applied_jobs, name='user_applied_jobs'),
    path("update-profile-photo/", views.update_profile_photo, name="update_profile_photo"),
    path("search/", views.home_search, name="home_search"),

]
