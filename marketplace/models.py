from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import os
import uuid
from uuid import uuid4

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email address.")
        if not username:
            raise ValueError("User must have a username.")
        user = self.model(
            email= self.normalize_email(email),
            username= username,
        )
        user.set_password(password)
        user.save(using= self._db)
        return user
    
    def create_superuser(self, email, username, password):
        user = self.create_user(
            email= self.normalize_email(email), 
            username= username,
            password= password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using= self._db)
        return user

class Account(AbstractBaseUser):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username        = models.CharField(max_length=30, unique=True)
    email           = models.EmailField(verbose_name="email", max_length=80, unique=True)
    date_joined     = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login      = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)
    hideEmail       = models.BooleanField(default=True)
    balance         = models.FloatField(validators=[MinValueValidator(0)], default=0)
    # password = models.CharField(max_length=30)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

    def check_password(self, raw_password: str) -> bool:
        return super().check_password(raw_password)

class Product(models.Model):
    categories = (
        ('Digital Devices', 'Digital Devices'),
        ('Clothes', 'Clothes'),
        ('Sport', 'Sport'),
        ('Food', 'Food'),
        ('Home Devices', 'Home Devices'),
        ('Other', 'Other')
    )
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=30)
    description = models.CharField(max_length=200, default="")
    price       = models.FloatField(validators=[MinValueValidator(0)])
    quantity    = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1000)])
    recommend   = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    category    = models.CharField(max_length=15, choices=categories, default=1)
    user        = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="productOwner")
    image       = models.ImageField(upload_to="%Y/%m/%d", blank= True, 
                    default='default.jpg')

    def __str__(self):
        return self.name

class Cart(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="cartOwner")
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True)
    quantity    = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True)

    def __str__(self):
        return f"{self.user}'s Cart"

    class Meta:
        unique_together = (('user', 'product'),)
        index_together = (('user', 'product'),)

class Market(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user    = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="marketOwner")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="productsMarket")

    def __str__(self):
        return f"{self.user}'s Market"
    
    class Meta:
        unique_together = (('user', 'product'),)
        index_together = (('user', 'product'),)

class Ownership(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller      = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="seller")
    buyer       = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="buyer")
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="productsBought")
    quantity    = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], blank=True)
    date_buy    = models.DateTimeField(verbose_name="date buy", auto_now_add=True)
    
    def __str__(self):
        return f"{self.seller} sell {self.quantity} * {self.product} to {self.buyer}"
