# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class Invoices(models.Model):
    id = models.IntegerField("id", primary_key=True)
    date_added = models.DateField(blank=True, null=True)
    vendor = models.CharField(max_length=255, blank=True, null=True)
    inv_num = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    ym = models.IntegerField(blank=True, null=True)
    cc = models.IntegerField(blank=True, null=True)
    cc_user = models.CharField(max_length=2, blank=True, null=True)
    approved = models.IntegerField(blank=True, null=True)
    paid = models.IntegerField(blank=True, null=True)
    date_paid = models.DateField(blank=True, null=True)

    def __str__(self):
        return " ".join([self.vendor, "-", self.inv_num])

    class Meta:
        # managed = False
        db_table = "invoices"


class Vendors(models.Model):
    vendor = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    exp_cat = models.CharField(max_length=255, blank=True, null=True)
    approver = models.CharField(max_length=255, blank=True, null=True)
    pmt_type = models.CharField(max_length=255, blank=True, null=True)
    qb_mapping = models.CharField(max_length=255, blank=True, null=True)
    acct_mapping = models.IntegerField(blank=True, null=True)
    ach_aba = models.CharField(max_length=9, blank=True, null=True)
    ach_acct_no = models.CharField(max_length=255, blank=True, null=True)
    ach_vendor = models.CharField(max_length=255, blank=True, null=True)
    idb = models.TextField(
        blank=True, null=True
    )  # This field type is a guess.
    contact = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    template = models.CharField(max_length=255, blank=True, null=True)
    ben_id = models.CharField(max_length=255, blank=True, null=True)
    ben_id_type = models.CharField(max_length=255, blank=True, null=True)
    ben_country = models.CharField(max_length=255, blank=True, null=True)
    ben_bank_id_type = models.CharField(max_length=255, blank=True, null=True)
    ben_bank_id = models.CharField(max_length=255, blank=True, null=True)
    ben_bank_name = models.CharField(max_length=255, blank=True, null=True)
    ben_bank_address_line_1 = models.CharField(
        max_length=255, blank=True, null=True
    )
    ben_bank_address_line_2 = models.CharField(
        max_length=255, blank=True, null=True
    )
    ben_bank_city_st_prov_zip = models.CharField(
        max_length=255, blank=True, null=True
    )
    ben_bank_country = models.CharField(max_length=255, blank=True, null=True)
    int_bank_id_type = models.CharField(max_length=255, blank=True, null=True)
    int_bank_id = models.CharField(max_length=255, blank=True, null=True)
    int_bank_name = models.CharField(max_length=255, blank=True, null=True)
    int_bank_address_line_1 = models.CharField(
        max_length=255, blank=True, null=True
    )
    int_bank_address_line_2 = models.CharField(
        max_length=255, blank=True, null=True
    )
    int_bank_city_st_prov_zip = models.CharField(
        max_length=255, blank=True, null=True
    )
    int_bank_country = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = "vendors"
