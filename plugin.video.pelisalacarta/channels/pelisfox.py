# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Canal (PelisFox) por Hernan_Ar_c
# ------------------------------------------------------------

import urlparse, urllib2, urllib, re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import tmdb
from core import jsontools

tgenero = {"Drama":"https://s32.postimg.org/e6z83sqzp/drama.png",
           u"Accción":"https://s32.postimg.org/4hp7gwh9x/accion.png",
           u"Animación":"https://s32.postimg.org/rbo1kypj9/animacion.png",
           u"Ciencia Ficción":"https://s32.postimg.org/6hp3tsxsl/ciencia_ficcion.png",
           "Terror":"https://s32.postimg.org/ca25xg0ed/terror.png",
           }

audio = {'LAT':'[COLOR limegreen]LATINO[/COLOR]', 'SUB':'[COLOR red]Subtitulado[/COLOR]'}

host = 'http://pelisfox.tv'


def mainlist(item):
    logger.info()

    itemlist = []

    itemlist.append(item.clone(title="Ultimas",
                               action="lista",
                               thumbnail='https://s31.postimg.org/3ua9kwg23/ultimas.png',
                               fanart='https://s31.postimg.org/3ua9kwg23/ultimas.png',
                               url=host+'/estrenos/'
                               ))

    itemlist.append(item.clone(title="Generos",
                               action="seccion",
                               url=host,
                               thumbnail='https://s31.postimg.org/szbr0gmkb/generos.png',
                               fanart='https://s31.postimg.org/szbr0gmkb/generos.png',
                               seccion='generos'
                               ))

    itemlist.append(item.clone(title="Por Año",
                               action="seccion",
                               url=host+'/peliculas/2017/',
                               thumbnail='https://s31.postimg.org/iyl5fvzqz/pora_o.png',
                               fanart='https://s31.postimg.org/iyl5fvzqz/pora_o.png',
                               seccion='anios'
                               ))

    itemlist.append(item.clone(title="Por Actor",
                               action="seccion",
                               url=host + '/actores/',
                               thumbnail='https://s22.postimg.org/ymnctv2r5/por-actor.png',
                               fanart='https://s22.postimg.org/ymnctv2r5/por-actor.png',
                               seccion='actor'
                               ))

    itemlist.append(item.clone(title="Buscar",
                               action="search",
                               url=host +'/api/elastic/suggest?query=',
                               thumbnail='https://s31.postimg.org/qose4p13f/Buscar.png',
                               fanart='https://s31.postimg.org/qose4p13f/Buscar.png'
                               ))

    return itemlist


def lista(item):
    logger.info()

    itemlist = []
    data = httptools.downloadpage(item.url).data
    #logger.debug(data)
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)

    logger.debug(data)
    # return
    if item.seccion != 'actor':
        patron = '<li class=item-serie.*?><a href=(.*?) title=(.*?)><img src=(.*?) alt=><span '
        patron += 'class=s-title><strong>.*?<\/strong><p>(.*?)<\/p><\/span><\/a><\/li>'
    else:
        patron = '<li><a href=(\/pelicula\/.*?)><figure><img src=(.*?) alt=><\/figure><p class=title>(.*?)<\/p><p '
        patron += 'class=year>(.*?)<\/p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail, scrapedyear in matches:
        url = host+scrapedurl
        if item.seccion != 'actor':
            thumbnail = scrapedthumbnail
            contentTitle = scrapedtitle
        else:
            thumbnail = scrapedtitle
            contentTitle = scrapedthumbnail
        plot = ''
        year = scrapedyear
        title = contentTitle + ' ('+year+')'
        itemlist.append(
                        Item(channel=item.channel,
                             action='findvideos',
                             title=title,
                             url=url,
                             thumbnail=thumbnail,
                             plot=plot,
                             contentTitle=contentTitle,
                             infoLabels={'year': year}
                             ))
    tmdb.set_infoLabels_itemlist(itemlist, seekTmdb=True)
    # Paginacion

    if itemlist != []:
        next_page = scrapertools.find_single_match(data, '<li><a class= item href=(.*?)&limit=.*?>Siguiente <')
        next_page_url = host+next_page
        import inspect
        if next_page != '':
            itemlist.append(Item(channel=item.channel,
                                 action="lista",
                                 title='Siguiente >>>',
                                 url=next_page_url,
                                 thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'
                                 ))
    return itemlist


def seccion(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    logger.debug(data)
    if item.seccion == 'generos':
        patron = '<a href=(\/peliculas\/[\D].*?\/) title=Películas de .*?>(.*?)<\/a>'
    elif item.seccion == 'anios':
        patron = '<li class=.*?><a href=(.*?)>(\d{4})<\/a> <\/li>'
    elif item.seccion == 'actor':
        patron = '<li><a href=(.*?)><div.*?<div class=photopurple title=(.*?)><\/div><img src=(.*?)><\/figure>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    if item.seccion != 'actor':
        for scrapedurl, scrapedtitle in matches:
            title = scrapedtitle.decode('utf-8')
            thumbnail = ''
            if item.seccion == 'generos':
                thumbnail = tgenero[title]
            fanart = ''
            url = host+scrapedurl

            itemlist.append(
                Item(channel=item.channel,
                     action="lista",
                     title=title,
                     fulltitle=item.title,
                     url=url,
                     thumbnail=thumbnail,
                     fanart=fanart
                     ))
    else:
        for scrapedurl, scrapedname, scrapedthumbnail in matches:
            thumbnail = scrapedthumbnail
            fanart = ''
            title = scrapedname
            url = host + scrapedurl

            itemlist.append(Item(channel=item.channel,
                                 action="lista",
                                 title=title,
                                 fulltitle=item.title,
                                 url=url,
                                 thumbnail=thumbnail,
                                 fanart=fanart,
                                 seccion = item.seccion
                                 ))
        # Paginacion

        if itemlist != []:
            next_page = scrapertools.find_single_match(data, '<li><a class= item href=(.*?)&limit=.*?>Siguiente <')
            next_page_url = host + next_page
            import inspect
            if next_page != '':
                itemlist.append(item.clone(action="seccion",
                                           title='Siguiente >>>',
                                           url=next_page_url,
                                           thumbnail='https://s32.postimg.org/4zppxf5j9/siguiente.png'
                                           ))

    return itemlist


def busqueda(item):
    logger.info()
    itemlist =[]
    data = httptools.downloadpage(item.url).data
    dict_data = jsontools.load_json(data)
    logger.debug('dict_data: %s'%dict_data)
    resultados = dict_data['result'][0]['options']

    for resultado in resultados:
        logger.debug('resultado: %s' % resultado['_source'])
        if 'title' in resultado['_source']:
            title = resultado['_source']['title']
            thumbnail = 'http://s3.amazonaws.com/pelisfox'+'/'+resultado['_source']['cover']
            plot = resultado['_source']['sinopsis']
            url = host+resultado['_source']['url']+'/'

            itemlist.append(item.clone(title=title,
                                       thumbnail = thumbnail,
                                       plot = plot,
                                       url = url,
                                       action = 'findvideos',
                                       contentTitle= title
                                       ))
    return itemlist




def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = item.url + texto

    if texto != '':
        return busqueda(item)
    else:
        return []

def findvideos(item):
    logger.info()
    itemlist = []
    templist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
    logger.debug('item: %s'%item)
    patron = '<li data-quality=(.*?) data-lang=(.*?)><a href=(.*?) title=.*?'
    matches = matches = re.compile(patron, re.DOTALL).findall(data)
    for quality, lang, scrapedurl in matches:
        url=host+scrapedurl
        title = item.title+' ('+lang+') ('+quality+')'
        templist.append(item.clone(title=title,
                                   language= lang,
                                   url=url
                                   ))

    for videoitem in templist:

        data = httptools.downloadpage(videoitem.url).data
        data = re.sub(r'"|\n|\r|\t|&nbsp;|<br>|\s{2,}', "", data)
        logger.debug(data)
        id = scrapertools.find_single_match(data,'var _SOURCE =.*?source:(.*?),')
        if videoitem.language == 'SUB':
            sub = scrapertools.find_single_match(data, 'var _SOURCE =.*?srt:(.*?),')
            sub = sub.replace('\\', '')
        else:
            sub = ''
        logger.debug('subtitle: %s'%sub)
        new_url='http://iplay.one/api/embed?id=%s&token=8908d9f846&%s'%(id, sub)

        data = httptools.downloadpage(new_url).data

        patron = 'file":"(.*?)","label":"(.*?)","type":".*?"}'
        matches = matches = re.compile(patron, re.DOTALL).findall(data)

        for scrapedurl, quality in matches:
            title = videoitem.contentTitle +' ('+quality+') ('+audio[videoitem.language]+')'
            url = scrapedurl.replace('\\','')
            itemlist.append(item.clone(title=title,
                                       action = 'play',
                                       url = url,
                                       subtitle = sub,
                                       server = 'directo',
                                       quality = quality,
                                       language = 'lang'
                                       ))

    if config.get_library_support() and len(itemlist) > 0 and item.extra != 'findvideos':
        itemlist.append(
            Item(channel=item.channel,
                 title='[COLOR yellow]Añadir esta pelicula a la biblioteca[/COLOR]',
                 url=item.url,
                 action="add_pelicula_to_library",
                 extra="findvideos",
                 contentTitle=item.contentTitle
                 ))
    return itemlist

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    #categoria='peliculas'
    try:
        if categoria == 'peliculas':
            item.url = host+'/estrenos/'
            item.extra = 'peliculas'
        elif categoria == 'infantiles':
            item.url = host+'http://pelisfox.tv/peliculas/animacion/'
            item.extra = 'peliculas'
        itemlist = todas(item)
        if itemlist[-1].title == 'Siguiente >>>':
                itemlist.pop()
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

