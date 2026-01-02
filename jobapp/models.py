from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# -------------------------------------------------------------------
# Custom User Model (Only ONE)
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Override groups and permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',
        blank=True
    )

    def __str__(self):
        return self.username
    
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', default=None, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ItJobs(models.Model):
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_location = models.CharField(max_length=100)
    experience = models.FloatField()
    salary = models.CharField(max_length=50, null=True, blank=True)
    job_description = models.TextField(blank=True, null=True)
    required_skills = models.TextField(
        help_text="Comma separated skills (python, django, sql)",
        blank=True,
        null=True
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    @property
    def category_name(self):
        return "IT"

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class MechJobs(models.Model):
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_location = models.CharField(max_length=100)
    experience = models.FloatField()
    salary = models.CharField(max_length=50, null=True, blank=True)
    job_description = models.TextField(blank=True, null=True)
    required_skills = models.TextField(
        help_text="Comma separated skills (design, develop, build, mechanical engineer, CAD)",
        blank=True,
        null=True
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    @property
    def category_name(self):
        return "Mechanical"

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class CivilJobs(models.Model):
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_location = models.CharField(max_length=100)
    experience = models.FloatField()
    salary = models.CharField(max_length=50, null=True, blank=True)
    job_description = models.TextField(blank=True, null=True)
    required_skills = models.TextField(
        help_text="Comma separated skills (structural analysis, critical thinking, project management, Construction Knowledge)",
        blank=True,
        null=True
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    @property
    def category_name(self):
        return "Civil"

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"



# -------------------------------------------------------------------
class JobApplication(models.Model):
    CATEGORY_CHOICES = [
        ('IT', 'IT'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # ================= JOB INFO =================
    job_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the job from IT / Mechanical / Civil table"
    )

    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    job_location = models.CharField(max_length=200, null=True, blank=True)
    salary = models.CharField(max_length=50, null=True, blank=True)

    # SNAPSHOT (VERY IMPORTANT FOR AI)
    job_description_snapshot = models.TextField(
        null=True,
        blank=True,
        help_text="Job description at the time of application"
    )

    required_skills_snapshot = models.TextField(
        null=True,
        blank=True,
        help_text="Required skills at the time of application"
    )

    # ================= APPLICANT INFO =================
    name = models.CharField(max_length=150)
    email = models.EmailField()
    contact = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')

    applied_on = models.DateTimeField(auto_now_add=True)

    # ================= REVIEW & AI =================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    review_comment = models.TextField(blank=True, null=True)
    reviewed_on = models.DateTimeField(blank=True, null=True)

    ai_score = models.FloatField(default=0)
    ai_label = models.CharField(max_length=30, blank=True, null=True)
    ai_feedback = models.TextField(blank=True, null=True)
    matched_skills = models.TextField(
        blank=True,
        null=True,
        help_text="Skills matched from resume"
    )

    ai_summary = models.TextField(
        blank=True,
        null=True,
        help_text="AI generated resume summary"
    )

    def __str__(self):
        return f"{self.name} - {self.job_title} ({self.category})"


# -------------------------------------------------------------------
# General Job Model for Recruiters
# class Job(models.Model):
#     recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     company_name = models.CharField(max_length=200)
#     branch = models.CharField(max_length=100)
#     location = models.CharField(max_length=150)
#     salary = models.CharField(max_length=100)
#     description = models.TextField()
#     posted_on = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} at {self.company_name}"
    

class JobPost(models.Model):
    CATEGORY_CHOICES = [
        ('IT', 'IT'),
        ('Mechanical', 'Mechanical'),
        ('Civil', 'Civil'),
        ('Other', 'Other'),
    ]

    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    job_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)  # ADD CHOICES
    job_location = models.CharField(max_length=100)
    salary = models.CharField(max_length=50)
    description = models.TextField()
    required_skills = models.TextField(
        help_text="Comma separated skills (python, django, sql)",
        blank=True,
        null=True
    )
    posted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} - {self.company_name}"
