from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        """
        Creates and saves a User with the username, email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    USER_CHOICES = (('O', 'Organization'), ('T', 'Staff'), ('S', 'Student'))
    organization = models.ForeignKey('User', on_delete=models.CASCADE, 
                    limit_choices_to={'user_type': 'O'}, null=True, blank=True, related_name='students_and_staffs')
    username = models.CharField(max_length=20, unique=True, primary_key=True)
    email = models.EmailField(
        verbose_name='Email Address', max_length=255, unique=True)
    user_type = models.CharField(max_length=1, choices=USER_CHOICES, null=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @property
    def profile(self):
        if self.user_type == 'O':
            return self.organization_profile
        if self.user_type == 'T':
            return self.staff_profile
        return self.student_profile

    @property
    def staffs(self):
        return self.students_and_staffs.filter(user_type='T')

    @property
    def students(self):
        return self.students_and_staffs.filter(user_type='S')

