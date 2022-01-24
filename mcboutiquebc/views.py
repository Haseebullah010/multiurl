from django.shortcuts import render
from django.http import HttpResponse
import json, csv, uuid, shutil
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from csv import writer
import re
from selenium import webdriver
from webdriver_manager import driver
from webdriver_manager.chrome import ChromeDriverManager

base_url = 'https://www.trendyol.com/'


def index(request):
    return render(request, 'home.html')


def getCategoryLength(request):
    input_file = open(request.POST.get('category'),"r+")
    reader_file = csv.reader(input_file)
    value = len(list(reader_file)) - 1
    productLength = json.dumps({
        'categoryLength': value
    })
    return HttpResponse(productLength, content_type='application/json') 


#Get Product URLs (For Now Predefined)

def multiproduct(request):
    
    finals_links = []
    # try:
    name = request.POST.get('textarea1')
    print(name)
    name = name.replace("\n", "")
    name = name.replace("\r", "")
    print(name)
    link_list =  name.split(",")


    for link in link_list:
        print ("in for loop")
        lenthofhttpinllink=len(re.findall("http", link))
        if lenthofhttpinllink == 1 or 0:
            print ("solo link",link)
            finals_links.append(link)
        else:
            location=[m.start() for m in re.finditer("http", link)]
            print (location)
            for i in range(lenthofhttpinllink):

                if i == 0:
                    first_list = link[location[0]:location[1]]
                    print ("first link in connected links",first_list)
                    finals_links.append(first_list)
                elif i + 1 == lenthofhttpinllink :
                    last_link = link[location[i]:]
                    finals_links.append(last_link)
                    print ("last link",last_link)
                elif (i != 0) or (i + 1 != lenthofhttpinllink):
                    print (i)
                    centerd_link=link[location[i]:location[i+1]]
                    finals_links.append(centerd_link)
                    print ("centerd_link",centerd_link)

                print ("value of i",i)

        print (lenthofhttpinllink)
        print (link)
    print ("final link list =", finals_links)
    print (len(finals_links))

    if len(finals_links)==0:
        return render(request,"home.html")

    
    # urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', name)
    # print (urls)

    # print(re.search("(?P<url>https?://[^\s]+)", name).group("url"))


    # word = "http"
    # string1 = name
    # location=[m.start() for m in re.finditer(word, name)]

    # # location = name.find_all(word)
    # print (location[1])
    # print (string1[location[0]:location[1]])

    # print ("total length of http",len(re.findall(word, string1)))

    # link_list =  name.split(",")
    # print (link_list)
    # print (link_list[0])

     
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.add_argument('--no-sandbox')    
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {
        "translate_whitelists": {"tr":"en"},
        "translate":{"enabled":"true"}
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    driver.maximize_window()

    driver.get(base_url + 'bebek-giyim-x-c104158')
    driver.implicitly_wait(3)

    result = getEachProduct(finals_links,driver)
    

    return render(request, 'home.html', {
        'file': '/static/products/general2.csv'
    })
    


#Get Each Product Data
def getEachProduct(products, driver):
    print ("in each product")
    image_urls = []
    sizes = []

    i = 0
    for val, x in enumerate(products):
        print(val, x)
        driver.get(x)
        driver.implicitly_wait(4)

        #Get Product Name
        try:
            title = driver.find_element_by_class_name('pr-new-br').text
            print ("title",title)
           
        except:
            print("Product Name Error")
            pass

         #Get Product Images
        images = []
        try:
            images = driver.find_elements_by_class_name('slc-img')
            image_urls = []
            for img in images:
                url = img.find_element_by_tag_name('img')
                image_urls.append(url.get_attribute('src'))
            if not image_urls:
                temp = driver.find_element_by_xpath('//div[@class="product-slide focused"]')
                image_urls.append(temp.find_element_by_tag_name('img').get_attribute('src'))
            images = ';'.join(str(e) for e in image_urls)
            images = images
            # productImageUrlList.append(images)
        except NoSuchElementException:
            if driver.find_elements_by_class_name('base-product-image'):
                img = driver.find_element_by_class_name('base-product-image')
                url = img.find_element_by_tag_name('img')
                images = url.get_attribute('src')
                images = images
                # productImageUrlList.append(images)
                print(images, 'nosuchelement1')
            else:
                # titleList.pop()
                pass
        except NoSuchElementException:
            titleList.pop()
            print("Product Pictures Error")
            pass

        #Get Product Description
        try:
            description = driver.find_element_by_id('content-descriptions-list').text
            description = description
        except:
            description = ''

       
        #Get Product Price
        try:
            temp = driver.find_element_by_class_name('container-right-content')
            temp = temp.find_element_by_class_name('product-price-container')
            temp1 = temp.find_element_by_xpath('//div[@class="pr-bx-nm with-org-prc"]')
            price = temp1.find_element_by_class_name('prc-org').text
            price = price[:-3]
            price = price.replace(",", ".")
            if not price:
                temp1 = temp.find_element_by_xpath('//div[@class="pr-bx-nm"]')
                price = temp1.find_element_by_xpath('//span[@class="prc-slg prc-slg-w-dsc"]').text
                price = price[:-3]
                price = price.replace(",", ".")
            price = price
            # priceList.append(float(price))
        except:
            print("Product Price Error")
            price = '50'
            price = price
            # priceList.append(float(50))
        
        #Get Size
        try:
            size_chart = driver.find_elements_by_class_name('sp-itm')
            sizes = []
            for size in size_chart:
                sizes.append(size.text)
            if sizes:
                description1 = ';'.join(str(e) for e in sizes)
                productOptionName1List = 'Size'
                productOptionType1List = 'DROP_DOWN'
                productOptionDescription1List = description1

            else:
                productOptionName1List = ''
                productOptionType1List = ''
                productOptionDescription1List = ''

        except:
            productOptionName1List = ''
            productOptionType1List = ''
            productOptionDescription1List = ''

        # Get Color
        try:
            driver.implicitly_wait(3)
            color_list = driver.find_elements_by_css_selector('.slc-img')
            colors = []
            for color in color_list:
                colors.append(color.get_attribute('title'))
            if colors:
                description2 = ';'.join(str(e) for e in colors)
                productOptionName2List='Color'
                productOptionType2List='COLOR'
                productOptionDescription2List=description2

            else:
                productOptionName2List=''
                productOptionType2List=''
                productOptionDescription2List=''

        except:
            
            productOptionName2List=''
            productOptionType2List=''
            productOptionDescription2List=''


        data =  [str("product")+str(i),'product',title,description,images,'2/ All Clothes','','',price,'','False','percent','0','in stock','0',productOptionName1List,productOptionType1List,productOptionDescription1List,productOptionName2List,productOptionType2List,productOptionDescription2List]
        
        print (i)
        print ("overall data for ", data)

        with open('./static/products/general2.csv','a',newline='',encoding='utf-8') as f_object:
  
        # Pass this file object to csv.writer()
        # and get a writer object
            writer_object = writer(f_object)
        
            # Pass the list as an argument into
            # the writerow()
            writer_object.writerow(data)
        
            #Close the file object
            f_object.close()
        print(i, 'hwa')
        i = i+1
        # print ("title list",titleList)
    return data
