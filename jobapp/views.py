from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from .forms import AdminRegistrationForm
from .forms import AdminRegistrationForm, UserRegistrationForm, JobPostForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from jobapp.forms import (
    CreateItJobsForm, UpdateItJobsForm,
    CreateMechanicalJobForm, UpdateMechanicalJobsForm, CreateCivilJobsForm, UpdateCivilJobsForm
    
)

from .models import Profile
from django.urls import reverse
import json
from itertools import chain
from django.db.models import Count, Q, Avg
from django.utils.timezone import now
from datetime import timedelta
import calendar
from .models import ItJobs, MechJobs, CivilJobs, JobPost, JobApplication
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jobapp.ai.resume_parser import extract_text_from_resume
from jobapp.ai.resume_matcher import calculate_ai_score


# ========================================================================================
# -----------HOME VIEWS-------------------
# ========================================================================================

def home(request):
    """Public home page"""
    return render(request, 'jobapp/home.html')
# =====================================================================================================================

def home_search(request):
    query = request.GET.get("q", "").strip().lower()

    # Default
    category = "Other"
    template = "jobapp/other_jobs.html"

    if any(word in query for word in ["it", "developer", "software", "programmer", "tech"]):
        category = "IT"
        template = "jobapp/it_jobs.html"
        jobs = ItJobs.objects.all()
        if query:
            jobs = jobs.filter(
                Q(job_title__icontains=query) |
                Q(company_name__icontains=query) |
                Q(job_location__icontains=query) |
                Q(job_description__icontains=query)
            )

    elif any(word in query for word in ["mechanical", "mech", "machine", "production"]):
        category = "Mechanical"
        template = "jobapp/mech_jobs.html"
        jobs = MechJobs.objects.all()
        if query:
            jobs = jobs.filter(
                Q(job_title__icontains=query) |
                Q(company_name__icontains=query) |
                Q(job_location__icontains=query) |
                Q(job_description__icontains=query)
            )

    elif any(word in query for word in ["civil", "construction", "site"]):
        category = "Civil"
        template = "jobapp/civil_jobs.html"
        jobs = CivilJobs.objects.all()
        if query:
            jobs = jobs.filter(
                Q(job_title__icontains=query) |
                Q(company_name__icontains=query) |
                Q(job_location__icontains=query) |
                Q(job_description__icontains=query)
            )

    # For Other/HR/Account jobs
    else:
        category = "Other"
        template = "jobapp/other_jobs.html"
        jobs = JobPost.objects.filter(
            Q(job_category__iexact='Other') |
            Q(job_category__iexact='HR') |
            Q(job_category__iexact='Accountant')
        )
        if query:
            jobs = jobs.filter(
                Q(job_title__icontains=query) |
                Q(company_name__icontains=query) |
                Q(job_location__icontains=query) |
                Q(description__icontains=query)
            )


    # Show only 3 most recent jobs
    jobs = jobs.order_by('-posted_on')[:3]

    return render(request, template, {
        "jobs": jobs,
        "query": query,
        "category": category
    })
# =====================================================================================================================

def welcome(request):
    """User welcome page"""
    return render(request, 'jobapp/welcome.html')
# =====================================================================================================================

def about(request):
    return render(request, 'jobapp/about.html')
# =====================================================================================================================

def contact(request):
    return render(request, 'jobapp/contact.html')

# ========================================================================================
# Admin Authentication
# ========================================================================================

CustomUser = get_user_model()

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # ✅ make admin
            user.save()
            messages.success(request, "Admin account created! Please log in.")
            return redirect('admin_login')
    else:
        form = AdminRegistrationForm()
    return render(request, 'jobapp/admin_register.html', {'form': form})
# =====================================================================================================================

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # ✅ check for is_staff instead of is_admin
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin user.")
            return redirect('admin_login')

    return render(request, 'jobapp/admin_login.html')
# -----------------------------------------------------------------------------------------------------------

# Admin Dashboard
@login_required(login_url='admin_login')
def admin_dashboard(request):
    User = get_user_model()
    users = User.objects.all().count()

    # Count users
    total_users = users

    # Count recruiters
    total_recruiters = User.objects.filter(is_recruiter=True).count()
    
      # Latest data
    latest_users = User.objects.all().order_by('-date_joined')[:5]
    # Count pending applications
    # Count pending applications
    pending_applications = JobApplication.objects.filter(status='Pending').count()


     # Fetch jobs from all models
    jobpost_jobs = list(JobPost.objects.all())
    it_jobs = list(ItJobs.objects.all())
    mech_jobs = list(MechJobs.objects.all())
    civil_jobs = list(CivilJobs.objects.all())

    # MERGE all jobs into one list
    all_jobs = jobpost_jobs + it_jobs + mech_jobs + civil_jobs

    # SORT by posted_on
    latest_jobs = sorted(all_jobs, key=lambda x: x.posted_on, reverse=True)[:5]  
    # ↑ This ensures ONLY top 5 latest jobs across all models

    # Count jobs
    total_jobs = len(all_jobs)

    pending_recruiters = User.objects.filter(is_recruiter=True, is_active=False)

    # Count all type of jobs
    total_jobs = (
        JobPost.objects.count() +
        ItJobs.objects.count() +
        MechJobs.objects.count() +
        CivilJobs.objects.count()
    )

     # ---------------- CHART DATA ----------------
     # Total counts
    total_recruiters = CustomUser.objects.filter(is_recruiter=True).count()
    total_jobs = ItJobs.objects.count() + MechJobs.objects.count() + CivilJobs.objects.count() + JobPost.objects.count()

    # Latest entries
    latest_jobs = list(ItJobs.objects.all().order_by('-posted_on')[:3]) + \
                  list(MechJobs.objects.all().order_by('-posted_on')[:3]) + \
                  list(CivilJobs.objects.all().order_by('-posted_on')[:3]) + \
                  list(JobPost.objects.all().order_by('posted_on')[:3])
    latest_jobs = sorted(latest_jobs, key=lambda x: x.posted_on, reverse=True)[:5]

    pending_recruiters = CustomUser.objects.filter(is_recruiter=True, is_active=False)

    # Jobs per category for chart
    category_labels = ['IT', 'Mechanical', 'Civil', 'Other']
    category_counts = [
        ItJobs.objects.count(),
        MechJobs.objects.count(),
        CivilJobs.objects.count(),
        JobPost.objects.count()
    ]

    # Users trend example (last 6 months)
    
    month_labels = []
    month_counts = []

    today = now()
    for i in range(5, -1, -1):  # Last 6 months
        month = (today - timedelta(days=i*30)).month
        year = (today - timedelta(days=i*30)).year
        month_labels.append(calendar.month_name[month])
        count = CustomUser.objects.filter(
            date_joined__year=year,
            date_joined__month=month,
            is_user=True
        ).count()
        month_counts.append(count)

    # Users registered per month (last 6 months)
    last_six_months = timezone.now().date().replace(day=1)
    users_per_month = (
        User.objects.all()
        .extra(select={'month': "strftime('%%Y-%%m', date_joined)"})
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    month_labels = [x['month'] for x in users_per_month]
    month_counts = [x['count'] for x in users_per_month]

    # ---------------- ACTIVITY FEED ----------------
    recent_activity = JobApplication.objects.order_by('-applied_on')[:5]

    context = {
        "total_users": total_users,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "pending_applications": pending_applications,
        "total_applications": JobApplication.objects.count(),
        'latest_users': latest_users,
        'latest_jobs': latest_jobs,
        'pending_recruiters': pending_recruiters,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'month_labels': month_labels,
        'month_counts': month_counts,
        'recent_activity': recent_activity,
    }

    return render(request, "jobapp/admin_dashboard.html", context)

#------------------------------------------------------------------------------------------------------

@login_required(login_url='admin_login')
def admin_profile(request):
    return render(request, "jobapp/admin_profile.html")

#========================================================================================================
@login_required(login_url='admin_login')
def admin_edit_profile(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        user.bio = request.POST.get("bio")

        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get("profile_pic")

        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect("admin_profile")

    return render(request, "jobapp/admin_edit_profile.html")
#==========================================================================================================

# Admin Users Page
@login_required(login_url='admin_login')
def admin_users(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'jobapp/admin_users.html', {'users': users})
#============================================================================================================

@login_required(login_url='admin_login')
def admin_delete_user(request, user_id):
    if not request.user.is_admin:
        messages.error(request, "Access Denied!")
        return redirect("home")

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully!")
    return redirect("admin_users")
#================================================================================================================

@login_required(login_url='admin_login')
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES["profile_pic"]

        user.save()
        messages.success(request, "User updated successfully!")
        return redirect("admin_users")

    return render(request, "jobapp/admin_edit_user.html", {"user": user})
#===========================================================================================================

@login_required(login_url='admin_login')
def admin_recruiters(request):
    if not request.user.is_admin:
        return redirect("admin_login")

    recruiters = CustomUser.objects.filter(is_recruiter=True)
    return render(request, "jobapp/admin_recruiters.html", {"recruiters": recruiters})
#============================================================================================================

@login_required(login_url='admin_login')
def admin_view_recruiter(request, recruiter_id):
    recruiter = get_object_or_404(CustomUser, id=recruiter_id)

    # Fetch all jobs posted by this recruiter from ALL models
    general_jobs = JobPost.objects.filter(recruiter=recruiter)
    it_jobs = ItJobs.objects.filter(recruiter=recruiter)
    mech_jobs = MechJobs.objects.filter(recruiter=recruiter)
    civil_jobs = CivilJobs.objects.filter(recruiter=recruiter)

    # Combine ALL jobs into ONE list (optional)
    all_jobs = (
        list(general_jobs) +
        list(it_jobs) +
        list(mech_jobs) +
        list(civil_jobs)
    )

    context = {
        "recruiter": recruiter,
        "jobs": all_jobs,
    }
    return render(request, "jobapp/admin_view_recruiter.html", context)
#==================================================================================================================

@login_required(login_url='admin_login')
def admin_delete_recruiter(request, recruiter_id):
    recruiter = get_object_or_404(CustomUser, id=recruiter_id, is_recruiter=True)

    if request.method == "POST":
        # Delete recruiter → Jobs auto delete due to CASCADE
        recruiter.delete()
        messages.success(request, "Recruiter and all posted jobs deleted successfully.")
        return redirect("admin_recruiters")

    # GET request → show confirmation page
    return render(request, "jobapp/admin_confirm_delete_recruiter.html", {
        "recruiter": recruiter
    })
#================================================================================================================

@login_required(login_url='admin_login')
def admin_jobs(request):
    jobs = JobPost.objects.all()
    it_jobs = ItJobs.objects.all()
    mech_jobs = MechJobs.objects.all()
    civil_jobs = CivilJobs.objects.all()

    all_jobs_list = list(chain(jobs, it_jobs, mech_jobs, civil_jobs))

    return render(request, 'jobapp/admin_jobs.html', {'jobs': all_jobs_list})
#===============================================================================================================

@login_required(login_url='admin_login')
def admin_applicants(request):
    applications = JobApplication.objects.all().order_by('-applied_on')
    return render(request, "jobapp/admin_applicants.html", {"applications": applications})
#==============================================================================================================

@login_required(login_url='admin_login')
def admin_view_applicant(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    return render(request, "jobapp/admin_view_applicant.html", {"app": application})
#===============================================================================================================

@login_required(login_url='admin_login')
def admin_update_application(request, app_id, status):
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = status
    application.reviewed_on = timezone.now()
    application.save()
    return redirect("admin_view_applicant", app_id=app_id)
#=================================================================================================================

@login_required(login_url='admin_login')
def admin_delete_application(request, app_id):
    app = get_object_or_404(JobApplication, id=app_id)
    app.delete()
    return redirect("admin_applicants")
#=================================================================================================================

# Manage Jobs Page
@login_required(login_url='admin_login')
def manage_jobs(request):
    it_jobs = ItJobs.objects.all()
    mech_jobs = MechJobs.objects.all()
    civil_jobs = CivilJobs.objects.all()
    return render(request, 'jobapp/manage_jobs.html', {
        'it_jobs': it_jobs,
        'mech_jobs': mech_jobs,
        'civil_jobs': civil_jobs
    })
#================================================================================================================

@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('home') 
#================================================================================================================

@login_required(login_url='recruiter_login')
def applicants_list(request):

    q = request.GET.get('q')
    job_type = request.GET.get('job_type')

    applicants = JobApplication.objects.filter(
        company_name__in=JobApplication.objects.filter(
            company_name__isnull=False
        ).values_list('company_name', flat=True)
    ).order_by('-ai_score')

    applications = JobApplication.objects.all().order_by('-ai_score')
    if q:
        applicants = applicants.filter(
            Q(job_title__icontains=q) |
            Q(name__icontains=q)
        )

    if job_type:
        applicants = applicants.filter(category=job_type)

    # 🔥 AI SCORE CLASSIFICATION (ADD HERE)
    for app in applicants:
        if app.ai_score >= 75:
            app.ai_label = "High"
            app.ai_color = "success"
        elif app.ai_score >= 50:
            app.ai_label = "Moderate"
            app.ai_color = "warning"
        else:
            app.ai_label = "Low"
            app.ai_color = "danger"

    return render(request, 'jobapp/applicants_list.html', {
        'applicants': applicants,
        'applications': applications,
    })


@login_required(login_url='recruiter_login')
def approve_application(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = "Approved"
    application.save()
    return redirect('applicants_list')


@login_required(login_url='recruiter_login')
def reject_application(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = "Rejected"
    application.save()
    return redirect('applicants_list')


@login_required(login_url='recruiter_login')
def update_application_status(request, app_id, status):
    app = get_object_or_404(JobApplication, id=app_id)

    if status in ['Approved', 'Rejected']:
        app.status = status
        app.save()

    return redirect('recruiter_applicants')


# ========================================================================================
# User Authentication
# ========================================================================================


def user_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('user_registration')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('user_login')  # ✅ redirect to user login, not admin dashboard

    return render(request, 'jobapp/register.html')
#==========================================================================================================

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            elif getattr(user, 'is_recruiter', False):
                return redirect('recruiter_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password!")
    return render(request, 'jobapp/user_login.html')
#==================================================================================================================

@login_required(login_url='user_login')
def user_dashboard(request):
    # Jobs list as before
    it_jobs = ItJobs.objects.all().order_by('-posted_on')[:3]
    mech_jobs = MechJobs.objects.all().order_by('-posted_on')[:3]
    civil_jobs = CivilJobs.objects.all().order_by('-posted_on')[:3]
    other_jobs = JobPost.objects.exclude(job_category__in=['IT','Mechanical','Civil']).order_by('-posted_on')[:3]

    jobs = []
    for job in it_jobs:
        jobs.append({
            'instance': job,
            'category': 'IT',
            'badge_class': 'badge-it',
            'text_class': 'text-primary',
            'detail_url': reverse('job_detail_it', args=[job.id])
        })
    for job in mech_jobs:
        jobs.append({
            'instance': job,
            'category': 'Mechanical',
            'badge_class': 'badge-mech',
            'text_class': 'text-success',
            'detail_url': reverse('job_detail_mech', args=[job.id])
        })
    for job in civil_jobs:
        jobs.append({
            'instance': job,
            'category': 'Civil',
            'badge_class': 'badge-civil',
            'text_class': 'text-secondary',
            'detail_url': reverse('job_detail_civil', args=[job.id])
        })
    for job in other_jobs:
        jobs.append({
            'instance': job,
            'category': 'Other',
            'badge_class': 'badge-other',
            'text_class': 'text-dark',
            'detail_url': reverse('job_detail', args=[job.id])
        })

    # Application stats
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_on')
    total_applications = applications.count()
    approved_applications = applications.filter(status="Approved").count()
    rejected_applications = applications.filter(status="Rejected").count()
    pending_applications = applications.filter(status="Pending").count()

    return render(request, 'jobapp/user_dashboard.html', {
        'jobs': jobs,
        'applications': applications,
        'total_applications': total_applications,
        'approved_applications': approved_applications,
        'rejected_applications': rejected_applications,
        'pending_applications': pending_applications,
    })
#===============================================================================================================

@login_required(login_url='user_login')
def user_applied_jobs(request):
    # Fetch all applications for this user
    applications = JobApplication.objects.filter(user=request.user).order_by('-applied_on')
    return render(request, 'jobapp/user_applied_jobs.html', {'applications': applications})
#==================================================================================================================

@login_required(login_url='user_login')
def update_profile_photo(request):
    if request.method == "POST":
        profile, created = Profile.objects.get_or_create(user=request.user)

        photo = request.FILES.get("photo")
        if photo:
            profile.photo = photo
            profile.save()

        messages.success(request, "Profile photo updated!")
        return redirect("user_profile")

    return redirect("user_profile")
#===========================================================================================================

@login_required(login_url='user_login')
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    return render(request, 'jobapp/edit_profile.html', {'user': user})
#=============================================================================================================

@login_required(login_url='user_login')
def user_profile(request):
    """
    Display the logged-in user's profile information.
    """
    user = request.user
    return render(request, 'jobapp/user_profile.html', {'user': user})
#=============================================================================================================

@login_required(login_url='user_login')
def job_detail(request, job_id):
    """
    Display full details for a specific job.
    """
    job = get_object_or_404(JobPost, id=job_id)
    return render(request, 'jobapp/job_detail.html', {'job': job})
#=============================================================================================================

@login_required(login_url='user_login')
def list_of_all_jobs(request):
    other_jobs = JobPost.objects.exclude(
        job_category__in=['IT', 'Mechanical', 'Civil']
    ).order_by('-posted_on')
    return render(request, 'jobapp/list_of_all_jobs.html', {'other_jobs': other_jobs})
#==============================================================================================================

@login_required(login_url='user_login')
def user_logout(request):
    logout(request)
    request.session.flush()
    messages.success(request, "You have logged out successfully.")
    return redirect('home')

# ========================================================================================
# IT Jobs CRUD
# ========================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def create_it_jobs(request):
    form = CreateItJobsForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user   
        job.save()
        return redirect('recruiter_manage_jobs')
    return render(request, 'jobapp/create-it.html', {'form': form})
#==============================================================================================================

@never_cache
def list_of_it_jobs(request):
    context = {'data': ItJobs.objects.all()}
    return render(request, 'jobapp/list_of_it_jobs.html', context)
#============================================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def update_it_job(request, job_id):
    job = get_object_or_404(ItJobs, id=job_id)
    form = UpdateItJobsForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('list_of_it_jobs')
    return render(request, 'jobapp/update-it.html', {'form': form, 'job': job})
#============================================================================================================

@never_cache
@login_required(login_url='admin_login')
def delete_it_job(request, job_id):
    job = get_object_or_404(ItJobs, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('list_of_it_jobs')
    return render(request, 'jobapp/delete_it_job.html', {'job': job})
#============================================================================================================

# ========================================================================================
# Mechanical Jobs CRUD
# ========================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def create_mechanical_jobs(request):
    form = CreateMechanicalJobForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user   
        job.save()
        return redirect('recruiter_manage_jobs')
    return render(request, 'jobapp/create_mechanical_jobs.html', {'form': form})
#============================================================================================================

def list_of_mechanical_jobs(request):
    context = {'data': MechJobs.objects.all()}
    return render(request, 'jobapp/list_of_mech_jobs.html', context)
#============================================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def update_mechanical_job(request, job_id):
    job = get_object_or_404(MechJobs, id=job_id)
    form = UpdateMechanicalJobsForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('list_of_mech_jobs')
    return render(request, 'jobapp/update_mech.html', {'form': form, 'job': job})
#============================================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def delete_mechanical_job(request, job_id):
    job = get_object_or_404(MechJobs, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('list_of_mech_jobs')
    return render(request, 'jobapp/delete_mech_job.html', {'job': job})


# ========================================================================================
# Civil Jobs CRUD
# ========================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def create_civil_jobs(request):
    form = CreateCivilJobsForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False)
        job.recruiter = request.user   
        job.save()
        return redirect('recruiter_manage_jobs')
    return render(request, 'jobapp/create_civil_jobs.html', {'form': form})
#============================================================================================================

def list_of_civil_jobs(request):
    context = {'data': CivilJobs.objects.all()}
    return render(request, 'jobapp/list_of_civil_jobs.html', context)
#============================================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def update_civil_jobs(request, job_id):
    job = get_object_or_404(CivilJobs, id=job_id)
    form = UpdateCivilJobsForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('list_of_civil_jobs')
    return render(request, 'jobapp/update_civil_jobs.html', {'form': form, 'job': job})
#============================================================================================================

@never_cache
@login_required(login_url='recruiter_login')
def delete_civil_jobs(request, job_id):
    job = get_object_or_404(CivilJobs, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('list_of_civil_jobs')
    return render(request, 'jobapp/delete_civil_jobs.html', {'job': job})
#============================================================================================================
# ======================================================
# JOB DETAILS + APPLY (IT, MECH, CIVIL)
# ======================================================

# ===== IT =====
@login_required(login_url='user_login')
def it_job_detail(request, id):
    """View IT Job Details"""
    job = get_object_or_404(ItJobs, id=id)
    return render(request, 'jobapp/job_detail_it.html', {'job': job})
#============================================================================================================

# ===== MECHANICAL =====
@login_required(login_url='user_login')
def mech_job_detail(request, id):
    """View Mechanical Job Details"""
    job = get_object_or_404(MechJobs, id=id)
    return render(request, 'jobapp/job_detail_mech.html', {'job': job})
#============================================================================================================

# ===== CIVIL =====
@login_required(login_url='user_login')
def civil_job_detail(request, id):
    """View Civil Job Details"""
    job = get_object_or_404(CivilJobs, id=id)
    return render(request, 'jobapp/job_detail_civil.html', {'job': job})
#============================================================================================================

# ========== APPLY IT JOB ==========
@login_required(login_url='user_login')
def apply_it_job(request, id):
    print("🔥 APPLY JOB VIEW HIT 🔥")

    job = get_object_or_404(ItJobs, id=id)

    if request.method == "POST":
        resume_file = request.FILES.get('resume')

        # 1️⃣ Extract resume text
        resume_text = extract_text_from_resume(resume_file)

        # 2️⃣ Run AI matching (CORRECT CALL)
        ai_score, matched_skills, missing_skills, feedback = calculate_ai_score(
            resume_text=resume_text,
            job_description=job.job_description,
            required_skills=job.required_skills,
            job_category="IT"
        )

        matched_skills_str = ", ".join(matched_skills)
        missing_skills_str = ", ".join(missing_skills)
        ai_summary = feedback

        # 3️⃣ AI Label + Status Logic (SINGLE SOURCE)
        if ai_score >= 70:
            ai_label = "High Match"
            status = "Approved"
        elif ai_score >= 40:
            ai_label = "Medium Match"
            status = "Pending"
        else:
            ai_label = "Low Match"
            status = "Rejected"

        # 🔍 DEBUG
        print("========== AI DEBUG ==========")
        print("JOB REQUIRED SKILLS:", job.required_skills)
        print("MATCHED SKILLS:", matched_skills_str)
        print("MISSING SKILLS:", missing_skills_str)
        print("AI SCORE:", ai_score)
        print("STATUS:", status)
        print("================================")

        # 4️⃣ SAVE APPLICATION
        JobApplication.objects.create(
            user=request.user,
            job_id=job.id,

            job_title=job.job_title,
            company_name=job.company_name,
            category="IT",
            job_location=job.job_location,
            salary=job.salary,

            # Snapshots
            job_description_snapshot=job.job_description,
            required_skills_snapshot=job.required_skills,

            # Applicant info
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            contact=request.POST.get('contact'),
            qualification=request.POST.get('qualification'),
            resume=resume_file,

            # AI fields
            ai_score=ai_score,
            ai_label=ai_label,
            matched_skills=matched_skills_str,
            ai_feedback=feedback,
            ai_summary=feedback,
            status=status
        )

        return redirect('application_confirmation')

    return render(request, 'jobapp/apply_it_job.html', {'job': job})


#=================================================================================================================
@login_required
def application_detail_user(request, app_id):
    application = get_object_or_404(
        JobApplication,
        id=app_id,
        user=request.user
    )

    return render(
        request,
        'jobapp/application_detail_user.html',
        {'application': application}
    )
# =====================================================================================================================

# ========== APPLY MECHANICAL JOB ==========
@login_required(login_url='user_login')
def apply_mech_job(request, id):
    print("🔥 APPLY JOB VIEW HIT 🔥")

    job = get_object_or_404(MechJobs, id=id)

    if request.method == "POST":
        resume_file = request.FILES.get('resume')

        # 1️⃣ Extract resume text
        resume_text = extract_text_from_resume(resume_file)

        # 2️⃣ Run AI matching (CORRECT CALL)
        ai_score, matched_skills, missing_skills, feedback = calculate_ai_score(
            resume_text=resume_text,
            job_description=job.job_description,
            required_skills=job.required_skills,
            job_category="IT"
        )

        matched_skills_str = ", ".join(matched_skills)
        missing_skills_str = ", ".join(missing_skills)

        # 3️⃣ AI Label + Status Logic (SINGLE SOURCE)
        if ai_score >= 70:
            ai_label = "High Match"
            status = "Approved"
        elif ai_score >= 40:
            ai_label = "Medium Match"
            status = "Pending"
        else:
            ai_label = "Low Match"
            status = "Rejected"

        # 🔍 DEBUG
        print("========== AI DEBUG ==========")
        print("JOB REQUIRED SKILLS:", job.required_skills)
        print("MATCHED SKILLS:", matched_skills_str)
        print("MISSING SKILLS:", missing_skills_str)
        print("AI SCORE:", ai_score)
        print("STATUS:", status)
        print("================================")

        # 4️⃣ SAVE APPLICATION
        JobApplication.objects.create(
            user=request.user,
            job_id=job.id,

            job_title=job.job_title,
            company_name=job.company_name,
            category="Mechanical",
            job_location=job.job_location,
            salary=job.salary,

            # Snapshots
            job_description_snapshot=job.job_description,
            required_skills_snapshot=job.required_skills,

            # Applicant info
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            contact=request.POST.get('contact'),
            qualification=request.POST.get('qualification'),
            resume=resume_file,

            # AI fields
            ai_score=ai_score,
            ai_label=ai_label,
            matched_skills=matched_skills_str,
            ai_feedback=feedback,
            ai_summary=feedback,

            status=status
        )

        return redirect('application_confirmation')

    return render(request, 'jobapp/apply_mech_job.html', {'job': job})



# =====================================================================================================================

# ========== APPLY CIVIL JOB ==========
@login_required(login_url='user_login')
def apply_civil_job(request, id):
    print("🔥 APPLY JOB VIEW HIT 🔥")

    job = get_object_or_404(CivilJobs, id=id)

    if request.method == "POST":
        resume_file = request.FILES.get('resume')

        # 1️⃣ Extract resume text
        resume_text = extract_text_from_resume(resume_file)

        # 2️⃣ Run AI matching (CORRECT CALL)
        ai_score, matched_skills, missing_skills, feedback = calculate_ai_score(
            resume_text=resume_text,
            job_description=job.job_description,
            required_skills=job.required_skills,
            job_category="Civil"
        )

        matched_skills_str = ", ".join(matched_skills)
        missing_skills_str = ", ".join(missing_skills)

        # 3️⃣ AI Label + Status Logic (SINGLE SOURCE)
        if ai_score >= 70:
            ai_label = "High Match"
            status = "Approved"
        elif ai_score >= 40:
            ai_label = "Medium Match"
            status = "Pending"
        else:
            ai_label = "Low Match"
            status = "Rejected"

        # 🔍 DEBUG
        print("========== AI DEBUG ==========")
        print("JOB REQUIRED SKILLS:", job.required_skills)
        print("MATCHED SKILLS:", matched_skills_str)
        print("MISSING SKILLS:", missing_skills_str)
        print("AI SCORE:", ai_score)
        print("STATUS:", status)
        print("================================")

        # 4️⃣ SAVE APPLICATION
        JobApplication.objects.create(
            user=request.user,
            job_id=job.id,

            job_title=job.job_title,
            company_name=job.company_name,
            category="IT",
            job_location=job.job_location,
            salary=job.salary,

            # Snapshots
            job_description_snapshot=job.job_description,
            required_skills_snapshot=job.required_skills,

            # Applicant info
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            contact=request.POST.get('contact'),
            qualification=request.POST.get('qualification'),
            resume=resume_file,

            # AI fields
            ai_score=ai_score,
            ai_label=ai_label,
            matched_skills=matched_skills_str,
            ai_feedback=feedback,
            ai_summary=feedback,

            status=status
        )

        return redirect('application_confirmation')

    return render(request, 'jobapp/apply_civil_job.html', {'job': job})

# =====================================================================================================================

@login_required(login_url='user_login')
def application_confirmation(request):
    last_app = JobApplication.objects.filter(user=request.user).last()

    return render(request, 'jobapp/application_confirmation.html', {
        'job_title': last_app.job_title,
        'company_name': last_app.company_name,
        'category': last_app.category,
        'location': last_app.job_location,
        'salary': last_app.salary,
        'applied_on': last_app.applied_on,
        'status': last_app.status
    })
# =====================================================================================================================

@login_required(login_url='user_login')
def apply_success_it(request):
    last_app = JobApplication.objects.filter(user=request.user).last()
    return render(request, 'jobapp/application_confirmation.html', {
        'job_title': last_app.job_title,
        'company_name': last_app.company_name,
        'category': last_app.category,
        'applied_on': last_app.applied_on,
    })
# =====================================================================================================================

@login_required(login_url='user_login')
def apply_success_mech(request):
    last_app = JobApplication.objects.filter(user=request.user).last()
    return render(request, 'jobapp/application_confirmation.html', {
        'job_title': last_app.job_title,
        'company_name': last_app.company_name,
        'category': last_app.category,
        'applied_on': last_app.applied_on,
    })
# =====================================================================================================================

@login_required(login_url='user_login')
def apply_success_civil(request):
    last_app = JobApplication.objects.filter(user=request.user).last()
    return render(request, 'jobapp/application_confirmation.html', {
        'job_title': last_app.job_title,
        'company_name': last_app.company_name,
        'category': last_app.category,
        'applied_on': last_app.applied_on,
    })
# =====================================================================================================================

@login_required(login_url='recruiter_login')
def delete_application(request, id):
    app = get_object_or_404(JobApplication, id=id)
    
    if app.status != "Rejected":
        messages.error(request, "Only rejected applications can be deleted.")
        return redirect("applicants_list")
    
    app.delete()
    messages.success(request, "Application deleted successfully.")
    return redirect("applicants_list")

@login_required(login_url='recruiter_login')
def application_detail(request, id):
    app = get_object_or_404(JobApplication, id=id)

    # 🎨 Progress bar color
    if app.ai_score >= 75:
        app.ai_color = "bg-success"
    elif app.ai_score >= 50:
        app.ai_color = "bg-warning"
    else:
        app.ai_color = "bg-danger"

    # 🤖 Auto-generate AI summary if missing
    if app.ai_score is not None and not app.ai_summary:
        if app.ai_score >= 75:
            app.ai_label = "High Match"
            app.ai_summary = (
                "Candidate strongly matches the job requirements "
                "with relevant skills and experience."
            )
        elif app.ai_score >= 50:
            app.ai_label = "Moderate Match"
            app.ai_summary = (
                "Candidate partially matches the job requirements "
                "and should be reviewed further."
            )
        else:
            app.ai_label = "Low Match"
            app.ai_summary = (
                "Candidate profile does not sufficiently align "
                "with the job requirements."
            )
        app.save()

    return render(request, 'jobapp/application_detail.html', {'app': app})

# ------------------------------------------------------------------------------------------------------------------
#===================================================================================================================
#============RECRUITER CREDENTIAL=====================||
#===========                     =====================||

def recruiter_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('recruiter_register')

        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        user.is_recruiter = True
        user.save()

        messages.success(request, "Recruiter registered successfully! Please login.")
        return redirect('recruiter_login')

    return render(request, 'jobapp/recruiter_register.html')
# =====================================================================================================================

def recruiter_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_recruiter:
            login(request, user)
            return redirect('recruiter_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a recruiter account.")
            return redirect('recruiter_login')

    return render(request, 'jobapp/recruiter_login.html')
# =====================================================================================================================

@login_required(login_url='recruiter_login')
def recruiter_profile(request):
    user = request.user

    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")

        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES["profile_pic"]

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("recruiter_dashboard")  

    return render(request, "jobapp/recruiter_profile.html")
# =====================================================================================================================

# @login_required(login_url='user_login')
# def recruiter_dashboard(request):
#     return render(request, 'jobapp/recruiter_dashboard.html')

@login_required(login_url='recruiter_login')
def recruiter_logout(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('home')
# =====================================================================================================================

@login_required(login_url='recruiter_login') 
def recruiter_dashboard(request): 
    user = request.user 

    # Jobs created by this recruiter 
    it_jobs = ItJobs.objects.filter(recruiter=user) 
    mech_jobs = MechJobs.objects.filter(recruiter=user) 
    civil_jobs = CivilJobs.objects.filter(recruiter=user) 
    other_jobs = JobPost.objects.filter(recruiter=user) 
    jobs = list(chain(it_jobs, mech_jobs, civil_jobs, other_jobs)) 

    # Applications related to this recruiter 

    applications = JobApplication.objects.filter( company_name__in=[job.company_name for job in jobs] ) 
    applications = applications.order_by('-ai_score') 

    # ----- AI METRICS ----- 
    avg_ai_score = applications.aggregate( Avg('ai_score') )['ai_score__avg'] or 0 
    high_match_count = applications.filter( ai_score__gte=80 ).count() 
    total_applicants = applications.count() 
    approved_applicants = applications.filter(status="Approved").count() 
    rejected_applicants = applications.filter(status="Rejected").count() 
    pending_applicants = applications.filter(status="Pending").count()
     # ----- CATEGORY COUNTS ----- 
     
    categoryLabels = ["IT", "Mechanical", "Civil", "Other"] 
    categoryCounts = [ 
                        applications.filter(category="IT").count(), 
                        applications.filter(category="Mechanical").count(), 
                        applications.filter(category="Civil").count(), 
                        applications.exclude(category__in=["IT", "Mechanical", "Civil"]).count(), 
                    ] 
    status_counts = { "Approved": approved_applicants, 
                     "Rejected": rejected_applicants, 
                     "Pending": pending_applicants, } 
    return render(request, 'jobapp/recruiter_dashboard.html', 
                  { 
                    'jobs': jobs, 
                    'total_applicants': total_applicants, 
                    'approved_applicants': approved_applicants, 
                    'rejected_applicants': rejected_applicants, 
                    'pending_applicants': pending_applicants, 
                    'category_labels': json.dumps(categoryLabels), 
                    'category_counts': json.dumps(categoryCounts), 
                    'status_counts': status_counts, 
                    'avg_ai_score': round(avg_ai_score, 1), 
                    'high_match_count': high_match_count, })

# =====================================================================================================================

@login_required(login_url='recruiter_login')
def recruiter_all_jobs(request):
    jobs = JobPost.objects.filter(recruiter=request.user).order_by('-posted_on')
    return render(request, 'jobapp/recruiter_all_jobs.html', {'jobs': jobs})
# =====================================================================================================================
@login_required(login_url='recruiter_login')
def recruiter_manage_jobs(request):
    user = request.user

    it_jobs = ItJobs.objects.filter(recruiter=user)
    mech_jobs = MechJobs.objects.filter(recruiter=user)
    civil_jobs = CivilJobs.objects.filter(recruiter=user)
    other_jobs = JobPost.objects.filter(recruiter=user)

    jobs = list(chain(it_jobs, mech_jobs, civil_jobs, other_jobs))

    return render(request, 'jobapp/recruiter_manage_jobs.html', {
        'jobs': jobs
    })
#===================================================================================================================


def create_all_jobs(request):
    if request.method == "POST":
        job_title = request.POST.get("job_title")
        company_name = request.POST.get("company_name")
        job_category = request.POST.get("job_category")
        job_location = request.POST.get("job_location")
        salary = request.POST.get("salary")
        description = request.POST.get("description")

        job = JobPost.objects.create(
            job_title=job_title,
            company_name=company_name,
            job_category=job_category,
            job_location=job_location,
            salary=salary,
            description=description,
            recruiter=request.user
        )
        job.save()
        messages.success(request, "Job added successfully.")
        return redirect("recruiter_dashboard")

    return render(request, "jobapp/create_all_jobs.html")
#==============================================================================================================

def all_jobs(request):
    jobs = JobPost.objects.all()
    it_jobs = ItJobs.objects.all()
    mech_jobs = MechJobs.objects.all()
    civil_jobs = CivilJobs.objects.all()

    all_jobs_list = list(chain(jobs, it_jobs, mech_jobs, civil_jobs))

    return render(request, 'jobapp/all_jobs.html', {'jobs': all_jobs_list})
# =====================================================================================================================

@login_required(login_url='recruiter_login')
def edit_job(request, job_id):
    """
    Robust edit view: look for the job id in JobPost, ItJobs, MechJobs, CivilJobs.
    Only allow edit if the current user is the recruiter/owner when applicable.
    Quick shortcut implementation to avoid 404 when a job id belongs to another table.
    """

    job = JobPost.objects.filter(id=job_id).first()
    if job:
        if job.recruiter != request.user:
            messages.error(request, "You don't have permission to edit this job.")
            return redirect('recruiter_dashboard')

        if request.method == 'POST':
            form = JobPostForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, "Job updated successfully.")
                return redirect('recruiter_dashboard')
        else:
            form = JobPostForm(instance=job)

        return render(request, 'jobapp/edit_job.html', {'form': form, 'job': job})

    job_it = ItJobs.objects.filter(id=job_id).first()
    if job_it:
        if getattr(job_it, 'recruiter', None) and job_it.recruiter != request.user:
            messages.error(request, "You don't have permission to edit this IT job.")
            return redirect('recruiter_dashboard')

        if request.method == 'POST':
            job_it.company_name = request.POST.get('company_name', job_it.company_name)
            job_it.job_title = request.POST.get('job_title', job_it.job_title)
            job_it.job_location = request.POST.get('job_location', job_it.job_location)
            job_it.experience = request.POST.get('experience', job_it.experience)
            job_it.salary = request.POST.get('salary', job_it.salary)
            job_it.job_description = request.POST.get('job_description', job_it.job_description)
            job_it.save()
            messages.success(request, "IT Job updated successfully.")
            return redirect('recruiter_dashboard')

        context = {'job_it': job_it, 'type': 'it'}
        return render(request, 'jobapp/edit_it_job.html', context)

    job_mech = MechJobs.objects.filter(id=job_id).first()
    if job_mech:
        if getattr(job_mech, 'recruiter', None) and job_mech.recruiter != request.user:
            messages.error(request, "You don't have permission to edit this Mechanical job.")
            return redirect('recruiter_dashboard')

        if request.method == 'POST':
            job_mech.company_name = request.POST.get('company_name', job_mech.company_name)
            job_mech.job_title = request.POST.get('job_title', job_mech.job_title)
            job_mech.job_location = request.POST.get('job_location', job_mech.job_location)
            job_mech.experience = request.POST.get('experience', job_mech.experience)
            job_mech.salary = request.POST.get('salary', job_mech.salary)
            job_mech.job_description = request.POST.get('job_description', job_mech.job_description)
            job_mech.save()
            messages.success(request, "Mechanical Job updated successfully.")
            return redirect('recruiter_dashboard')

        context = {'job_mech': job_mech, 'type': 'mech'}
        return render(request, 'jobapp/edit_mech_job.html', context)

    job_civil = CivilJobs.objects.filter(id=job_id).first()
    if job_civil:
        if getattr(job_civil, 'recruiter', None) and job_civil.recruiter != request.user:
            messages.error(request, "You don't have permission to edit this Civil job.")
            return redirect('recruiter_dashboard')

        if request.method == 'POST':
            job_civil.company_name = request.POST.get('company_name', job_civil.company_name)
            job_civil.job_title = request.POST.get('job_title', job_civil.job_title)
            job_civil.job_location = request.POST.get('job_location', job_civil.job_location)
            job_civil.experience = request.POST.get('experience', job_civil.experience)
            job_civil.salary = request.POST.get('salary', job_civil.salary)
            job_civil.job_description = request.POST.get('job_description', job_civil.job_description)
            job_civil.save()
            messages.success(request, "Civil Job updated successfully.")
            return redirect('recruiter_dashboard')

        context = {'job_civil': job_civil, 'type': 'civil'}
        return render(request, 'jobapp/edit_civil_job.html', context)

    messages.error(request, "Job not found.")
    return redirect('recruiter_dashboard')
# =====================================================================================================================

@login_required(login_url='recruiter_login')
def delete_job(request, job_id):

    job = JobPost.objects.filter(id=job_id).first()
    if job:
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('recruiter_dashboard')

    job = ItJobs.objects.filter(id=job_id).first()
    if job:
        job.delete()
        messages.success(request, "IT Job deleted successfully!")
        return redirect('recruiter_dashboard')

    job = MechJobs.objects.filter(id=job_id).first()
    if job:
        job.delete()
        messages.success(request, "Mechanical Job deleted successfully!")
        return redirect('recruiter_dashboard')
    
    job = CivilJobs.objects.filter(id=job_id).first()
    if job:
        job.delete()
        messages.success(request, "Civil Job deleted successfully!")
        return redirect('recruiter_dashboard')

    messages.error(request, "Job not found!")
    return redirect('recruiter_dashboard')
# =====================================================================================================================

def admin_add(request):
    return render(request, 'jobapp/admin_add.html')
# =====================================================================================================================

# def admin_register(request):
#     return render(request, 'jobapp/admin_register.html')
# =====================================================================================================================
@login_required(login_url='user_login')
def apply_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    if not request.user.is_authenticated:
        messages.warning(request, "Please login to apply for this job.")
        return redirect('login')

    messages.success(request, f"You have successfully applied for {job.job_title}!")
    return redirect('all_jobs')
# =====================================================================================================================
# =====================================================================================================================
@login_required(login_url='login')
def apply_other_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        qualification = request.POST.get('qualification')
        resume = request.FILES.get('resume')

        if not resume:
            messages.error(request, "Please upload your resume.")
            return redirect(request.path)

 # ================= AI PROCESS =================
        resume_text = extract_text_from_resume(resume)

        job_text = f"""
        {job.job_title}
        {job.description or ""}
        {job.required_skills or ""}
        {job.job_location}
        """

        ai_score, matched_skills = calculate_ai_score(
            resume_text,
            job.description or "",
            job.required_skills or "",
            job.job_category
        )

        # Correct label logic
        if ai_score >= 70:
            ai_label = "High Match"
            ai_summary = "Strong profile. Skills closely match the job requirements."
            status = "Approved"
        elif ai_score >= 40:
            ai_label = "Medium Match"
            ai_summary = "Candidate partially matches the job requirements."
            status = "Pending"
        else:
            ai_label = "Low Match"
            ai_summary = "Resume does not sufficiently match the job requirements."
            status = "Rejected"

        # ================= SAVE APPLICATION =================
        JobApplication.objects.create(
            user=request.user,

            # 🔥 REQUIRED (FIX)
            job_id=job.id,

            job_title=job.job_title,
            company_name=job.company_name,
            category=job.job_category,
            job_location=job.job_location,
            salary=job.salary,

            # 🔥 SNAPSHOTS
            job_description_snapshot=job.description,
            required_skills_snapshot=job.required_skills,

            name=full_name,
            email=email,
            contact=phone,
            qualification=qualification,
            resume=resume,

            ai_score=ai_score,
            ai_label=ai_label,
            ai_summary=ai_summary,
            matched_skills=", ".join(matched_skills),
            status=status
        )

        messages.success(request, "Application submitted successfully!")
        return redirect('application_confirmation')

    return render(request, 'jobapp/apply_other_job.html', {'job': job})


# =====================================================================================================================
#===============AI IMPLEMENTATION=========================

