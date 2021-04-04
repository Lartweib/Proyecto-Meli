from bs4 import BeautifulSoup as BS
import requests
import re

#Solicitar ingreso de busqueda
busqueda = input('Especifique que desea buscar en ML: ').lower()
#normalizar busquedas para insertar en el link
busqueda_ml = busqueda.replace(' ', '-')
busqueda_ml = busqueda_ml.replace('+','þ')

#generacion del link de busqueda de ml
link_ml = 'https://listado.mercadolibre.com.ar/'+busqueda_ml+'_OrderId_PRICE'

#creacion de archivo csv y escritura de encabezados
archivo_out = open('consulta '+busqueda+'.csv','w',encoding = 'utf-8')
archivo_out.write(link_ml+'\n')
archivo_out.write('Titulo,Precio,Cantidad,Ventas,Vendedor,Link\n')

#solicitud del html de la web
response = requests.get(link_ml)
response.encoding = 'utf-8'
archivo_html = response.text

#creacion del dom parseado de la web
dom = BS(archivo_html, features = 'html.parser')

#extraccion de las distintas publicaciones listadas
publicaciones = dom.find_all('div', class_='ui-search-result__content-wrapper')

#iteracion de extraccion de datos
for publicacion in range(len(publicaciones)):
    try:
        #Extraer el titulo de la publicacion
        titulo = publicaciones[publicacion].div.a['title']
        titulo = titulo.lower()
              
        #normalizo las , que pudiera haber en el titulo
        titulo = titulo.replace(',', ' ')
        
        #Extraer el link de la publicacion
        link = publicaciones[publicacion].div.a['href']
                    
        #Extraer el precio de la publicacion            
        precio_busq = str(publicaciones[publicacion].find('span', class_='price-tag-fraction'))
        pos = precio_busq.find('">')
        pos_final = precio_busq.find('</')
        precio = (precio_busq[pos+2:pos_final])
        precio = precio.replace('.','')
        precio = str(precio)
        
        #Conexion con el link de la publicacion
        response_prod = requests.get(link)
        response_prod.encoding = 'utf-8'
        archivo_html_prod = response_prod.text
        dom_prod = BS(archivo_html_prod, features = 'html.parser')
        
        #Extraer cantidad disponible en la publicacion
        cantidad_busq = str(dom_prod.find('span', class_='ui-pdp-buybox__quantity__available'))
        pos = cantidad_busq.find('(')
        pos_final = cantidad_busq.find('</')
        cantidad = (cantidad_busq[pos+1:pos_final-1])
        if re.search('No', cantidad): cantidad = '1'
        else: continue 
                    
        #Extraer el nombre del vendedor    
        vendedor_busq = str(dom_prod.find('span', class_='ui-pdp-color--BLUE'))
        pos = vendedor_busq.find('">')
        pos_final = vendedor_busq.find('</')
        vendedor = (vendedor_busq[pos+2:pos_final])
        
        #Extraer el numero de ventas de la publicacion
        ventas_busq = str(dom_prod.find_all('span', class_="ui-pdp-subtitle"))
        pos = ventas_busq.find('| ')
        pos_final = ventas_busq.find('</')
        ventas = (ventas_busq[pos+3:pos_final])
        if re.search('vendido', ventas):
            continue
        else: ventas = '0 vendidos'

        #escritura de datos en el csv por cada publicacion iterada
        archivo_out.write(titulo+','+precio+','+cantidad+','+ventas+','+vendedor+','+link+'\n') 
        
        #print(titulo+','+precio + '\n')
         
    except: continue
    
    
archivo_out.close()     
print('Se creo el archivo .csv correctamente')
