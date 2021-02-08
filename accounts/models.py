from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class MyUserManager(BaseUserManager):
    dummyemail = 'dummydummy@dummydummy.dummy'
    dummyname = 'dummy'
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_or_create_dummyuser(self):
        try:
            user = self.create_user(
                email = self.dummyemail,
                name = self.dummyname,
            )
            user.save(using=self._db)
            return user
        except:
            user = User.objects.get(email=self.dummyemail,name=self.dummyname)
            return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(
        verbose_name='이름',
        max_length=30,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email' #로그인 할 때 쓰는 건가?
    # 다른것들
        # EMAIL_FIELD
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return '{}({})'.format(self.name,self.email)

    def has_perm(self,perm,obj=None):
        return True

    def has_module_perms(self,app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin