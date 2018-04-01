from django.shortcuts import render
from django.http import JsonResponse,Http404
import json
from tt_goods.models import GoodsSKU
from django_redis import get_redis_connection

# Create your views here.
def add(request):

    #当前将数据进行添加，只支持post请求
    if request.method != 'POST':
        return Http404

    #接收请求的商品编号、数量
    dict = request.POST
    sku_id = dict.get('sku_id','0')
    count = int(dict.get('count',0))

    #不要完全相信js的验证，因为非法的请求者会直接请求地址，
    #不会通过界面操作
    if GoodsSKU.objects.filter(id=sku_id).count() <= 0:
        return JsonResponse({'status':2})
    #判断数量是否合法
    if count <= 0:
        return JsonResponse({'status':3})

    #判断用户是否登录
    if request.user.is_authenticated():
        #如果已经登录，则数据存储在redis中
        redis_client = get_redis_connection()
        #创建键
        key = 'cart%d'%request.user.id
        #1.判断商品是否已经存在
        if redis_client.hexists(key,sku_id):
            #如果此商品已将存在，则数量相加在赋值
            count1 = int(redis_client.hget(key,sku_id))
            count0 = count1 + count
            if count0 > 5:
                count0 = 5
            redis_client.hset(key,sku_id,count0)
        else:
            #如果此商品不存在，则直接加入
            redis_client.hset(key,sku_id,count)
        #计算总数量
        total_count = 0
        #命令hvals表示获取所有属性的值，构成列表返回
        for c in redis_client.hvals(key):
            total_count += int(c)
        return JsonResponse({'status':1,'total_count':total_count})
    else:
        #如果未登录，则数据存储在cookies中
        #修改原有字典的数据，更新购物车信息
        #先读取原来的购物车数据
        cart_str = request.COOKIES.get('cart')
        #将字符串转换成字典
        if cart_str:
            cart_dict = json.loads(cart_str)
        else:
            cart_dict = {}
        #将购物车的数据进行更新
        #判断：如果购物车中此商品已经存在，则更新数量
        if sku_id in cart_dict:
            count = cart_dict[sku_id] + count
            #判断是否超过购买上限
            if count > 5:
                count = 5
            cart_dict[sku_id] = count
        else:
            #如果购物车中没有此商品，则添加
            cart_dict[sku_id] = count

        #计算商品数量并返回
        total_count = 0
        for k,v in cart_dict.items():
            total_count += v

        #将字典转换成字符串，因为cookie中存储的数据是字符串类型
        cart_str = json.dumps(cart_dict)
        #创建响应对象,写cookie
        response = JsonResponse({'status':1,'total_count':total_count})
        response.set_cookie('cart',cart_str,expires=60*60*24*14)
        return response
def index(request):
    sku_list = []
    if request.user.is_authenticated():
        #如果登录，则从redis中读取数据
        redis_client = get_redis_connection()
        id_list = redis_client.hkeys('cart%d'%request.user.id)

        for id1 in id_list:
            sku = GoodsSKU.objects.get(pk=id1)
            sku.cart_count = int(redis_client.hget('cart%d'%request.user.id,id1))
            sku_list.append(sku)

            # print(sku_list)
    else:
        #如果未登录，则从cookie中读取数据
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            #将字符串转换成字典{id：couunt}
            cart_dict = json.loads(cart_str)
            #遍历字典，查询商品
            for k,v in cart_dict.items():
                sku = GoodsSKU.objects.get(pk=k)
                sku.cart_count = v
                sku_list.append(sku)
                # print(sku_list)
    context = {
        'title':'购物车',
        'sku_list':sku_list,
    }
    # response = render(request,'cart.html',context)
    # response.delete_cookie('cart')
    # return response
    return render(request,'cart.html',context)

def edit(request):
    if request.method != 'POST':
        return Http404
    dict = request.POST
    sku_id = dict.get('sku_id','0')
    count = int(dict.get('count',0))

    if GoodsSKU.objects.filter(id = sku_id).count() <= 0:
        return JsonResponse({'status':2})
    if count <= 0:
        count = 0
    elif count > 5:
        count = 5
    response = JsonResponse({'status':1})

    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        redis_client.hset('cart%d'%request.user.id,sku_id,count)
    else:
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            cart_dict[sku_id] = count
        cart_str = json.dumps(cart_dict)
        response.set_cookie('cart',cart_str,expires=60*60*24*14)
    return response
def delete(request):
    #只支持post请求
    if request.method != 'POST':
        return Http404
    sku_id = request.POST.get('sku_id')
    response = JsonResponse({'status':1})
    #登录请求创建redis连接
    if request.user.is_authenticated():
        redis_client = get_redis_connection()
        redis_client.hdel('cart%d'%request.user.id,sku_id)
    else:
        #未登录写入cookie
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            cart_dict.pop(sku_id)
            cart_str = json.dumps(cart_dict)
            response.set_cookie('cart',cart_str,expires=60*60*24*14)

    return response