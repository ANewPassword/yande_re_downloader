# -*- coding: utf-8 -*-

from os import _exit
from asyncio import exceptions
import requests
from requests.packages import urllib3
from urllib.parse import unquote
import queue
import threading
from time import sleep, time, localtime, strftime
from random import uniform
from func.database import SQLLITE
from func.fileio import file_mkdir, file_is_exist, file_write_binary, file_write_stream, file_write, file_delete, file_size
from func.log import add_log
from func.debug import debug_info
from func.chksum import md5sum
from core.constant import *

urllib3.disable_warnings()

download_count = 0

class Downloader(threading.Thread):
    def __init__(self, que, path, proxy_address, retry_max, deduplication, chksums, with_metadata, program_path, template_name):
        threading.Thread.__init__(self)
        threading.Thread.daemon = True # 守护进程
        self.que = que
        self.path = path
        self.proxy = proxy_address
        self.retry_max = retry_max
        self.deduplication = deduplication
        self.chksums = chksums
        self.with_metadata = with_metadata
        self.program_path = program_path
        self.template_name = template_name

    def run(self):
        global download_count
        while True:
            if not self.que.empty():
                # sleep(uniform(0.2, 0.5)) # 防止写入日志出错
                file_mkdir(self.path)
                db_handler = SQLLITE(self.program_path, self.template_name)
                db_handler.connect()
                db_handler.install()
                post_list = self.que.get() # 取出一个图片
                post_id = post_list['positioner']['id']
                post_md5 = post_list['positioner']['md5']
                post_url = post_list['positioner']['file_url']
                post_metadata = post_list['download']['metadata']
                post_file_name = post_list['download']['filename']
                post_metadata_filename = post_list['download']['metadata_filename']
                post_header = post_list['download']['header']
                for char in post_file_name: # 判断图片名称是否包含以上字符，如果包含则替换为空字符
                    if char in unsupported_file_name:
                        post_file_name = post_file_name.replace(char, '')
                if file_is_exist(self.path + '/' + post_file_name): # 根据文件名判断图片是否已经存在并提醒
                    add_log("检测到 %s 已存在，将根据下载记录和去重模式决定是否覆盖下载" % post_file_name, 'Warn', debug_info())
                deduplication_check = db_handler.select_post_by_id(post_id)
                # print(deduplication_check)
                if len(deduplication_check) >= 1:
                    if self.deduplication == 'strict':
                        if deduplication_check[0]['md5'] == post_md5:
                            add_log("检测到 %s 有下载记录，上一次下载时间为 %s ，跳过此次下载，本图片的下载描述： %s" % (post_file_name, strftime("%Y-%m-%d %H:%M:%S", localtime(int(deduplication_check[0]['timestamp']))), deduplication_check[0]['description'] if deduplication_check[0]['description'] not in ['', None] else '无'), 'Warn', debug_info())
                            download_count += 1
                            continue
                        else:
                            add_log("检测到 %s 有下载记录，上一次下载时间为 %s ，但校验失败， %s -> %s 不匹配，根据指定的去重模式将覆盖下载，通常出现这种情况的原因为图片已被上传者更新，本图片的下载描述： %s" % (post_file_name, strftime("%Y-%m-%d %H:%M:%S", localtime(int(deduplication_check[0]['timestamp']))), deduplication_check[0]['md5'], post_md5, deduplication_check[0]['description'] if deduplication_check[0]['description'] not in ['', None] else '无'), 'Warn', debug_info())
                    elif self.deduplication == 'sloppy':
                        if deduplication_check[0]['md5'] == post_md5:
                            add_log("检测到 %s 有下载记录，上一次下载时间为 %s ，跳过此次下载，本图片的下载描述： %s" % (post_file_name, strftime("%Y-%m-%d %H:%M:%S", localtime(int(deduplication_check[0]['timestamp']))), deduplication_check[0]['description'] if deduplication_check[0]['description'] not in ['', None] else '无'), 'Warn', debug_info())
                        else:
                            add_log("检测到 %s 有下载记录，上一次下载时间为 %s ，但校验失败， %s -> %s 不匹配，根据指定的去重模式将跳过此次下载，通常出现这种情况的原因为图片已被上传者更新，本图片的下载描述： %s" % (post_file_name, strftime("%Y-%m-%d %H:%M:%S", localtime(int(deduplication_check[0]['timestamp']))), deduplication_check[0]['md5'], post_md5, deduplication_check[0]['description'] if deduplication_check[0]['description'] not in ['', None] else '无'), 'Warn', debug_info())
                        download_count += 1
                        continue
                    elif self.deduplication == 'none':
                        if deduplication_check[0]['md5'] == post_md5:
                            add_log("检测到 %s 有下载记录，上一次下载时间为 %s ，根据指定的去重模式将覆盖下载，本图片的下载描述： %s" % (post_file_name, strftime("%Y-%m-%d %H:%M:%S", localtime(int(deduplication_check[0]['timestamp']))), deduplication_check[0]['description'] if deduplication_check[0]['description'] not in ['', None] else '无'), 'Warn', debug_info())
                        else:
                            add_log("检测到 %s 有下载记录，上一次下载时间为 %s ，但校验失败， %s -> %s 不匹配，根据指定的去重模式将覆盖下载，通常出现这种情况的原因为图片已被上传者更新，本图片的下载描述： %s" % (post_file_name, strftime("%Y-%m-%d %H:%M:%S", localtime(int(deduplication_check[0]['timestamp']))), deduplication_check[0]['md5'], post_md5, deduplication_check[0]['description'] if deduplication_check[0]['description'] not in ['', None] else '无'), 'Warn', debug_info())
                add_log("正在下载 %s" % post_file_name, 'Info', debug_info())
                err_count = 0
                continue_point = False
                def download_and_save():
                    global download_count
                    err_count = 0
                    continue_point = False
                    while True:
                        try:
                            if continue_point:
                                break
                            res = requests.get(post_url, proxies = self.proxy, headers = post_header, verify = False, stream = True) # 下载
                            task_length = int(res.headers.get('content-length', 0))
                            if res.status_code == 200:
                                if not file_write_stream('{}{}{}'.format(self.path, '/', post_file_name), res, 3600): # 写入文件
                                    if err_count < self.retry_max or self.retry_max == -1:
                                        err_count += 1
                                        add_log('%s 下载超时, 正在第 %s 次重试' % (post_file_name, err_count), 'Warn')
                                        continue
                                    else:
                                        add_log('%s 下载超时, 超过最大重试次数' % (post_file_name), 'Error')
                                        continue_point = True
                                        continue
                                if task_length != file_size('{}{}{}'.format(self.path, '/', post_file_name)) and task_length != 0:
                                    if err_count < self.retry_max or self.retry_max == -1:
                                        err_count += 1
                                        add_log('%s 本地文件与远端文件大小不一致, 正在第 %s 次重试' % (post_file_name, err_count), 'Warn')
                                        continue
                                    else:
                                        add_log('%s 本地文件与远端文件大小不一致, 超过最大重试次数' % (post_file_name), 'Error')
                                        continue_point = True
                                        continue
                            elif err_count < self.retry_max or self.retry_max == -1:
                                err_count += 1
                                add_log("%s 请求失败，HTTP错误码： %s ，正在第 %s 次重试" % (post_file_name, res.status_code, err_count), 'Warn', debug_info())
                                continue
                            else:
                                continue_point = True
                                add_log("%s 请求失败，HTTP错误码： %s ，超过最大重试次数" % (post_file_name, res.status_code), 'Error', debug_info())
                                file_delete(self.path + '/' + post_file_name)
                                download_count += 1
                                continue_point = True
                            break
                        except Exception as e:
                            err_count += 1
                            if err_count > self.retry_max and self.retry_max != -1:
                                add_log("%s: %s" % (e.__class__.__name__, e), 'Error', debug_info())
                                file_delete(self.path + '/' + post_file_name)
                                download_count += 1
                                continue_point = True
                            else:
                                add_log("%s: %s ，正在第 %s 次重试" % (e.__class__.__name__, e, err_count), 'Warn', debug_info())
                                continue
                    return continue_point
                if download_and_save():
                    continue_point = False
                    continue
                err_count = 0
                if self.chksums:
                    add_log("%s 下载成功，正在校验文件完整性" % post_file_name, 'Info', debug_info())
                    chksum_res = md5sum('{}{}{}'.format(self.path, '/', post_file_name), post_md5)
                    if chksum_res == True:
                        add_log("%s 校验成功， %s -> %s 匹配" % (post_file_name, post_md5, post_md5), 'Info', debug_info())
                    else:
                        while chksum_res != True and (err_count < self.retry_max or self.retry_max == -1):
                            err_count += 1
                            add_log("%s 校验失败， %s -> %s 不匹配，正在第 %s 次重试" % (post_file_name, chksum_res, post_md5, err_count), 'Warn', debug_info())
                            file_delete(self.path + '/' + post_file_name)
                            if download_and_save():
                                continue_point = True
                                break
                            add_log("%s 下载成功，正在校验文件完整性" % post_file_name, 'Info', debug_info())
                            chksum_res = md5sum('{}{}{}'.format(self.path, '/', post_file_name), post_md5)
                        else:
                            if chksum_res == True:
                                add_log("%s 校验成功，%s -> %s 匹配" % (post_file_name, post_md5, post_md5), 'Info', debug_info())
                                add_log("%s 下载成功" % post_file_name, 'Info', debug_info())
                            if err_count >= self.retry_max and self.retry_max != -1:
                                file_delete(self.path + '/' + post_file_name)
                                add_log("%s 校验失败， %s -> %s 不匹配，超过最大重试次数" % (post_file_name, chksum_res, post_md5), 'Error', debug_info())
                        if continue_point:
                                continue_point = False
                                continue
                else:
                    add_log("%s 下载成功" % post_file_name, 'Info', debug_info())
                if self.with_metadata:
                    add_log("生成元数据文件 %s 成功" % post_metadata_filename, 'Info', debug_info())
                    file_write(self.path + '/' + post_metadata_filename, post_metadata)
                if len(deduplication_check) >= 1:
                    post_update_timestamp = int(time())
                    post_update_description = "%s|于 %s 覆盖下载，原md5： %s ，原时间戳： %s ，本次下载的去重模式： %s" % (deduplication_check[0]['description'], strftime("%Y-%m-%d %H:%M:%S", localtime(post_update_timestamp)), deduplication_check[0]['md5'], deduplication_check[0]['timestamp'], self.deduplication)
                    db_handler.update_post_by_id(post_id, {'id': post_id, 'md5': post_md5, 'timestamp': post_update_timestamp, 'description': post_update_description})
                else:
                    post_insert_timestamp = int(time())
                    strftime("%Y-%m-%d %H:%M:%S", localtime(post_insert_timestamp))
                    post_insert_description = "于 %s 初次下载" % strftime("%Y-%m-%d %H:%M:%S", localtime(post_insert_timestamp))
                    db_handler.insert_post(post_id, post_md5, timestamp = post_insert_timestamp, description = post_insert_description)
                download_count += 1
            else:
                db_handler.close()
                return True
 
def start_download(download_info, thread, path, proxy_address, retry_max, deduplication, chksums, with_metadata, program_path, template_name): # 下载器接口
    global download_count, download_result
    download_count = 0
    download_result = []
    add_log("开始本次下载任务", 'Info', debug_info())
    decoding = 'utf8'
    thread = thread if thread <= len(download_info) else len(download_info)
    que = queue.Queue()
    for i in download_info:
        que.put(i)
    for i in range(thread):
        d=Downloader(que, path, proxy_address, retry_max, deduplication, chksums, with_metadata, program_path, template_name)
        d.start()
    while True: # hold
        if que.empty() and len(download_info) <= download_count:
            add_log("本次下载任务完成", 'Info', debug_info())
            download_count = 0
            break
        sleep(1)