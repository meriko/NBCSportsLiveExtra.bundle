ExtractVideoInfo = SharedCodeService.nbcsle.ExtractVideoInfo

PREFIX = '/video/nbcsportsliveextra'

TITLE = 'NBC Sports Live Extra'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = String.Decode('aHR0cDovL3N0cmVhbS5uYmNzcG9ydHMuY29tL2RhdGEvbW9iaWxlLw__')
CONFIG_URL = BASE_URL + 'configuration-2014-RSN-Sections.json'
LIVE_URL = BASE_URL + 'mcms/prod/nbc-live.json'
FEATURED_URL = BASE_URL + 'mcms/prod/nbc-featured.json'
UPCOMING_URL = BASE_URL + 'mcms/prod/nbc-upcoming.json'

ITEMS_PER_PAGE = 25

##########################################################################################
def Start():

    # Setup the default attributes for the ObjectContainer
    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    # Setup the default attributes for the other objects
    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.3.18 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.18'

##########################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()

    title = 'Live'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Videos,
                    title = title,
                    items_url = LIVE_URL,
                    cacheTime = 0
                ),
            title = title
        )
    )
    
    title = 'Upcoming'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Videos,
                    title = title,
                    items_url = UPCOMING_URL
                ),
            title = title
        )
    )
    
    title = 'Featured'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Featured,
                    title = title,
                    items_url = FEATURED_URL
                ),
            title = title
        )
    )
    
    oc_sports = Sports('Sports')
    for object in oc_sports.objects:
        oc.add(object)
 
    return oc

##########################################################################################
@route(PREFIX + '/Featured')
def Featured(title, items_url):

    oc = ObjectContainer(title2 = title)
    
    title = 'Spotlight'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Videos,
                    title = title,
                    items_url = items_url,
                    choice = 'spotlight'
                ),
            title = title
        )
    )
    
    title = 'Showcase'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Videos,
                    title = title,
                    items_url = items_url,
                    choice = 'showCase'
                ),
            title = title
        )
    )
    
    title = 'Replays'
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Videos,
                    title = title,
                    items_url = items_url,
                    choice = 'replay'
                ),
            title = title
        )
    )
    
    return oc

##########################################################################################
@route(PREFIX + '/Sports')
def Sports(title):

    oc = ObjectContainer(title2 = title)
    
    data = JSON.ObjectFromURL(CONFIG_URL)
    
    for sport in data['sports']:
        if sport['name'].startswith('CSN'):
            continue
        
        if not 'code' in sport:
            continue
            
        if not sport['code']:
            continue
        
        try:
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Featured,
                            title = sport['name'],
                            items_url = BASE_URL + 'mcms/prod/%s.json' % str(sport['code'])
                        ),
                    title = sport['name']
                )
            )
        except:
            pass
            
    return oc

##########################################################################################
@route(PREFIX + '/Videos', cacheTime = int, offset = int)
def Videos(title, items_url, choice = None, cacheTime = None, offset = 0):

    oc = ObjectContainer(title2 = title, no_cache = (cacheTime != None))

    data = JSON.ObjectFromURL(url = items_url, cacheTime = cacheTime)
    
    if choice:
        data = data[choice]
    
    for item in data[offset:]:
        
        info = ExtractVideoInfo(item, items_url, choice)
        
        if not info:
            continue
        
        oc.add(
            VideoClipObject(
                url = info['url'],
                title = info['title'],
                summary = info['summary'],
                duration = info['duration'],
                thumb = info['thumb'],
                originally_available_at = info['originally_available_at']
            )
        )
            
        offset = offset + 1
        
        if offset % ITEMS_PER_PAGE == 0 and (len(data) - offset > 0):
            oc.add(
                NextPageObject(
                    key =
                        Callback(
                            Videos,
                            title = title,
                            items_url = items_url,
                            choice = choice,
                            offset = offset
                        )
                )
            )
            
            return oc

    if len(oc) < 1:
        oc.header = "Sorry"
        oc.message = "There aren't any videos currently available" 

    return oc
