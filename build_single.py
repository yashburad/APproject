import json
import requests
from bs4 import BeautifulSoup
import random
import sqlite3

def get(url):
    data = requests.get(url )
    soup = BeautifulSoup(data.content,'lxml')
    content = soup.find('div',id='content')
    
    data_dict = {}
    try:
       for table in content.find_all('table', attrs={'class':'info-table'}):
        table_rows = table.find_all('tr')
        for tr in table_rows:
            for th in tr:
                th = tr.find('th')
                td = tr.find('td')
                data_dict[th.text] = str(td.text).replace("\n","").replace("\r","")
    except:
        pass
    

    desc = content.find('div' ,class_ = 'row')
    desc_head = desc.find_all('p')[1]
    data_dict['product_desc'] = str(desc_head.text).replace("\n","").replace("\r","")
    price_html = content.find('canvas' , id = 'pricechart')

    try:
        price_url = price_html['data-url']
        price_json = requests.get(price_url).json()
        data_dict['price'] = price_json['datasets'][0]['data'][1]  
         
    except:
        data_dict['price'] = random.randint(100,5000)

    brand_img_link = content.find('img',class_ = 'lazy pull-right brand-logo')['data-original']
    data_dict['brand_img_link'] =  brand_img_link

    prdct_img_link = content.find('img',class_ = 'thumb')['src']
    data_dict['prdct_img_link'] = prdct_img_link

    #Save json to a file
    # with open('data.json','w+') as file_object:
    #     file_object.write(json.dumps(data_dict))

    return data_dict

def main():
    conn = sqlite3.connect('app/site.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    db_out = c.fetchall()
    pid = len(db_out) + 1
    
    while True:
        url = str(input('Enter the url: '))
        if url == '00':
            break
        try:
            product = get(url=url)
            name =  str(product['Brand:'])  + str(" ") + str(product['Name:'])
            price = int(product['price']) *80
            product_img = product['prdct_img_link']
            brand_img = product['brand_img_link']

            if 'Analog' == product['Display:']:
                category = 1
            elif 'Digital' == product['Display:']:
                category = 2
            elif 'Analog/ Digital' == product['Display:']:
                category = 3
            else:
                category = 0

            if 'Brand:' in product:
                brand = product['Brand:']
            else:
                brand = 'NA'

            if 'Family:' in product:
                family = product['Family:']
            else:
                family = 'NA'
            
            if 'Reference:' in product:
                model = product['Reference:']
            else:
                model = 'NA'
            
            if 'Produced:' in product:
                produced = product['Produced:']
            else:
                produced = 'NA'
            
            if 'Materials:' in product:
                materials = product['Materials:']
            else:
                materials = 'NA'

            if 'Glass:' in product:
                glass = product['Glass:']
            else:
                glass = 'NA'
            
            if 'Diameter:' in product:
                diameter = product['Diameter:']
            else:
                diameter = 'NA'
            
            if 'Height:' in product:
                height = product['Height:']
            else:
                height = 'NA'
            
            if 'W/R:' in product:
                wr = product['W/R:']
            else:
                wr = 'NA'
            
            if 'Color:' in product:
                color = product['Color:']
            else:
                color = 'NA'

            if 'Finish:' in product:
                finish = product['Finish:']
            else:
                finish = 'NA'
            
            if 'Type:' in product:
                type = product['Type:']
            else:
                type = 'NA'
            
            if 'Display:' in product:
                display = product['Display:']
            else:
                display = 'NA'

            if 'Chronograph:' in product:
                chronograph = product['Chronograph:']
            else:
                chronograph = 'NA'
            
            if 'Acoustic:' in product:
                acoustic = product['Acoustic:']
            else:
                acoustic = 'NA'
            
            if 'Additionals:' in product:
                additional = product['Additionals:']
            else:
                additional = 'NA'

            if 'product_desc' in product:
                description = product['product_desc']
            else:
                description = 'NA'
            
            x = [name,description,pid]
            print(x)

            with open('index.json','a+') as fptr:
                fptr.write(json.dumps(x))


            c.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (pid, name, price, product_img, category,brand,family,model,produced,materials,glass,diameter,height,wr,color,finish,type,display,chronograph,acoustic,additional,description,brand_img))

            conn.commit()
            pid +=1
        except:
            print('Exception ignored')
            pass
        

if __name__ == "__main__":
    main()

