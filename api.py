import requests
from decouple import config

ADTECH_ENDPOINT = "http://54.255.190.93/api/v1"
access_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVkNDdmNmJmODdjZTcyMjcyYTlhNDQyYyIsImlhdCI6MTU3MTM4MDkzNTAxMH0.yP6DAws3FE-uil-60GJEtg53yfdp0592_vAbCMHqPW0"

##### DEVICE REGISTRATION ######
def get_all_devices():
    response = requests.get(
        ADTECH_ENDPOINT + "/devices",
        headers = {'Authorization': access_token}
    )
    print(response.status_code)
    print(response.text)

def get_specific_device(device_id):
    response = requests.get(
        ADTECH_ENDPOINT + "/devices/" + str(device_id),
        headers = {'Authorization': access_token}
    )
    print(response.status_code)
    print(response.text)

##### ADVERTISEMENTS #####
def get_all_ads():
    response = requests.get(
        ADTECH_ENDPOINT + "/advertisements" , 
        headers = {'Authorization': access_token}
    )
    print("Retrieving all ads: ")
    print(response.status_code)
    print(response.text)


def get_specific_ad(ad_id):
    response = requests.get(
        ADTECH_ENDPOINT + "/advertisements/" + ad_id, 
        headers = {'Authorization': access_token}
    )
    print("Retrieving specific ad: ")    
    print(response.status_code)
    print(response.text)


##### PLAYLISTS #####
def get_all_playlists():
    response = requests.get(
        ADTECH_ENDPOINT + "/playlists" , 
        headers = {'Authorization': access_token}
    )
    print("Retrieving all playlists: ")    
    print(response.status_code)
    print(response.text)


def get_specific_playlist(playlist_id):
    response = requests.get(
        ADTECH_ENDPOINT + "/playlists/" + playlist_id, 
        headers = {'Authorization': access_token}
    )
    print("Retrieving specific ads: ")    
    print(response.status_code)
    print(response.text)


def add_playlist(name):
    response = requests.post(
        ADTECH_ENDPOINT + "/playlists",
        data={'name': name},
        headers = {'Authorization': access_token}
    )
    print("Adding playlist: ")
    print(response.status_code)
    print(response.text)


def add_playlist_to_device(playlist_id):
    response = requests.put(
        ADTECH_ENDPOINT + "/devices/" + config('deviceUid', default=None, cast=str) + "/add_playlist", 
        data = {'id' : playlist_id},
        headers = {'Authorization': access_token}
    )
    print("Linking playlist to device: ")
    print(response.status_code)
    print(response.text)


def remove_playlist_from_device(playlist_id):
    response = requests.put(
        ADTECH_ENDPOINT + "/devices/" + config('deviceUid', default=None, cast=str) + "/remove_playlist", 
        data = {'id' : playlist_id},
        headers = {'Authorization': access_token}
    )
    print("Linking playlist to device: ")
    print(response.status_code)
    print(response.text)


def assign_playlist(playlist_id):
    response = requests.put(
        ADTECH_ENDPOINT + "/devices/" + config('deviceUid', default=None, cast=str) + "/assign_playlist", 
        data = {'id' : playlist_id},
        headers = {'Authorization': access_token}
    )
    print("Linking playlist to device: ")
    print(response.status_code)
    print(response.text)


def fetch_ads():
    response = requests.get(
        ADTECH_ENDPOINT + "/devices/" + config('deviceUid', default=None, cast=str) + "/carousel", 
        headers = {'Authorization': access_token}
    )
    print("Fetching ads for device: ")    
    print(response.status_code)
    print(response.text)    

    advertisements = response.json().get("advertisements")
    ad_urls = advertisements.get("advertUrls")
    ad_list = advertisements.get("advertNames")
    ad_timers = advertisements.get("advertTimers")

    print("ad list: ", ad_list)
    # print("advertisements urls: ", advertisements.get("advertUrls"))

    for ad in range(len(ad_list)):
        url = ad_urls[ad]
        title = ad_list[ad]
        # title = url[50:]  # If you want file extensions included                
        ad_timer = ad_timers[ad]
        print(ad, url, title, ad_timer)

#==================================================
# get_all_devices()
# get_specific_device('pneumonoultramicro')

# get_all_ads()
# get_specific_ad("5d974f434dad7a40cc046a89")

# get_all_playlists()
# get_specific_playlist("5d9ab7d74dad7a40cc046a8d")
# add_playlist("Foods")

# assign_playlist("5d9ab7294dad7a40cc046a8c")
fetch_ads()


# link

# fetch_ads()


# testString = "https://adtech-s3.s3.amazonaws.com/advertisements/gn-gift_guide_variable_c.jpg"
# testString = 345678
# title = testString[50:]
# print(title)