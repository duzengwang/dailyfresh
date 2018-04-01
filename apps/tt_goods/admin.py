from django.contrib import admin
from .models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexCategoryGoodsBanner,IndexGoodsBanner,IndexPromotionBanner
from django.conf import settings
from django.shortcuts import render
# from celery_tasks.tasks import generate_index
from django.core.cache import cache
# Register your models here.
class BaseAdmin(admin.ModelAdmin):
    #当对象被添加、修改时，会调用保存的方法
    def save_model(self, request, obj, form, change):
        super().save_model(request,obj,form,change)
        #生成首页静态页面
        from celery_tasks.tasks import generate_index
        generate_index.delay()
        #让缓存立即失效
        cache.delete('index')
    #当对象被删除时，会调用下面这个方法
    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        from celery_tasks.tasks import generate_index
        generate_index.delay()
        cache.delete('index')

class IndexPromotionBannerAdmin(BaseAdmin):
    list_display = ['id','name','url','index']
class GoodsCategoryAdmin(BaseAdmin):
    pass
class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass
class IndexGoodsBannerAdmin(BaseAdmin):
    pass



admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexCategoryGoodsBanner,IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexGoodsBanner,IndexGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner,IndexPromotionBannerAdmin)
