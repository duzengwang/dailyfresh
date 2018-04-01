def get_page_list(total_page,pindex):
    #通用计算页码的公式[n-2,n+3],n表示当前页码
    # 判断是否超过了5页数据
    if total_page <= 5:
        page_list = range(1, total_page + 1)
    elif pindex <= 2:  # 如果当前页码小于2,则不满足公式，直接构造页码列表
        page_list = range(1, 5)  # 如果当前页码是最后两页，则不满足公式，直接构造页码列表
    elif pindex >= total_page - 1:
        page_list = range(total_page - 4, total_page + 1)  # 10==>6 7 8 9 10
    else:
        page_list = range(pindex - 2, pindex + 3)

    return page_list