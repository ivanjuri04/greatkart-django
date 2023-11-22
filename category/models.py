from django.db import models
from django.urls import reverse
# Create your models here.

class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.SlugField(max_length=180,unique=True)
    description=models.CharField(max_length=250,blank=True)##blank=True da je opcijonalno
    cat_image=models.ImageField(upload_to='photos/categories/',blank=True)

    class Meta:   ##ako je krivo deklinira stavimo kako da pise u panelu
        verbose_name='category'
        verbose_name_plural='categories'


    def get_url(self):
        return reverse('products_by_catrgory',args=[self.slug])
    

    def __str__(self):
        return self.category_name ##kako se u textu prikaze instanca tog modela
    

