####################################################################################################
# Autor:    Pradeep Kadambar <a href="mailto:pradeep.kadambar@rsa.com">Pradeep Kadambar</a>
# Date:     4/14/2013
# About:    This plugin allows contents from SonyLIV.com to be viewed over Plex clients.
#
# Version:  0.12
#
# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
####################################################################################################

import re

####################################################################################################
NAME = "Sony LIV"
ICON = "icon-default.png"
ART = "art-default.png"
ICON_PREFS = 'icon-prefs.png'

RE_TITLE = Regex('^(.+?)\s*\W*Ep')

LIVE_URL = "http://www.sonyliv.com/"

NOT_AVAILABLE = "- NA -"

EPISODE_LINK = "http://www.sonyliv.com/view-all/more-episodes/%s/page/%s"

XPATH_SHOWS = "//ul[@id='showname']/li/a"
XPATH_CLASSIC = "//div[@class='classic-slides']/div[@class='image-container']/a"

####################################################################################################

def Start():
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    
    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = 'InfoList'

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    MovieObject.thumb = R(ICON)
    MovieObject.art = R(ART)
    SeasonObject.thumb = R(ICON)
    SeasonObject.art = R(ART)
    NextPageObject.thumb = R(ICON)
    NextPageObject.art = R(ART)
    
@handler("/video/sonyliv", NAME, thumb=ICON, art=ART)
def MainMenu():
    Log("MainMenu - Enter")
    oc = ObjectContainer(view_group="InfoList")
    page = HTML.ElementFromURL(LIVE_URL)
    #Log(HTML.StringFromElement(page))

    oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
    oc.add(DirectoryObject(key = Callback(GetClassics), title = "Classics"))
        
    showCategories = page.xpath("//div/ul[@id='show-menu']/li/a/span/text()")
    for showCategory in showCategories:
        Log("Category name " + showCategory)
        oc.add(DirectoryObject(
            key = Callback(GetProgrammeForCategory, url = LIVE_URL, path = XPATH_SHOWS, categoryName = showCategory), 
            title = showCategory))
        
    Log("MainMenu - Exit")
    return oc

@route("/video/sonyliv/GetClassics")
def GetClassics():
    oc = ObjectContainer(title2 = "Classics")
    
    page = HTML.ElementFromURL(LIVE_URL + "/classics")
    
    showCategories = page.xpath("//div/ul[@id='show-menu']/li/a/span/text()")
    for showCategory in showCategories:
        Log("Category name " + showCategory)
        oc.add(DirectoryObject(
                        key = Callback(GetClassicProgrammeForCategory, url = LIVE_URL + "/classics", 
                        path = XPATH_CLASSIC, categoryName = showCategory), 
                        title = showCategory))    
    
    return oc

@route("/video/sonyliv/GetClassicProgrammeForCategory")
def GetClassicProgrammeForCategory(url, path, categoryName):
    oc = ObjectContainer(title2 = categoryName)  
    categoryId = categoryName.replace(' ', '-').lower()      
    page = HTML.ElementFromURL(url)        
    programmesList = page.xpath(path)
        
    for item in programmesList:
        #Log(HTML.StringFromElement(item))
        itemLink = item.xpath(".//@href")[0].lstrip().rstrip()
        Log("itemLink" + itemLink)
        #Log("check if %s is in %s", categoryId, itemLink)             
        if 'all' == categoryId or (categoryId in itemLink):        
            itemTitle = item.xpath(".//img/@alt")[0].lstrip().rstrip()
            Log("itemTitle = " + itemTitle)            
            itemThumb = item.xpath("//img/@src")[0]
            Log("itemThumb = " + itemThumb)
            oc.add(DirectoryObject(
                        key = Callback(GetProgramme, programmeName = itemTitle, programmeUrl = itemLink), 
                        title = itemTitle))    
    
    return oc    

@route("/video/sonyliv/GetProgrammeForCategory")
def GetProgrammeForCategory(url, path, categoryName):
    oc = ObjectContainer(title2 = categoryName)  
    categoryId = categoryName.replace(' ', '-').lower()       
    page = HTML.ElementFromURL(url)
    programmesList = page.xpath(path)
         
    for item in programmesList:
        #Log(HTML.StringFromElement(item))
        itemLink = item.xpath(".//@href")[0].lstrip().rstrip()
        #Log("check if %s is in %s", categoryId, itemLink)             
        if 'all' == categoryId or (categoryId in itemLink):
            itemTitle = item.xpath(".//text()")[0].lstrip().rstrip()
            Log("programmeName = " + itemTitle)            
            itemId = item.xpath("//ul[@id='showname']/li/a/@onmouseover")[0]
            Log("Programme id = " + itemId)  
            oc.add(DirectoryObject(
                        key = Callback(GetProgramme, programmeName = itemTitle, programmeUrl = itemLink), 
                        title = itemTitle))    
     
    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There aren't any items")
                      
    return oc

@route("/video/sonyliv/GetProgramme")
def GetProgramme(programmeName, programmeUrl):
    Log("GetProgramme - Enter")    
    page = HTML.ElementFromURL(programmeUrl)    

    fullProgrammeName = page.xpath("//div[@id='block-content-type-subscriptions-subscriptions']/div/h2[@class ='fl']/text()")[0].lstrip().rstrip()
    if fullProgrammeName != '':
        programmeName = fullProgrammeName
    oc = ObjectContainer(title2 = programmeName)

    try:    
        summary = page.xpath("//div[@id='block-sonyliv-video-description']/div/p/text()")[0].lstrip().rstrip()
    except:
        try:
            summary = page.xpath("//div[@id='block-sonyliv-video-description']/div/div/text()")[0].lstrip().rstrip()
        except:         
            summary = NOT_AVAILABLE
        
    try:
        genre = programmeUrl.split('/')[-2]
    except:
        genre = NOT_AVAILABLE    
    
    Log("Genre = " + genre)
    try:
        episodeCount = page.xpath("//div[id('block-content-type-subscriptions-subscriptions')]/div/div/span/span[@class='white-color text11']/text()")[0].split(' ')[0]
    except:
        episodeCount = '1'
        
    Log("episodeCount = " + episodeCount)
        
    # Get the episode id
    try:
        programmeID = page.xpath("//link[@rel='shortlink']/@href")[0].split('/')[-1]
    except:
        try:
            programmeID = page.xpath("//div[@id='block-sonyliv-more-episodes']/div/div/div/div[1]/span/a/@href")[0].split('/')[-1]
        except:
            return ObjectContainer(header = programmeName, message = "There are no titles available for the requested item.")
        
    Log("programmeID = " + programmeID)
    
    maxPageIndex, pageIndex, nextIndex, buttonText = getPageIndex(episodeCount)
    
    Log("maxPageIndex " + str(maxPageIndex))
    Log("pageIndex " + str(pageIndex))
    Log("nextIndex " + str(nextIndex))
      
    episodes = GetEpisodes(programmeName, summary, programmeID, pageIndex, maxPageIndex)
    Log("Loaded episodes " + str(len(episodes)))
    for episode in episodes:
        oc.add(episode)
        
    oc.add(NextPageObject(
            key = Callback(GetEpisodesWithContainer, programmeName = programmeName, summary = summary, programmeID = programmeID, 
                           pageIndex = nextIndex, maxPageIndex = maxPageIndex),
            title = buttonText
            ))        

    Log("GetProgramme - Exit")    
    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There aren't any items")
                      
    return oc

def getPageIndex(episodeCount):
    # Estimate pages
    maxPageIndex,mod = divmod(int(episodeCount), 12)        
   
    Log("Preference --- " + Prefs['ordering'])
    
    if Prefs['ordering'] == 'Oldest First':
        if mod != 0:
            pageIndex = maxPageIndex
        else:
            pageIndex = maxPageIndex - 1
        nextIndex = pageIndex - 1
        buttonText = "Newer ..."
        Log("Ordering --> Oldest index " + str(pageIndex))
    else:
        pageIndex = 0
        nextIndex = 1
        buttonText = "Older ..."
        Log("Ordering --> Newest index " + str(pageIndex))     
            
    Log("Max estimated pages " + str(maxPageIndex))
    return (maxPageIndex, pageIndex, nextIndex, buttonText)

@route("/video/sonyliv/GetEpisodesWithContainer")
def GetEpisodesWithContainer(programmeName, summary, programmeID, pageIndex, maxPageIndex):
    oc = ObjectContainer(title2 = programmeName)
    
    pageIndex = int(pageIndex)
    
    episodes = GetEpisodes(programmeName, summary, programmeID, pageIndex, maxPageIndex)
    for episode in episodes:
        oc.add(episode)

    if Prefs['ordering'] == 'Oldest First':
        if pageIndex > 0:
            pageIndex = pageIndex - 1
        buttonText = "Newer ..."        
        Log("Ordering --> Oldest  index " + str(pageIndex))
    else:
        if pageIndex < maxPageIndex:
            pageIndex += 1
        buttonText = "Older ..."            
        Log("Ordering --> newest  index " + str(pageIndex))   
                
    Log("Page index -->" + str(pageIndex))
    if(pageIndex < maxPageIndex):
        oc.add(NextPageObject(
            key = Callback(GetEpisodesWithContainer, programmeName = programmeName, summary = summary, programmeID = programmeID, 
                           pageIndex = pageIndex, maxPageIndex = maxPageIndex),
            title = buttonText
            ))
        
    if len(oc) < 1:
        return ObjectContainer(header="Empty", message="There aren't any items")
                      
    return oc

@route("/video/sonyliv/GetEpisodes")
def GetEpisodes(programmeName, summary, programmeID, pageIndex, maxPageIndex):    
    page =  HTML.ElementFromURL(EPISODE_LINK % (programmeID, pageIndex))
    
    # Get the episodes on first page
    episodesList = page.xpath("//div[@id='block-system-main']/div/div/ul/li")
        
    if Prefs['ordering'] == 'Oldest First':
        Log("reversing list --> Oldest  ")
        episodesList.reverse()
    
    #count = 0
    episodes = []
    
    for episode in episodesList:
        episodeThumb = episode.xpath(".//div[@class='img']/a/img/@src")[0].lstrip().rstrip()
        #Log("episodeThumb = " + episodeThumb)
        episodeLink = episode.xpath(".//div[@class='img']/a/@href")[0].lstrip().rstrip()
        Log("episodeLink = " + episodeLink)
        episodeTitle = episode.xpath(".//div[@class='img']/a/img/@alt")[0].lstrip().rstrip()
        Log("episodeTitle = " + episodeTitle)
        
        try:
            episodeTitle = RE_TITLE.findall(episodeTitle)[0]
            Log("episodeTitle after REGEX = " + episodeTitle)
        except: pass            

        Log("episodeTitle FINALK = " + episodeTitle)
        
        try:
            episodeDuration = episode.xpath(".//div[@class='icon-sets']/p/span[@class='date-color']/text()")[0].lstrip().rstrip()
            episodeDuration = Datetime.MillisecondsFromString(episodeDuration)
        except:
            episodeDuration = None
            
        #Log("episodeDuration = " + str(episodeDuration))
        episodeNumber = episode.xpath(".//div[@class='show-details fl']/span/text()")[0].replace('Ep #','').lstrip().rstrip()

        Log("episodeNumber = " + episodeNumber)
        
        try:
            episodeAirDate = episode.xpath(".//span[@class='date date-color']/text()")[0].lstrip().rstrip()
            episodeAirDate = Datetime.ParseDate(episodeAirDate).date()
        except:
            episodeAirDate = None
            
        Log("episodeAirDate = " + str(episodeAirDate))                   
        episodes.append(EpisodeObject(
                url = episodeLink,
                title = episodeTitle,
                summary = summary,
                duration = episodeDuration,
                originally_available_at = episodeAirDate,
                thumb = Resource.ContentsOfURLWithFallback(episodeThumb),
                season = 1,
                index = int(episodeNumber) if episodeNumber != '' else None,
                show = programmeName
                ))
        #count += 1
        
    return episodes
 
