from django.shortcuts import render
from .models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from django.conf import settings
from django.http import Http404
# 使用这个模型进行缓存的读写操作
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Paginator, Page
from haystack.generic_views import SearchView
from utils.page import get_page_list
import json


# Create your views here.
def test(request):
    category = GoodsCategory.objects.get(pk=1)
    context = {'category': category}
    return render(request, 'fdfs_test.html', context)


def index(request):
    # 从缓存中获取数据，方法get(键)
    context = cache.get('index')
    if context is None:
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
        # 加入缓存，set方法的参数为键，值，过期时间（以秒为单位）
        cache.set('index', context, 3600)

    # 读取购物车数量
    context['cart_count'] = get_cart_count(request)
    response = render(request, 'index.html', context)
    # # 最终生成的html:
    # html = response.content.decode()
    # # 在磁盘上写文件
    # with open(settings.GENERATE_HTML, 'w') as f1:
    #     f1.write(html)
    return response


def detail(request, sku_id):
    # 根据编号查询商品
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()

    # 查询所有分类
    category_list = GoodsCategory.objects.all()

    # 最新推荐，查询当前商品同类的最新的两个商品
    # new_list=GoodsSKU.objects.filter(category=sku.category).order_by('-id')[0:2]
    # 根据商品找分类，属于根据多找一：对象.外键
    # 根据分类找商品，属于根据一找多：对象.类名小写_set
    new_list = sku.category.goodssku_set.all().order_by('-id')[0:2]

    # 查询其它商品的陈列
    # 根据多找一：sku.goods
    # 根据一找多：***.goodssku_set
    other_list = sku.goods.goodssku_set.all()

    context = {
        'title': '商品详情',
        'sku': sku,
        'category_list': category_list,
        'new_list': new_list,
        'other_list': other_list,
    }

    # 读取购物车数量
    context['cart_count'] = get_cart_count(request)
    # 保存用户最近浏览的商品信息
    if request.user.is_authenticated():
        # 获取键
        key = 'history%d' % request.user.id

        redis_client = get_redis_connection()
        # 如果这个商品已经存在了，如何处理？
        redis_client.lrem(key, 0, sku_id)
        # 数据类型使用的是list，添加数据的方法为lpush
        redis_client.lpush(key, sku_id)
        # 如果列表个数超过5个，如何处理？
        if redis_client.llen(key) > 5:
            # 如果超过5个，则将最后一个元素扔掉
            redis_client.rpop(key)

    return render(request, 'detail.html', context)


def list_sku(request, category_id):
    # 查询当前分类对象
    try:
        category_now = GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404()

    # 查询所有分类信息
    category_list = GoodsCategory.objects.all()

    # 当前分类的最新的两个商品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    # 排序规则：默认-id 价格price 人气sales
    # 参数键为order，值为1表示默认降序，2表示价格降序，3表示价格升序，4表示人气降序
    order = int(request.GET.get('order', 1))
    if order == 2:
        order_by = '-price'
    elif order == 3:
        order_by = 'price'
    elif order == 4:
        order_by = '-sales'
    else:
        order_by = '-id'

    # 查询当前分类的所有商品，并分页
    slist = category_now.goodssku_set.all().order_by(order_by)
    paginator = Paginator(slist, 1)
    # 分页总数
    total_page = paginator.num_pages

    # 接收参数页码
    pindex = int(request.GET.get('pindex', 1))
    # 验证页码的有效性
    if pindex <= 1:
        pindex = 1
    if pindex >= total_page:
        pindex = total_page

    # 获取指定页的数据
    page = paginator.page(pindex)

    # 构造页码信息1 2 3 4 5 range(n-2,n+3)
    page_list = []
    # 判断是否超过了5页数据
    if total_page <= 5:
        page_list = range(1, total_page + 1)
    elif pindex <= 2:  # 如果当前页码小于2,则不满足公式，直接构造页码列表
        page_list = range(1, 5)  # 如果当前页码是最后两页，则不满足公式，直接构造页码列表
    elif pindex >= total_page - 1:
        page_list = range(total_page - 4, total_page + 1)  # 10==>6 7 8 9 10
    else:
        page_list = range(pindex - 2, pindex + 3)

    context = {
        'title': '商品列表',
        'category_list': category_list,
        'category_now': category_now,
        'new_list': new_list,
        'page': page,
        'page_list': page_list,
        'order': order,
    }
    # 读取购物车数量
    context['cart_count'] = get_cart_count(request)

    return render(request, 'list.html', context)


class MySearchView(SearchView):
    """My custom search view."""
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title']='全文搜索结果'
        #计算页码列表
        total_page = context['paginator'].num_pages
        pindex = context['paginator'].number
        context['page_list'] = get_page_list(total_page,pindex)
        #读取购物车数量
        context['cart_count'] = get_cart_count(self.curr_request)
        return context

def get_cart_count(request):
    #读取购物车数量
    total_count = 0
    if request.user.is_authenticated():
        #如果已经登录则从redis中读取
        redis_client = get_redis_connection()
        for count in redis_client.hvals('cart%d'%request.user.id):
            total_count += int(count)
    else:
        #如果未登录则从cookie中读取
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            for k,v in cart_dict.items():
                total_count += v
    return total_count