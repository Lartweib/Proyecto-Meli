import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import re
from bs4 import BeautifulSoup as BS
import requests

PATH = "D:/Federico/Proyectos GIT/Proyectos/Selenium-Test/chromedriver.exe"

busqueda = input('Especifique que desea buscar en ML: ').lower()
url = 'https://www.mercadolibre.com.ar/'
busqueda_split = busqueda.split(' ')

#

chrome_options = Options()
chrome_options.add_argument("--headless")

# XPath:

path_busqueda = '/html/body/header/div/form/input'
boton_busqueda = '/html/body/header/div/form/button'

# Abrir navegador

driver = webdriver.Chrome(options=chrome_options)

# Maximizar pantalla

driver.maximize_window()

driver.get(url)

# Acciones en la web

driver.find_element_by_xpath(path_busqueda).send_keys(busqueda)
driver.find_element_by_xpath(boton_busqueda).click()

time.sleep(3)

link_ml = str(driver.current_url)

# Creacion de archivo csv y escritura de encabezados
archivo_out = open('consulta '+busqueda+'.csv', 'w', encoding='utf-8')
archivo_out.write(link_ml+'\n')
archivo_out.write('Titulo,Precio,Cantidad,Ventas,Vendedor,Link\n')

# Eextraccion del html
html = driver.execute_script('return document.documentElement.outerHTML')
dom = BS(html, features='html.parser')

# extraccion de las distintas publicaciones listadas
publicaciones = dom.find_all('div', class_='ui-search-result__content-wrapper')


# iteracion de extraccion de datos
for publicacion in range(len(publicaciones)):
    try:
        # Extraer el titulo de la publicacion
        titulo = publicaciones[publicacion].div.a['title']
        titulo = titulo.lower()

        # Corroborar el titulo de la publicacion coincida con la busqueda
        contador = 0
        for i in range(len(busqueda_split)):
            if re.search(busqueda_split[i], titulo):
                contador += 1
                continue
            else:
                break

        if contador == len(busqueda_split):
            # normalizo las , que pudiera haber en el titulo
            titulo = titulo.replace(',', ' ')
            print(titulo)

            # Extraer el link de la publicacion
            link = publicaciones[publicacion].div.a['href']
            print(link)

            # Extraer el precio de la publicacion            
            precio_busq = str(publicaciones[publicacion].find('span', class_='price-tag-fraction'))
            pos = precio_busq.find('">')
            pos_final = precio_busq.find('</')
            precio = (precio_busq[pos+2:pos_final])
            precio = precio.replace('.', '')
            precio = str(precio)
            print(precio)

            # Conexion con el link de la publicacion
            response_prod = requests.get(link)
            response_prod.encoding = 'utf-8'
            archivo_html_prod = response_prod.text
            dom_prod = BS(archivo_html_prod, features='html.parser')

            # Extraer cantidad disponible en la publicacion
            cantidad_busq = str(dom_prod.find('span', class_='ui-pdp-buybox__quantity__available'))
            pos = cantidad_busq.find('(')
            pos_final = cantidad_busq.find('</')
            cantidad = (cantidad_busq[pos+1:pos_final-1])
            if re.search('No', cantidad):
                cantidad = '1'
            print(cantidad)

            # Extraer el numero de ventas de la publicacion
            ventas_busq = str(dom_prod.find_all('span', class_="ui-pdp-subtitle"))
            pos = ventas_busq.find('| ')
            pos_final = ventas_busq.find('</')
            ventas = (ventas_busq[pos+3:pos_final])
            if not re.search('vendido', ventas):
                ventas = '0 vendidos'
            print(ventas)

            # Extraer el nombre del vendedor 
            link_vend = str(dom_prod.find(class_="ui-pdp-media__action ui-box-component__action")['href'])
            pos = link_vend.find('.ar/')
            vendedor = (link_vend[pos+4:])
            print(vendedor)

            # Escritura de datos en el csv por cada publicacion iterada
            archivo_out.write(titulo+','+precio+','+cantidad+','+ventas+','+vendedor+','+link+'\n')
            print(titulo+','+precio+','+cantidad+','+ventas+','+vendedor+','+link+'\n')
            print('ahora si')

    except:
        continue

archivo_out.close()
print('Se creo el archivo .csv correctamente')

# Cerrar driver
driver.quit()
