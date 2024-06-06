import os
import re
import sched
import time
from zipfile import ZipFile

import aiofiles
from fastapi import logger
from flask import Flask, jsonify, request, json, send_file, render_template, redirect, url_for, flash
import requests
import asyncio
import config

from main import CrawlerFactory
from var import crawler_type_var

app = Flask(__name__)
app.secret_key = '68f2d2ee5b3c4482b78cf1bbd81324cb'



# db.init_db()

@app.route('/')
def home():
    return jsonify(message="Hello World")


# def process_input_param()

def get_crawler_image_urls(note_id=None):
    logger.logger.info('Crawler xhs: ' + note_id)
    # print(note_id)
    # print(config.XHS_SPECIFIED_ID_LIST)
    config.XHS_SPECIFIED_ID_LIST = [note_id]
    # print(config.XHS_SPECIFIED_ID_LIST)
    crler = CrawlerFactory.create_crawler(platform='xhs')
    crler.init_config(
        platform='xhs',
        login_type='cookie',
        crawler_type='detail',
        start_page=config.CRAWLER_TYPE,
        keyword=config.KEYWORDS
    )

    asyncio.run(crler.start())

    file_name = f'data/xhs/{crler.get_id()}_detail_contents.json'
    with open(file_name, 'r', encoding='utf-8') as file:
        content = file.read()

    objs = json.loads(content)
    if len(objs) < 0:
        return jsonify(message="No data found")

    image_urls = objs[0]['image_list']

    return image_urls


@app.route('/api/v1/crawler/xhs/images', methods=['GET', 'POST'])
def crawler_images_urls():
    share_url = request.form.get('share_url', 'http://xhslink.com/tUiI5K')
    if share_url is None:
        logger.logger.info('输入空的表单参数：share_url')
        return jsonify(message="请输入分享链接")
    response = requests.get(share_url, allow_redirects=False)
    xhs = response.content.decode('utf-8')
    # 第一个匹配项
    matches = re.findall('xiaohongshu.com/discovery/item/(\w+)', xhs)
    note_id = matches[0]

    image_urls = get_crawler_image_urls(note_id)
    return image_urls


@app.route('/api/v1/crawler/xhs', methods=['GET'])
def crawler(share_url='https://xhslink.com/tUiI5K'):
    note_id = request.form.get('note_id', None)
    # share_url = request.form.get('share_url', 'http://xhslink.com/tUiI5K')
    if note_id is None:
        response = requests.get(share_url, allow_redirects=False)
        xhs = response.content.decode('utf-8')
        # 第一个匹配项
        matches = re.findall('xiaohongshu.com/discovery/item/(\w+)', xhs)
        note_id = matches[0]

    image_urls = get_crawler_image_urls(note_id)
    # for img_route in objs[0]['image_list']:

    # 创建一个临时目录来存储下载的图片
    os.makedirs('temp', exist_ok=True)

    # 下载所有图片
    image_files = []
    for i, url in enumerate(image_urls):
        response = requests.get(url)
        image_file = f'temp/{note_id}_image_{i}.jpg'
        with open(image_file, 'wb') as f:
            f.write(response.content)
            image_files.append(image_file)

    # 创建一个zip文件
    image_zip_file = f'temp/{note_id}_images.zip'
    with ZipFile(image_zip_file, 'w') as zipf:
        for i in range(len(image_files)):
            zipf.write(image_files[i], arcname=os.path.basename(image_files[i]))
            # zipf.wr
    # print()
    # 返回zip文件
    return send_file(image_zip_file, as_attachment=True)


@app.route('/input_form', methods=['GET', 'POST'])
def input_form():
    if request.method == 'POST':
        input_value = request.form.get('input_field')
        matches = re.findall('(https?://xhslink\.com/\w+)', input_value)
        logger.logger.info(input_value)
        logger.logger.info(len(matches))
        if len(matches) == 0:
            flash('无法解析输入内容', 'error')
            return render_template('input_form.html')
        input_val = matches[0]
        # 在这里处理输入值
        logger.logger.info('Input value: ' + input_val)
        print(input_val)
        # print(url_for('crawler', share_url=input_val))
        return crawler(share_url=input_val)
    flash('请输入分享链接', 'Info')
    return render_template('input_form.html')


def scan_temp():
    for root, dirs, files in os.walk('temp'):
        for file in files:
            if os.path.getctime(os.path.join(root, file)) < time.time() - 60 * 60:
                os.remove(os.path.join(root, file))


if __name__ == '__main__':
    print('Start Flask Server')
    s = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)
    s.enter(60 * 60, 1, )
    app.run(host='0.0.0.0', debug=False, port=5000)

    # db.close()
