# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para backin.net
# by be4t5
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
version = config.get_setting("plugin_version_number")
HEADERS =  {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language':'es-es,es;q=0.8,en-us;q=0.5,en;q=0.3',
    'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept-Encoding':'gzip,deflate',
    'Keep-Alive':'300',
    'Connection':'keep-alive'}
def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.cnubis page_url="+page_url)
    video_urls = []
    media_url = []
    if "|" in page_url:
        page_url,url_ref = page_url.split("|")
        HEADERS["Referer"] = url_ref
    if version == '4203' or len(version) == 0:
        data = scrapertools.cachePage(page_url,headers=HEADERS)
    else:
        data = scrapertools.downloadpageGzip(page_url)
    logger.info(data)
    media_url.append(scrapertools.find_single_match(data,'<meta itemprop="contentURL" content="([^"]+)"'))
    if len(media_url)==0:
        media_url.append( scrapertools.find_single_match(data,'data-src-mp4-\w+="([^"]+)"'))
    if "mp4" in media_url[0]:
        media_url.append("mp4")
    if media_url[0].startswith("//"):
        media_url[0] = "http:" + media_url[0]
    logger.info("media_url="+media_url[0])

    # URL del vídeo
    video_urls.append( [ "."+ media_url[1] + " [cnubis]", media_url[0].replace("https","http") ] )

    for video_url in video_urls:
       logger.info("pelisalacarta.servers.cnubis %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # https://cnubis.com/plugins/mediaplayer/site/_1embed.php?u=9mk&w=640&h=320
    # http://cnubis.com/plugins/mediaplayer/site/_2embed.php?u=2aZD
    # http://cnubis.com/plugins/mediaplayer/embed/_2embed.php?u=U6w
    patronvideos  = 'cnubis.com/plugins/mediaplayer/(.*?/[^.]+.php\?u\=[A-Za-z0-9]+)'
    logger.info("pelisalacarta.servers.cnubis find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[cnubis]"
        url = "http://cnubis.com/plugins/mediaplayer/%s" % (match)
        if url not in encontrados and id != "":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'cnubis' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)        

    return devuelve

def test():

    video_urls = get_video_url("http://cnubis.com/plugins/mediaplayer/site/_embed1.php?u=9mk&w=640&h=320")
    return len(video_urls)>0
