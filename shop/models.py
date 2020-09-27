from currencies.models import Currency
from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import datetime
from django.utils import timezone

class Category(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200,
                              db_index=True),
        slug=models.SlugField(max_length=200,
                              db_index=True,
                              unique=True,allow_unicode=True)
    )

    image = models.ImageField(upload_to='categories/%Y/%m/%d',
        blank=False,null=False)

    class Meta:
        # ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])

class Product(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200, db_index=True),
        slug=models.SlugField(max_length=200, db_index=True, allow_unicode=True),
        description=models.TextField(blank=True),
        currency = models.ForeignKey(Currency, on_delete=models.CASCADE,null=True,blank=True),
    )
    category = models.ForeignKey(Category,
        related_name='products',
        on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/%Y/%m/%d',
        blank=False,null=False)
    image1 = models.ImageField(upload_to='products/%Y/%m/%d',
        blank=True)
    image2 = models.ImageField(upload_to='products/%Y/%m/%d',
        blank=True)
    image3 = models.ImageField(upload_to='products/%Y/%m/%d',
        blank=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    HotDeal = models.BooleanField(default=False)
    HotDealAmount = models.IntegerField(default=0)
    HotDeal_valid_to = models.DateField(null=True)

    discount = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
    # class Meta:
        # ordering = ('name',)
        # index_together = (('id', 'slug'),)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])

    def get_discount(self):
        if self.discount:
            return (self.discount / Decimal('100')) \
                   * self.price

    def get_total_price_after_discount(self):
        return self.price - self.get_discount()

    def is_hot_deal(self):
        now = timezone.now().date()
        if self.HotDeal== True:
            if self.HotDeal_valid_to > now:
                return True
        return False

    def is_new(self):
        now = timezone.now()
        two_weeks_ago = now - datetime.timedelta(days=14)
        if self.created > two_weeks_ago:
            return True

        return False

class Feature(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=50, db_index=True),
        feature=models.CharField(max_length=50, db_index=True),
    )
    product = models.ForeignKey(Product,
        related_name='features',
        on_delete=models.CASCADE)