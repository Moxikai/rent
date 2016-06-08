# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field,Item

class RentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field() #发布id,唯一标识
    title = Field() #标题
    location = Field() #区域
    price = Field() #租金
    unit = Field() #单位
    pay = Field() #支付方式
    tag = Field() #描述关键词
    set =Field() #房屋配置
    #--------------房屋资料-----------------
    area = Field() #面积
    type = Field() #厅室
    floor = Field() #楼层
    address = Field() #详细地址
    name = Field() #联系人
    phone = Field() #联系电话

    #-----------------图片------------------
    updated = Field() #网页更新时间
    image_urls = Field()
    images = Field()

