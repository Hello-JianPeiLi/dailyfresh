# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/08/24 11:42
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from fdfs_client.client import get_tracker_conf
from dailyfresh import settings


class FDFSStorage(Storage):

    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf
        if base_url is None:
            base_url = settings.FDFS_STORAGE_URL
        self.base_url = base_url

    def _open(self, name):
        """django打开文件时使用"""
        pass

    def _save(self, name, content):
        """django保存文件时使用"""
        # name:保存的文件名
        # content:包含上传文件内容的File对象

        # 创建对象，将文件商户餐到fastdfs的类
        client_conf = get_tracker_conf(self.client_conf)

        client = Fdfs_client(client_conf)

        res = client.upload_by_buffer(content.read())
        # buffer返回
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }

        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到fastdfs失败')
        filename = res.get('Remote file_id').decode()

        return filename

    def exists(self, name):
        """django判断文件名是否可用，调用_save前调用,文件存储在fdfs所以不存在文件名不可用,返回False"""
        return False

    def url(self, name):
        return self.base_url + name
