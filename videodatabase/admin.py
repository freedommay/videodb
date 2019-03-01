from .models import *
import xadmin
# Register your models here.


class ContainerAdmin(object):
    list_dispaly = 'name'


class ScenesAdmin(object):
    list_dispaly = 'name'


class ProductCategoryAdmin(object):
    list_dispaly = 'name'


class StyleAdmin(object):
    list_dispaly = 'name'


xadmin.site.register(Container, ContainerAdmin)
xadmin.site.register(Scene, ScenesAdmin)
xadmin.site.register(ProductCategory, ProductCategoryAdmin)
xadmin.site.register(Style, StyleAdmin)
