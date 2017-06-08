# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (AnimesHD) por Hernan_Ar_c
# ------------------------------------------------------------

import urlparse, urllib2, urllib, re
import os, sys

from core import logger
from core import tmdb
from core import scrapertools
from core import httptools
from core import logger
from core import scrapertools
from core.item import Item
from core import servertools

tgenero = {"Comedia":"https://s32.postimg.org/q7g2qs90l/comedia.png",
               "Drama":"https://s32.postimg.org/e6z83sqzp/drama.png",
               "Acción":"https://s32.postimg.org/4hp7gwh9x/accion.png",
               "Aventura":"https://s32.postimg.org/whwh56is5/aventura.png",
               "Romance":"https://s31.postimg.org/y7vai8dln/romance.png",
               "Ciencia ficción":"https://s32.postimg.org/6hp3tsxsl/ciencia_ficcion.png",
               "Terror":"https://s32.postimg.org/ca25xg0ed/terror.png",
               "Fantasía":"https://s32.postimg.org/pklrf01id/fantasia.png",
               "Misterio":"https://s4.postimg.org/kd48bcxe5/misterio.png",
               "Crimen":"https://s14.postimg.org/5lez1j1gx/crimen.png",
               "Hentai": "https://s27.postimg.org/569jfucg3/hentai.png",
               "Magia":"https://s21.postimg.org/5scanldif/magia.png",
               "Psicológico":"https://s24.postimg.org/wlqntq8fp/psicologico.png",
               "Sobrenatural":"https://s15.postimg.org/izfne2l9n/sobrenatural.png",
               "Torneo":"https://s27.postimg.org/lu5gad5w3/torneo.png",
               "Thriller":"https://s31.postimg.org/4d7bl25y3/thriller.png",
               "Otros": "https://s16.postimg.org/fssbi4nlh/otros.png"}


host = "http://www.animeshd.tv"

headers = [['User-Agent', 'Mozilla/50.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'],
           ['Referer', host]]

def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Ultimas",
                               action="lista",
                               thumbnail='https://s31.postimg.org/3ua9kwg23/ultimas.png',
                               fanart='https://s31.postimg.org/3ua9kwg23/ultimas.png',
                               url=host+'/ultimos'
                               ))

    itemlist.append(item.clone(title="Todas",
                               action="lista",
                               thumbnail='https://s12.postimg.org/iygbg8ip9/todas.png',
                               fanart='https://s12.postimg.org/iygbg8ip9/todas.png',
                               url=host + '/buscar?t=todos&q='
                               ))


    itemlist.append(item.clone(title="Generos",
                               action="generos",
                               url=host,
                               thumbnail='https://s31.postimg.org/szbr0gmkb/generos.png',
                               fanart='https://s31.postimg.org/szbr0gmkb/generos.png'
                               ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url=host + '/buscar?t=todos&q=',
                               thumbnail='https://s31.postimg.org/qose4p13f/Buscar.png',
                               fanart='https://s31.postimg.org/qose4p13f/Buscar.png'
                               ))
    
    return itemlist

def get_source(url):
    logger.info()
    data = httptools.downloadpage(url).data
    data = re.sub(r'\n|\r|\t|&nbsp;|<br>|\s{2,}|"|\(|\)', "", data)
    return data


def lista(item):
    logger.info()

    itemlist = []

    post = ''
    if item.extra in ['episodios']:
        post= {'tipo': 'episodios', '_token':'rAqVX74O9HVHFFigST3M9lMa5VL7seIO7fT8PBkl'}
        post = urllib.urlencode(post)
    data = get_source(item.url)
    logger.debug('data: %s'%data)
    patron = 'class=anime><div class=cover style=background-image: url(.*?)>.*?<a href=(.*?)><h2>(.*?)<\/h2><\/a><\/div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:
        url= scrapedurl
        thumbnail = host+scrapedthumbnail
        title = scrapedtitle
        itemlist.append(item.clone(action = 'episodios',
                                   title=title, 
                                   url=url, 
                                   thumbnail=thumbnail,
                                   contentSerieName = title
                                   ))
    
     # Paginacion
    next_page = scrapertools.find_single_match(data, '<li class=active><span>.*?<\/span><\/li><li><a href=(.*?)>.*?<\/a><\/li>')
    next_page_url = scrapertools.decodeHtmlentities(next_page)
    if next_page_url != "":
        itemlist.append(Item(channel=item.channel,
                             action="lista",
                             title=">> Página siguiente",
                             url=next_page_url,
                             thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'
                             ))
    
    return itemlist

def search(item,texto):
    logger.info()
    texto = texto.replace(" ","+")
    item.url = item.url+texto
    try:
        if texto != '':
            return lista(item)
        else:
            return []
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def generos(item):
    logger.info()
    itemlist=[]

    data = get_source(item.url)
    patron = '<li class=><a href=http:\/\/www\.animeshd\.tv\/genero\/(.*?)>(.*?)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        title=scrapertools.decodeHtmlentities(scrapedtitle)
        if title == 'Recuentos de la vida':
            title='Otros'
        genero = scrapertools.decodeHtmlentities(scrapedurl)
        thumbnail=''
        if title in tgenero:
            thumbnail=tgenero[title]

        url='http://www.animeshd.tv/genero/%s'%genero
        itemlist.append(item.clone(action='lista', title=title, url=url, thumbnail=thumbnail))
    return itemlist


def episodios(item):
    logger.info()
    itemlist =[]
        
    data= get_source(item.url)
    logger.debug('data: %s'%data)
    patron = '<li id=epi-.*? class=list-group-item ><a href=(.*?) class=badge.*?width=25 title=(.*?)> <\/span>(.*?)<\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for scrapedurl, scrapedlang, scrapedtitle in matches:
        language = scrapedlang
        title = scrapedtitle+' (%s)'%language
        url=scrapedurl
        itemlist.append(item.clone(title=title, url=url, action='findvideos', language=language))
    return itemlist
    
def findvideos(item):
    logger.info()
    itemlist=[]
    
    data= get_source(item.url)
    logger.debug('data: %s'%data)
    patron ='<iframe.*?src=(.*?) frameborder=0'
    matches = re.compile(patron, re.DOTALL).findall(data)
    
    for video_url in matches:
        data=get_source(video_url)
        data = data.replace("'",'')
        logger.debug('data findvideos2: %s'%data)
        patron ='file:(.*?),label:(.*?),type'
        matches = re.compile(patron, re.DOTALL).findall(data)
        
        for scrapedurl, scrapedquality in matches:
            url= scrapedurl
            quality = scrapedquality
            title = item.contentSerieName+' (%s)'%quality
            itemlist.append(item.clone(action='play', title=title, url=url, quality=quality))

    return itemlist
        
