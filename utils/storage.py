from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
class FdfsStorage(Storage):
    def __init__(self):
        self.client = settings.FDFS_CLIENT
        self.server = settings.FDFS_SERVER
    def open(self, name, mode='rb'):
        pass
    def save(self, name, content, max_length=None):
        buffer = content.read()
        client = Fdfs_client(self.client)
        try:
            result = client.upload_by_buffer(buffer)
        except:
            raise
        if result.get('Status') == 'Upload successed.':
            return result.get('Remote file_id')
        else:
            raise Exception('文件上传失败')
    def url(self,name):
        return self.server + name


