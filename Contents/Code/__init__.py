PREFIX = '/video/nbcsportsliveextra'

TITLE = 'NBC Sports Live Extra'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = String.Decode('aHR0cDovL3N0cmVhbS5uYmNzcG9ydHMuY29tL2RhdGEvbW9iaWxlLw__')
CONFIG_URL = BASE_URL + 'configuration-2014-RSN-Sections.json'
LIVE_URL = BASE_URL + 'mcms/prod/nbc-live.json'
FEATURED_URL = BASE_URL + 'mcms/prod/nbc-featured.json'
UPCOMING_URL = BASE_URL + 'mcms/prod/nbc-upcoming.json'

IMAGE_BASE_URL = 'https://hdliveextra-a.akamaihd.net/HD/image_sports/mobile/'
IMAGE_BASE_ALT_URL = 'http://hdliveextra-pmd.edgesuite.net/HD/image_sports/mobile/'

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
    HTTP.User_Agent = 'NBCSports/742 CFNetwork/672.0.8 Darwin/14.0.0'

###################################################################################################
def ValidatePrefs():

    if Prefs['resolution'] != 'Auto':
        return ObjectContainer(
            header = "Note!",
            message = "Only change to a specific resolution if you are experiencing problems"
        )

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

    oc.add(
        PrefsObject(
            title = 'Preferences',
            summary = 'Manage preferences'
        )
    )
 
    return oc
    
##########################################################################################
@route(PREFIX + '/Videos', cacheTime = int, offset = int)
def Videos(title, items_url, choice = None, cacheTime = None, offset = 0):

    oc = ObjectContainer(title2 = title, no_cache = (cacheTime != None))   
    data = JSON.ObjectFromURL(url = items_url, cacheTime = cacheTime)
    
    if choice:
        data = data[choice]
    
    for item in data[offset:]:
        
        if item['free'] == 0:
            continue
        
        if 'iosStreamUrl' in item:
            url = item['iosStreamUrl']
        elif 'androidStreamUrl' in item:
            url = item['androidStreamUrl']
        else:
            continue
        
        try:
            duration = int(round(float(item['length']) * 1000))
        except:
            duration = None
            
        thumb_id = item['image']
        
        try:
            date = item['start'].split('-')[0]
        except:
            date = None
        
        oc.add(
            CreateVideoClipObject(
                url = url,
                title = item['title'],
                summary = item['info'],
                duration = duration,
                thumb_id = thumb_id,
                date = date
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
@route(PREFIX + '/createvideoclipobject', duration = int, include_container = bool)
def CreateVideoClipObject(url, title, summary, duration, thumb_id, date, include_container = False):

    try:
        originally_available_at = Datetime.ParseDate(date).date()
    except:
        originally_available_at = None
    
    if Prefs['resolution'] == 'Auto' or Prefs['resolution'] == '1080':
        video_resolution = 1080
    else:
        video_resolution = int(Prefs['resolution'])
        
    if include_container:
        url = GetClientDependentURL(url, video_resolution)
    
    vco = VideoClipObject(
        key =
            Callback(
                CreateVideoClipObject,
                url = url,
                title = title,
                summary = summary,
                duration = duration,
                thumb_id = thumb_id,
                date = date,
                include_container = True
            ),
        rating_key = url,
        title = title,
        thumb = Callback(GetIMG, thumb_id = thumb_id),
        summary = summary,
        duration = duration,
        originally_available_at = originally_available_at,
        items = [
            MediaObject(
                parts = [
                    PartObject(
                        key = HTTPLiveStreamURL(url = url)
                    )
                ],
                video_resolution = video_resolution,
                audio_channels = 2
            )
        ]
    )
    
    if include_container:
        return ObjectContainer(objects = [vco])
    else:
        return vco
        
##########################################################################################
@route(PREFIX + '/GetClientDependentURL', video_resolution = int)
def GetClientDependentURL(url, video_resolution):

    if Client.Platform in ['Android', 'iOS', 'Roku', 'Safari'] and Prefs['resolution'] == 'Auto':
        # These clients can handle HLS correctly(adaptive streaming)
        hls_url = url
    else:
        try:
            streams = GetHLSStreams(url)
            
            hls_url = None
            if Prefs['resolution'] == 'Auto':
                # Return highest bitrate url. 
                hls_url = streams[0]['url']
            else:
                min_diff_found = 10000000 # Some huge number to get it started
                for stream in streams:
                    if 'resolution' in stream:
                        diff = abs(stream['resolution'] - video_resolution)
                        
                        if diff < min_diff_found:
                            hls_url = stream['url']
                            min_diff_found = diff
                    
                if not hls_url:
                    hls_url = streams[0]['url']
            
            if not '?' in hls_url:
                # Samsung requires an arbitrary parameter in the stream url since
                # '&' is always appended by that client ...
                hls_url = hls_url + '?null='
        except:
            hls_url = url
    
    Log(hls_url)    
    return hls_url

##########################################################################################
def GetHLSStreams(url):
    streams = []

    playList = HTTP.Request(url).content

    # Parse the m3u8 file to get:
    # - URL
    # - Resolution
    # - Bitrate
    for line in playList.splitlines():
        if "BANDWIDTH" in line:
            stream            = {}
            stream["bitrate"] = int(Regex('(?<=BANDWIDTH=)[0-9]+').search(line).group(0))        

            if "RESOLUTION" in line:
                stream["resolution"] = int(Regex('(?<=RESOLUTION=)[0-9]+x[0-9]+').search(line).group(0).split("x")[1])

        elif "m3u8" in line:
            path = ''
            
            if not line.startswith("http"):
                path = url[ : url.rfind('/') + 1]
            
            try:
                stream["url"] = path + line    
                streams.append(stream)
            except:
                pass
                
    sorted_streams = sorted(streams, key = lambda stream: stream["bitrate"], reverse = True)        

    return sorted_streams

##########################################################################################
@route(PREFIX + '/GetIMG')
def GetIMG(thumb_id):
    try:
        return HTTP.Request(IMAGE_BASE_URL + thumb_id + '_m50.jpg', cacheTime = CACHE_1MONTH).content
    except:
        try:
            return HTTP.Request(IMAGE_BASE_ALT_URL + thumb_id + '_m50.jpg', cacheTime = CACHE_1MONTH).content 
        except:
            return R(ICON)
