# coding=utf-8
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "dailyfresh.settings"
# 放到Celery服务器上时添加的代码
import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from celery import Celery
from tt_goods.models import GoodsCategory,Goods,GoodsSKU,GoodsImage,IndexCategoryGoodsBanner,IndexGoodsBanner,IndexPromotionBanner
from django.shortcuts import render

app=Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/5')

@app.task
def send_user_active(user):
    # 将账号信息进行加密
    serializer = Serializer(settings.SECRET_KEY, 60 * 60 * 2)
    value = serializer.dumps({'id': user.id})  # 返回bytes
    value = value.decode()  # 转成字符串，用于拼接地址

    # 向用户发送邮件
    # msg='<a href="http://127.0.0.1:8000/user/active/%d">点击激活</a>'%user.id
    msg = '<a href="http://127.0.0.1:8000/user/active/%s">点击激活</a>' % value
    send_mail('天天生鲜账户激活', '', settings.EMAIL_FROM, [user.email], html_message=msg)

@app.task
def generate_index():
    # 查询分类信息
    category_list = GoodsCategory.objects.all()

    # 查询首页轮播图片数据
    banner_list = IndexGoodsBanner.objects.all().order_by('index')

    # 查询首页广告位数据
    adv_list = IndexPromotionBanner.objects.all().order_by('index')

    # 查询分类的推荐商品信息
    for category in category_list:
        # 查询当前分类的推荐文本商品
        category.title_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=0).order_by(
            'index')[0:3]

        # 查询当前分类的推荐图片商品
        category.img_list = IndexCategoryGoodsBanner.objects.filter(category=category, display_type=1).order_by(
            'index')[0:4]

    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'adv_list': adv_list,
    }
    response = render(None, 'index.html', context)
    # 最终生成的html:
    html = response.content.decode()
    # 在磁盘上写文件
    with open(settings.GENERATE_HTML+'/index.html', 'w') as f1:
        f1.write(html)

