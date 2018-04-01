# coding=utf-8
#当前文件名称是固定的，haystack会读取这个文件中的内容，通知whoosh对相应的表及指定的字段，创建索引
from haystack import indexes
from .models import GoodsSKU

class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    """建立索引时被使用的类"""
    #属性名称text是固定
    #document=True表示将来由whoosh生成的索引数据存储在文档中
    #use_template=True表示使用一个模板指定查询的字段
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """从哪个表中查询"""
        return GoodsSKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据"""
        return self.get_model().objects.filter(isDelete=False)