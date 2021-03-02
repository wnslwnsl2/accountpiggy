from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# Create your models here.

class MyUserManager(BaseUserManager):
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

"""
user.dummy 로 접근 할 수 있도록 하는 Manager
"""
class DummyManager(models.Manager):
    dummyemail = 'dummydummy@dummydummy.dummy'
    dummyname = '임시'

    def get_queryset(self):
        try:
            user = User.objects.create_user(
                email=self.dummyemail,
                name=self.dummyname,
            )
            user.save(using=self._db)
        except:
            user = User.objects.get(email=self.dummyemail)
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
    dummy = DummyManager()

    USERNAME_FIELD = 'email' #로그인 할 때 쓰는 건가?
    # 다른것들
        # EMAIL_FIELD
    REQUIRED_FIELDS = ['name']

    def is_dummy(self):
        return self.email == DummyManager.dummyemail

    def __str__(self):
        return '{}({})'.format(self.name,self.email)

    def has_perm(self,perm,obj=None):
        return True

    def has_module_perms(self,app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def rooms(self):
        member_set = self.member_set
        return [member.room for member in member_set.all()]


class Account(models.Model):
    bank = models.CharField(verbose_name="은행",max_length=20)
    number = models.CharField(verbose_name="계좌번호",max_length=30)
    user = models.OneToOneField(User,on_delete=models.CASCADE)