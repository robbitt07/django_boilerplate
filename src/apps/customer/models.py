from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from rest_framework.authtoken.models import Token

from services.customer import CustomerIntegration


CUSTOMER_INTEGRATION_OPTIONS = (
	("STRIPE", "Stripe"),
)

from uuid import uuid4


# Customer
class Customer(models.Model):
	# ID Override to align with rest of structure
	id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	name = models.CharField(max_length=100, unique=True)
	name_hash = models.CharField(max_length=32, unique=True)
	customer_primary_email = models.EmailField(max_length=100, unique=True)
	trail_account = models.BooleanField(default=True)
	
	# Customer Integration Type
	integration = models.CharField(
		max_length=20, blank=True, null=True, choices=CUSTOMER_INTEGRATION_OPTIONS
	)
	# Customer Integration Key or Reference Number
	integration_key = models.CharField(max_length=500, blank=True, null=True)
	integration_payment_active = models.BooleanField(default=False) # Customer has active integration payment method

	demo_account = models.BooleanField(default=False) # Internal Demo Account
	
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "cust_customer"
		verbose_name = "Customer"
		verbose_name_plural = "Customers"
		ordering = ("pk",)

	def get_or_create_integration_key(self) -> str:
		if self.integration_key is not None:
			return self.integration_key
		if self.integration is None:
			self.integration = settings.CURRENT_CUSTOMER_INTEGRATION
			self.save()

		# TODO: Customer Integration that routes to the correct customer creation 
		# integration = CustomerIntegration(customer_obj=self)
		# return integration.create_customer()
		return "key"
		
	@property
	def _active_subscription(self):
		return self.subscriptions.filter(
			Q(Q(deactive_date=None) | Q(deactive_date__date__gt=timezone.now().date())),
			active_date__date__lte=timezone.now().date(),
		).first()

	@property
	def active_subscription(self):
		if self._active_subscription is None:
			# Default Demo Account
			return {
				"subscription": {
					"name": "Demo",
					"description": "Demo accounts have limited feature access. To access all features, upgrade to a paid account."
				}
			}
		return self._active_subscription
	
	@property
	def has_active_subscription(self):
		return self._active_subscription is not None

	def __str__(self):
		return str(self.name)


@receiver(post_save, sender=Customer)
def customer_post_save_handler(sender, instance, **kwargs):
	cache.delete(f"customer_config:{instance.pk}")


@receiver(post_delete, sender=Customer)
def customer_post_delete_handler(sender, instance, **kwargs):
	cache.delete(f"customer_config:{instance.pk}")


# User Manager
class UserManager(BaseUserManager):
	def get_queryset(self, customer=None):
		if customer is not None:
			return super().get_queryset().filter(customer=customer)
		else:
			return super().get_queryset()


	def create_user(self, email, customer_id, password=None, *args, **kwargs):
		"""
		Creates and saves a User with the given email and password.
		"""
		if not email:
			raise ValueError("Users must have an email address")

		user = self.model(
			email=self.normalize_email(email),
			customer_id=customer_id,
			first_name=kwargs.get("first_name", None),
			last_name=kwargs.get("last_name", None)
		)

		user.set_password(password)
		user.save(using=self._db)

		## Check if User is Assigned to Demo Customer, if so avoid email confirmation
		if user.customer is not None:
			if user.customer.demo_account:
				user.email_confirmed = True
				user.save()

		return user

	def create_staffuser(self, email: str, password: str,  **kwargs) -> object:
		"""
		Creates and saves a staff user with the given email and password.
		"""
		user = self.create_user(
			email=email,
			password=password,
			customer_id=None,
            **kwargs
		)
		user.internal_staff = True
		user.save(using=self._db)
		return user

	def create_superuser(self, email: str, password: str, **kwargs) -> object:
		"""
		Creates and saves a superuser with the given email and password.
		"""
		user = self.create_user(
			email=email,
			password=password,
			customer_id=None,
            **kwargs
		)
		user.internal_staff = True
		user.internal_admin = True
		user.save(using=self._db)
		return user

	def create_customer_admin(self, email, password, customer_id, email_confirmed=False, *args, **kwargs):
		"""
		Creates and saves a superuser with the given email and password.
		"""
		if customer_id is None:
			raise ValueError("Create tenant superuser requires tenant code or pk"
		)
		user = self.create_user(
			email,
			password=password,
			customer_id=customer_id,
			first_name=kwargs.get("first_name", None),
			last_name=kwargs.get("last_name", None)
		)
		user.customer_staff = True
		user.customer_admin = True
		user.email_confirmed = email_confirmed
		user.save(using=self._db)
		return user


class User(AbstractBaseUser):
  	# Override default id
	id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	customer = models.ForeignKey(
		to=Customer, on_delete=models.PROTECT, related_name="users", null=True,
		blank=True
	)
	email = models.EmailField(
		verbose_name="email address", max_length=255, unique=True,
	)
	first_name = models.CharField(max_length=100, blank=True, null=True)
	last_name = models.CharField(max_length=100, blank=True, null=True)
	info = models.CharField(max_length=250, blank=True, null=True)

	active = models.BooleanField(default=True)
	email_confirmed = models.BooleanField(default=False)

	customer_staff = models.BooleanField(default=False) # Customer Staff User
	customer_admin = models.BooleanField(default=False) # Customer Admin User
	internal_customer_admin = models.BooleanField(default=False) # Internal Customer Level Admin (Sudo into Client Account)
	
	internal_staff = models.BooleanField(default=False) # Internal Global Staff User
	internal_admin = models.BooleanField(default=False) # Internal Global Admin User

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = [] # Email & Password are required by default.

	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)

	objects = UserManager()

	class Meta:
		db_table = "cust_user"
		verbose_name = "User"
		verbose_name_plural = "Users"
		ordering = ("pk",)

	@property
	def username(self):
		return self.email
	
	@property
	def get_full_name(self):
		if self.first_name and self.last_name:
			return f"{self.first_name} {self.last_name}"
		else:
			return self.email

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
		return self.internal_staff

	@property
	def is_admin(self):
		"Is the user a admin member?"
		return self.internal_admin
		
	@property
	def is_active(self):
		"Is the user active?"
		return self.active

	def __str__(self):
		return self.get_full_name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Subscription(models.Model):
	# ID Override to align with rest of structure
	id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	code = models.CharField(max_length=50)
	name = models.CharField(max_length=500, blank=True, null=True)
	description = models.CharField(max_length=500, blank=True, null=True)
	# Customer Integration Type
	integration = models.CharField(
		max_length=20, blank=True, null=True, choices=CUSTOMER_INTEGRATION_OPTIONS
	)
	meta = JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)
	
	active = models.BooleanField(default=True)
	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "cust_subscription"
		verbose_name = "Subscription"
		verbose_name_plural = "Subscriptions"
		ordering = ("pk",)

	def __str__(self):
		return f"{str(self.code)} - {str(self.integration)}"


class CustomerSubscription(models.Model):
	# ID Override to align with rest of structure
	id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="subscriptions")
	subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT, related_name="customer_subscriptions")
	active_date = models.DateTimeField(blank=True, null=True) # Active from date
	deactive_date = models.DateTimeField(blank=True, null=True)
	payment_active_date = models.DateTimeField(blank=True, null=True) # Payment Method Actively Linked to Subscription
	
	meta = JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)
	
	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "cust_customer_subscription"
		verbose_name = "Customer Subscription"
		verbose_name_plural = "Customer Subscriptions"
		ordering = ("pk",)

	@property
	def is_active(self):
		if self.deactive_date is None:
			return True
		elif self.deactive_date < timezone.now():
			return True
		return False

	def __str__(self):
		return f"{str(self.customer)} - {self.subscription} ({str(self.is_active)})"


@receiver(post_save, sender=CustomerSubscription)
def customer_subscription_post_save_handler(sender, instance, **kwargs):
	cache.delete(f"customer_config:{instance.customer_id}")


@receiver(post_delete, sender=CustomerSubscription)
def customer_subscription_post_delete_handler(sender, instance, **kwargs):
	cache.delete(f"customer_config:{instance.customer_id}")


class CustomerUsage(models.Model):
	# ID Override to align with rest of structure
	id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
	USAGE_UNIT_TYPE_OPTIONS = (
		("<>", "Usage Unit"),
	)
	customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="usage")
	observation_datetime = models.DateTimeField()
	unit_type = models.CharField(max_length=10, choices=USAGE_UNIT_TYPE_OPTIONS)
	units = models.IntegerField(blank=True, null=True)
	meta = JSONField(encoder=DjangoJSONEncoder, blank=True, null=True)
	
	created_on = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "cust_usage"
		verbose_name = "Customer Usage"
		verbose_name_plural = "Customers Usage"
		ordering = ("pk",)

	def __str__(self):
		return f"{str(self.observation_datetime)}: {str(self.units)} ({str(self.unit_type)})"