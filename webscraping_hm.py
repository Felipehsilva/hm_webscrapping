import re
import os
import requests
import logging
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import numpy as np
import sqlite3
from sqlalchemy import create_engine


# ******************************************** DATA COLLECTION **************************************************************************************************************************************

def data_collection( url, headers):

    # Request to URL
    page = requests.get(url,headers=headers)


    #Beautiful soup object
    soup = BeautifulSoup( page.text, 'html.parser' )

    # =========================Product Data ============================================================
    products = soup.find( 'ul', class_='products-listing small' )

    product_list = products.find_all( 'article', class_='hm-product-item')

    # product id
    product_id = [p.get( 'data-articlecode' ) for p in product_list]

    # product category
    product_category = [p.get( 'data-category' ) for p in product_list]

    # product name
    product_list = products.find_all( 'a', class_='link' )
    product_name = [p.get_text() for p in product_list]

    # price
    product_list = products.find_all( 'span', class_='price regular' )
    product_price = [p.get_text() for p in product_list]

    data = pd.DataFrame( [product_id, product_category, product_name,product_price] ).T
    data.columns = ['product_id', 'product_category', 'product_name','product_price']

    return data



#******************************************** DATA COLLECTION  BY PRODUCT**************************************************************************************************************************************

def data_collection_by_product (data, headers):

    # empty dataframe
    df_compositions = pd.DataFrame()
    # unique columns for all products
    aux = []


    df_pattern = pd.DataFrame( columns=['Art. No.', 'Composition', 'Fit', 'Product safety', 'Size'] )

    for i in range(len(data)):
        #API Request
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id']+ '.html'
        logger.debug ('Product: %s', url)
        page = requests.get( url, headers=headers )
        
        # Beautiful Soup object
        soup = BeautifulSoup( page.text, 'html.parser' )
        
        # ==================== color name =================================
        #para pegar a cor pré selecionada do site que tem tag diferente e não estava sendo pegada 
        product_list = soup.find_all( 'a', class_='filter-option miniature active' ) + soup.find_all( 'a', class_='filter-option miniature' )
        color_name = [p.get( 'data-color' ) for p in product_list]
        
        # product id
        product_id = [p.get( 'data-articlecode' ) for p in product_list]
        df_color = pd.DataFrame( [product_id, color_name] ).T
        df_color.columns = ['product_id', 'color_name']
        
        for j in range(len(df_color)):
            #API Request
            url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id']+ '.html'
            
            logger.debug ('Color: %s', url) 
            #page = requests.get( url, headers=headers )

            # Beautiful Soup object
            # soup = BeautifulSoup( page.text, 'html.parser' )

            # ==================== Product Name =================================
            product_name = soup.find_all('h1', class_ = 'primary product-item-headline')
            product_name = product_name[0].get_text()
        
            # ==================== Product Price =================================
            product_price = soup.find_all('div', class_ = 'primary-row product-item-price')
            product_price =re.findall(r'\d+\.?\d+',product_price[0].get_text())[0]
        


            # ==================== composition =================================
            product_composition_list = soup.find_all( 'div',class_='pdp-description-list-item' )
            product_composition = [list( filter( None, p.get_text().split( '\n' ) ) ) for p in product_composition_list]
            # reaname dataframe
            df_composition = pd.DataFrame( product_composition ).T
            df_composition.columns = df_composition.iloc[0]
            # delete first row
            df_composition = df_composition.iloc[1:].fillna( method='ffill' )


            #remove pocket lining, shell abd lining
            #usado str ao invés de lambda, pois ela aplica a função sobre uma series, mas poderia usar apply
            df_composition['Composition'] = df_composition['Composition'].str.replace('Pocket lining: ','', regex = True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Shell: ','', regex = True)
            df_composition['Composition'] = df_composition['Composition'].str.replace('Lining: ','', regex = True)

            # garantee the same number of columns
            df_composition = pd.concat( [df_pattern, df_composition], axis=0 )
            df_composition['product_name'] = product_name
            df_composition['product_price'] = product_price

            # rename columns
            df_composition.columns = ['product_id','composition','fit','product_safety','size','product_name','product_price']
            
            #pego todos os nomes das colunas
            aux = aux + df_composition.columns.tolist()
            # merge data color + decomposition
            df_composition = pd.merge(df_composition, df_color, how='left', on= 'product_id' )

            # all products
            df_compositions = pd.concat( [df_compositions, df_composition], axis=0 )
    


    # Join Showroom data + details

    df_compositions['style_id'] = df_compositions['product_id'].apply( lambda x: x[:-3] )
    df_compositions['color_id'] = df_compositions['product_id'].apply( lambda x: x[-3:] )
    # scrapy datetime (comum ao fazer scrapping )
    df_compositions['scrapy_datetime'] = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )

    return df_compositions
#******************************************** DATA CLEANING**************************************************************************************************************************************

def data_cleaning(data_product):

    # product id
    df_data = data_product.dropna( subset=['product_id'] )

    # product name
    df_data['product_name'] = df_data['product_name'].str.replace('\n','')
    df_data['product_name'] = df_data['product_name'].str.replace('\t','')
    df_data['product_name'] = df_data['product_name'].str.replace('  ','')
    df_data['product_name'] = df_data['product_name'].str.replace(' ','_').str.lower()
    # product price
    df_data['product_price'] = df_data['product_price'].astype( float )


    # color name
    df_data['color_name'] = df_data['color_name'].str.replace(' ','_').str.lower()
    # fit
    df_data['fit'] = df_data['fit'].apply( lambda x: x.replace( ' ', '_' ).lower() if pd.notnull( x ) else x )
    # size number
    df_data['size_number'] = df_data['size'].apply( lambda x: re.search( '\d{3}cm', x ).group(0) if pd.notnull( x ) else x )
    df_data['size_number'] = df_data['size_number'].apply( lambda x: re.search( '\d+', x ).group(0) if pd.notnull( x ) else x )
    # size model
    df_data['size_model'] = df_data['size'].str.extract( '(\d+/\\d+)' )





    # break composition by comma
    df1 = df_data['composition'].str.split( ',', expand=True ).reset_index(drop=True)
    # cotton | polyester | elastano | elasterell
    df_ref = pd.DataFrame( index=np.arange( len( df_data ) ),columns=['cotton','polyester', 'elastane', 'elasterell'] )

    # ================================composition===============================================================================
    # --------cotton------------
    df_cotton_0 = df1.loc[df1[0].str.contains('Cotton', na= True),0]
    df_cotton_0.name = 'cotton'

    df_cotton_1 = df1.loc[df1[1].str.contains('Cotton', na= True),1]
    df_cotton_1.name = 'cotton'

    # combine
    df_cotton = df_cotton_0.combine_first(df_cotton_1)

    df_ref = pd.concat( [df_ref, df_cotton ], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last')]

    #------------polyester--------------------
    df_polyester_0 = df1.loc[df1[1].str.contains( 'Polyester', na=True ), 0]
    df_polyester_0.name = 'polyester'
    df_polyester_1 = df1.loc[df1[1].str.contains( 'Polyester', na=True ), 1]
    df_polyester_1.name = 'polyester'
    # combine
    df_polyester = df_polyester_0.combine_first(df_polyester_1)

    df_ref = pd.concat( [df_ref, df_polyester], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]

    #------------elastano--------------------
    df_elastane_1 = df1.loc[df1[1].str.contains( 'Elastane', na=True ), 1]
    df_elastane_1.name = 'elastane'
    df_elastane_2 = df1.loc[df1[2].str.contains( 'Elastane', na=True ), 2]
    df_elastane_2.name = 'elastane'

    # combine elastane from both columns 1 and 2
    df_elastane = df_elastane_1.combine_first( df_elastane_2 )

    df_ref = pd.concat( [df_ref, df_elastane], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]

    # elasterell
    df_elasterell = df1.loc[df1[1].str.contains( 'Elasterell', na=True ), 1]
    df_elasterell.name = 'elasterell'
    df_ref = pd.concat( [df_ref, df_elasterell], axis=1 )
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated( keep='last') ]


    #join of combine with product_id
    df_aux = pd.concat([df_data['product_id'].reset_index(drop = True),df_ref],axis=1)
    # format composition data
    df_aux['cotton'] = df_aux['cotton'].apply( lambda x: int( re.search('\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['polyester'] = df_aux['polyester'].apply( lambda x: int( re.search('\d+', x).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['elastane'] = df_aux['elastane'].apply( lambda x: int( re.search('\d+', x ).group(0) ) / 100 if pd.notnull( x ) else x )
    df_aux['elasterell'] = df_aux['elasterell'].apply( lambda x: int( re.search('\d+',x ).group(0) ) / 100 if pd.notnull( x ) else x )

    # # final join
    df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0)
    df_data = pd.merge(df_data, df_aux, on = 'product_id', how='left')

    # Drop columns
    df_data = df_data.drop( columns=['size', 'product_safety', 'composition'], axis=1 )
    # Drop duplicates
    df_data = df_data.drop_duplicates()

    return df_data

#******************************************** DATA INSERT**************************************************************************************************************************************

def data_insert( df_data):

    data_insert = df_data[['product_id',
                        'product_name',
                        'color_name',
                        'fit',
                        'product_price',
                        'size_number',
                        'size_model',
                        'cotton',
                        'polyester',
                        'elastane',
                        'elasterell'
                        
                        
                        ]]

    # create db connection data 
    create_engine ('sqlite:///database_hm.sqlite',echo=False)

    #data insert
    data_insert.to_sql('vitrine',con = conn, if_exists='append', index = False)

    return None



if __name__ == '__main__':

    #logging
    path = '/home/felipe/Documentos/Python_DS_ao_Dev/Notebooks/Modulo_9'

    if not os.path.exists(path + 'Logs'):
        os.makedirs(path + 'Logs')

    logging.basicConfig(
    filename = path + 'webscraping_hm.log',
    level = logging.DEBUG, 
    format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
    )   

    logger = logging.getLogger('webscraping_hm')
    
    


    #parameters and constants
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    #URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'

    # data collection
    data =  data_collection(url, headers)
    logger.info('Data collec done')

    # data collection by product
    data_product = data_collection_by_product( data,headers )
    logger.info('data collection by product done')

    # data cleaning
    data_product_cleaned = data_cleaning(data_product)
    logger.info('data cleaning done')
    # data insertion
    data_insert(data_product_cleaned)
    logger.info('data insertion done')