from django.db import models
# class ItemManager(models.Manager):
#     def cheap_item(self):
#         return self.filter(item_price__lt=5)
#     def expensive_item(self):
#         return self.filter(item_price__gt=5)
#
#     def search_item(self,keyword):
#         return self.filter(item_name__icontains=keyword)

class ItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    def deleted(self):
        return super().get_queryset().filter(is_deleted=False)
