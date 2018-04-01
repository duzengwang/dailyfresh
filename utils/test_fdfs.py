# coding=utf-8
#通过这个类，可以向fastDFS服务器上传文件
from fdfs_client.client import Fdfs_client
#根据配置文件创建客户端对象
#在配置文件中指定了tracker服务器
client=Fdfs_client('/etc/fdfs/client.conf')
#上传文件
result=client.upload_by_file('01.jpg')
#返回文件保存的信息，格式如下
'''
{'Local file name': '01.jpg', 'Remote file_id': 'group1/M00/00/00/wKi7hFq4XAiAc89JAAA2pLUeB60746.jpg', 'Group name': 'group1', 'Storage IP': '192.168.187.132', 'Uploaded size': '13.00KB', 'Status': 'Upload successed.'}
'''
print(result)
