# -*- coding: utf-8 -*-
import scrapy
import sys,re
from scrapy.http import Request
from Rent.items import RentItem
reload(sys)
sys.setdefaultencoding('utf-8')

def define_pinpai(item):
    if unicode(u'pinpaigongyu') in item:
        return True
    else:
        return False
def define_zufang(item):
    if unicode(u'整租') in item and unicode(u'pinpaigongyu') not in item:
        return True
    else:
        return False
def define_hezu(item):
    if unicode(u'单间') in item and unicode(u'pinpaigongyu') not in item:
        return True
    else:
        return False
#定义过滤函数
def filter_url(list,func):
    new_list = []
    old_list = []
    for item in list:
        if func(item):
            new_list.append(item)
        else:
            old_list.append(item)
    return new_list,old_list




class TongchengSpider(scrapy.Spider):
    name = "tongcheng"
    test_html = '/Users/guangtouling/Desktop/test.html'
    allowed_domains = ["58.com"]
    start_urls = (
        'http://sz.58.com/chuzu',
    )

    def parse(self, response):
        print '当前在页面%s'%response.url
        f = open(self.test_html,'w')
        f.write(response.body)
        print '网页源代码已写入文件%s'%self.test_html
        #解析记录
        items = response.xpath('//*[@class="t qj-rentd"]').extract()
        #过滤记录
        items_pinpaigongyu = filter_url(items,define_pinpai)[0]
        items_left = filter_url(items,define_pinpai)[1]
        items_danjian = filter_url(items_left,define_hezu)[0]
        items_left = filter_url(items_left,define_hezu)[1]
        items_zufang = filter_url(items_left,define_zufang)[0]
        items_left = filter_url(items_left,define_zufang)[1]
        if len(items_left) > 1:
            print '过滤后仍然有记录,请检查!'
            for item in items_left:
                print item
        print '当前页面租房%s个,品牌公寓%s个,普通合租%s个,普通租房%s个'%(len(items),len(items_pinpaigongyu),len(items_danjian),len(items_zufang))
        #提取品牌公寓链接
        pattern = re.compile('(?<=href=")\S{1,}(?=")')
        pattern1 = re.compile(('(?<=entityId=)\d{1,}(?=\&)'))
        item_url = []
        for item in items_pinpaigongyu:
            urls = pattern.findall(item)
            if urls:
                url = urls[0]
                item_url.append(url)



        #提取合租链接
        for item in items_danjian:
            urls = pattern1.findall(item)
            if urls:
                url = 'http://sz.58.com/hezu/%sx.shtml'%urls[0]
                item_url.append(url)
        #提取租房链接
        for item in items_zufang:
            urls = pattern1.findall(item)
            if urls:
                url = 'http://sz.58.com/zufang/%sx.shtml'%urls[0]
                item_url.append(url)
        print '当前页面获得链接数%s个'%len(item_url)

        for url in item_url:
            print '准备解析网页%s'%url
            if 'pinpaigongyu' in url:
                yield Request(url,callback=self.parse_pinpaigongyu)
            else:
                yield Request(url,callback=self.parse_normal)

        """
    #获取下一页链接
        next_urls = response.xpath('//*[@id="infolist"]/div/a[contains(@class,"next")]/@href').extract()
        if next_urls:
            next_url = 'http://sz.58.com%s'%next_urls[0]
            yield Request(url = next_url,callback=self.parse)
        else:
            print '本次获取链接%s个'%len(item_url)
    """


    #调用解析模板
    def parse_item(self,response):
        if 'pinpaigongyu' in response.url:
            yield self.parse_pinpaigongyu(response)
        else:
            yield self.parse_normal(response)



    #品牌公寓模板
    def parse_pinpaigongyu(self,response):
        print '我使用了品牌'
        item = RentItem()
        titles = response.xpath('//*[@id="headimg"]/div/div/div/h1/text()').extract() #标题
        locations = response.xpath('//*[@id="headimg"]/div/div/div/ul/li/a/text()').extract() #小区
        prices = response.xpath('/html/body/div[3]/div[1]/div[1]/span/text()').extract() #价格,单位
        tags = response.xpath('/html/body/div[3]/div[1]/div[2]/ul/li/text()').extract() #描述关键词
        areas = response.xpath('/html/body/div[4]/div/div[2]/ul/li[1]/span/text()').extract() #面积
        types = response.xpath('/html/body/div[4]/div/div[2]/ul/li[2]/span/text()').extract() #厅室
        floors = response.xpath('/html/body/div[4]/div/div[2]/ul/li[3]/span/text()').extract() #楼层
        addresses = response.xpath('/html/body/div[4]/div/div[2]/ul/li[4]/span/text()').extract() #地址
        phones = response.xpath('/html/body/div[3]/div[2]/span/text()').extract() #联系电话
        sets = response.xpath('/html/body/div[5]/ul/li/text()').extract() #房屋配置
        image_urls = response.xpath('//*[@id="title-img-list"]/li/img/@src').extract() #图片url
        updated = response.xpath('/html/body/div[3]/div[1]/div[2]/span/text()').extract() #网页更新时间
        if titles:
            item['title'] = titles[0]
        else:
            print '标题解析出错'
        item['location']=''
        for location in locations:
            item['location'] +=location
        item['price'] = prices[0]
        item['unit'] = prices[1] #单位
        item['tag'] = ''
        for tag in tags:
            item['tag'] +='-'+tag
        item['area'] = areas[0]
        item['type'] = types[0]
        item['floor'] = floors[0].replace('\t','').replace('\n','').replace(' ','')
        item['address'] = addresses[0]
        item['phone'] = phones[0]
        item['set'] = ''
        for set in sets:
            item['set'] += set
        item['image_urls'] = image_urls
        item['updated'] = updated[0].split('：')[-1].replace('\n','').replace(' ','')
        print item
        yield item


    #普通租房模板
    def parse_normal(self,response):
        print '我使用了普通租房'
        item = RentItem()
        titles = response.xpath('//div[@class="house-title"]/h1/text()').extract()
        updateds = response.xpath('//div[@class="title-right-info cb7 f14 pa"]/span[1]/text()').extract()
        prices = response.xpath('//em[@class="house-price"]/text()').extract()
        units = response.xpath('//div[@class="fl"]/i/text()').extract()
        pays = response.xpath('//*[@class="pay-method f16 c70"]/text()').extract()
        floors = response.xpath('//*[@class="fl house-type c70"]/text()').extract()
        locations = response.xpath('//div[@class="fl xiaoqu c70"]/a/text()').extract()
        address = response.xpath('//div[@class="fl c70"]/text()').extract()
        sets = response.xpath('//li[@class="house-primary-content-li clearfix broker-config"]/div/span/text()').extract()
        phones = response.xpath('//div[@class="fl tel cfff"]/span[1]/text()').extract()
        names = response.xpath('//div[@class="fl tel cfff"]/span[2]/text()').extract()
        image_urls = response.xpath('//ul[@id="leftImg"]/li/img/@src').extract()
        if titles:
            item['title'] = titles[0]
        else:
            print '解析标题出错'
            item['title'] = 'error'
        #区域
        item['location'] = ''
        if locations:
            for location in locations:
                item['location'] +=location +'-'
        if prices:
            item['price'] = prices[0]
        else:
            item['price'] = 0
        if units:
            item['unit'] = units[1].replace('\t','').replace(' ','')
        else:
            item['unit'] = ''
        if pays:
            item['pay'] = pays[0]
        floor_list = []
        for floor in floors:
            floor = floor.replace('\t','').replace('\n','').replace(' ','')
            floor_list.append(floor)
        item['type'] = floor_list[0].split('-')[0]
        item['area'] = floor_list[0].split('-')[1]
        item['floor'] = floor_list[0].split('-')[2]
        item['tag'] = floor_list[1]
        if phones:
            item['phone'] = phones[0]
        else:
            item['phone'] = ''
        item['name'] = names[0]
        item['image_urls'] = image_urls
        print item
        yield item

if __name__ =='__main__':
    list_test =['单间1','整租1','pinpaigongyu']
    filter_url(list_test,define_hezu)
    print filter_url(list_test,define_hezu)