import tkinter as tk
import os, random, sys
from os import path
import os.path
from os.path import abspath, dirname
import shutil
import json, httplib2
import urllib.request
import datetime
from PIL import Image, ImageTk
from decouple import config
import requests

ADTECH_ENDPOINT = "http://54.255.190.93/api/v1"

class SlideShowApp(object):
    def __init__(self):
        self.tk = tk.Tk()
        self.tk.attributes('-fullscreen', True)
        self.frame = tk.Frame(self.tk)
        self.canvas = tk.Canvas(self.tk, width=self.tk.winfo_screenwidth(), height=self.tk.winfo_screenheight())
        self.state = False
        self.tk.bind('<F11>', self.toggle_fullscreen)
        self.tk.bind('<Escape>', self.end_fullscreen)

        self.current_date = None
        self.base_dir = 'Images'        #Base directory for your images
        self.group_static = {
                            #  1: {
                            #      'category': 'daily_context', 'method': 'draw',
                            #      'slides': {
                            #                 1 : { 'name': 'TOD', 'path': 'TOD', 'callback': 'drawTOD'},
                            #                 2 : { 'name': 'Weather', 'path': 'Weather', 'callback': 'drawWeather'}
                            #                 }
                            #      },
                            #  2: {
                            #      'category': 'photo_context', 'method': 'image',
                            #      'slides': {
                            #                 1 : { 'name': 'Family', 'path': 'Family'}
                            #                 }
                            #      },
                            #  3: {
                            #      'category': 'reminders', 'method': 'image',
                            #      'slides': {
                            #                 1 : { 'name': 'Inspirational', 'path': 'Inspirational'},
                            #                 2 : { 'name': 'Health', 'path': 'Health'}
                            #                 }
                            #      },
                             2: {
                                 'category': 'advertisements', 'method': 'image',
                                 'slides': {
                                            1 : { 'name': 'cache', 'path': 'cache'}
                                            }
                                 }
                            }

        self.group_annual = {}      #placeholder for future slides
        self.group_scheduled = {}   #placeholder for futer slides

        # self.group_seasonal = {
                            #    1: {
                            #        'category': 'Holidays', 'method': 'image',
                            #        'slides': {
                            #                    1 : { 'name': 'Christmas', 'months': [12], 'path': 'Holidays/Christmas'},
                            #                    2 : { 'name': 'Easter', 'months': [4], 'path': 'Holidays/Easter'},
                            #                    3 : { 'name': 'Halloween', 'months': [10], 'path': 'Holidays/Halloween'},
                            #                    4 : { 'name': 'Independence', 'months': [7], 'path': 'Holidays/Independence'},
                            #                    5 : { 'name': 'Labor', 'months': [9], 'path': 'Holidays/Labor'},
                            #                    6 : { 'name': 'Memorial', 'months': [5], 'path': 'Holidays/Memorial'},
                            #                    8 : { 'name': 'Mothers', 'months': [5], 'path': 'Holidays/Mothers'},
                            #                    9 : { 'name': 'NewYear', 'months': [1], 'path': 'Holidays/NewYear'},
                            #                    10 : { 'name': 'Thanksgiving', 'months': [11], 'path': 'Holidays/Thanksgiving'},
                            #                    11 : { 'name': 'Valentines', 'months': [2], 'path': 'Holidays/Valentines'}
                            #                    }
                            #        },

                            #    2: {
                            #        'category': 'Seasons', 'method': 'image',
                            #        'slides': {
                            #                    1 : {'name': 'Fall', 'months': [9,10,11], 'path': 'Seasons/Fall'},
                            #                    2 : {'name': 'Winter', 'months': [12,1,2], 'path': 'Seasons/Winter'},
                            #                    3 : {'name': 'Spring', 'months': [3,4,5], 'path': 'Seasons/Spring'},
                            #                    4 : {'name': 'Summer', 'months': [6,7,8], 'path': 'Seasons/Summer'}
                            #                    }
                            #        }
                            #    }

        self.eligible_slides = self.group_static
        print(self.group_static)
        self.black_path = os.path.join(self.base_dir, 'Static', 'black1280.png')

        #Weather API
        self.weather_last_update = None
        self.weather_update_frequency = datetime.timedelta(seconds=3600)
        self.weather_cache = None
        self.weather_api_path = 'http://api.openweathermap.org/data/2.5/weather?zip=77034,us&units=imperial&APPID=bf21b5e020e1fcdbe8' #replace 77034 with your zip code
        self.weather_types = ['Thunderstorm', 'Drizzle', 'Rain', 'Snow']
        self.weather_cloud_types = {
               800 : 'Clear',
               801 : 'LightClouds',
               802 : 'LightClouds',
               803 : 'LightClouds',
               804 : 'OverCast'
               }

        #Advertisement API
        self.advertisement_last_update = None
        self.advertisement_update_frequency = datetime.timedelta(seconds=3600)
        self.advertisement_cache = None
        self.access_token = None
        self.connected = False              # flag for internet connection
        self.pre_registered = False         # validation flag  if .env file already has deviceid and deviceName
        self.pre_login = False              # validation flag  if .env file already has email and password
        self.device_registered = False      # flag for registered status
        self.login_failed = False           # flag for online login status - bad data, user doesn't exist, or passed the wrong password
        self.playlist_associated = False    # Device has playlist associated with it
        self.playlist_empty = False         # Device has playlist associated with it, but it's empty. 
        self.ad_index = 0
        self.timeout_counter = 0           # Counter for initial wifi connect 
        self.login()
        # self.test_register()
        self.register_device()
        self.dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_dir = self.dir + '/Images/cache/'
        ## Clear cache folder on startup
        if os.path.exists(self.cache_dir):
            for file in os.listdir(self.dir +'/Images/cache'):
                os.remove(self.cache_dir+file)
        else:
            os.makedirs(self.cache_dir)


    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.tk.attributes('-fullscreen', self.state)


    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes('-fullscreen', False)
        return 'break'


    def callback(self):
        get_image()


    def login(self):
        try:
            response = requests.post(ADTECH_ENDPOINT + '/auth/login', data={'email': config('email', cast=str), 'password': config('password', cast=str)})
            print("Login response: ", response.text)
            if response.status_code == 200:     # Success
                self.access_token = response.json().get('token')
                self.login_failed = False

            elif response.status_code == 404:   # User not found
                print(response.text)
                if os.path.exists('.env'):
                    os.remove('.env')
                    print('.env file deleted')
                print("Login error - User not found")
                self.login_failed = True

            elif response.status_code == 422:   # Invalid password
                print(response.text)
                if os.path.exists('.env'):
                    os.remove('.env')
                    print('.env file deleted')
                print("Login error - Invalid password")
                self.login_failed = True

            elif response.status_code == 400:   # Bad Data
                print(response.text)
                print("Login error - Bad data") 
                if os.path.exists('.env'):
                    os.remove('.env')
                    print('.env file deleted')
                self.login_failed = True

            self.connected = True 

        except Exception as e:
            print(e)
            print("Login failed. check Internet?")
            self.connected = False


    def register_device(self):
        if config('deviceUid', default=None) and config('deviceName', default=None):   # Check if .env file has deviceId and deviceName
            self.pre_registered = True 
            print("Pre-registered!")
        else:
            if os.path.exists('.env'):
                os.remove('.env')
                print('.env file deleted')
            self.pre_registered = False

        if config('email', default=None) and config('password', default=None):   # Check if .env file has deviceId and deviceName
            self.pre_login = True 
        else:
            if os.path.exists('.env'):
                os.remove('.env')
                print('.env file deleted')

            self.pre_login = False

        try:
            response = requests.post(
                ADTECH_ENDPOINT + '/devices', 
                data={'deviceUid': config('deviceUid', cast=str), 
                    'deviceName': config('deviceName', cast=str)
                }, 
                headers = {'Authorization':self.access_token}
            )
            print("Register response: ", response.status_code, response.text)

            if response.status_code == 201:     # Register successful!
                print("Registered Successfully!")
                self.device_registered = True

            elif response.status_code == 302:   # Device already exists
                print("Device already registered!")
                self.device_registered = True

                #TODO: Check if device belongs to the user. Add invalid user validation
            elif response.status_code == 422:   # Bad Data
                print("Register - Bad data")
                if os.path.exists('.env'):
                    os.remove('.env')
                    print('.env file deleted')
                self.device_registered = False

            self.connected = True
        
        except Exception as e:
            print(e)
            print("Register Device Error: Register failed. Check Internet?")
            self.device_registered = False
            self.connected = False


    def json_request(self, method='GET', path=None, body=None):
        connection = httplib2.Http()
        response, content = connection.request(
                                               uri = path,
                                               method = method,
                                               headers = {'Content-Type': 'application/json; charset=UTF-8'},
                                               body = body,
                                               )
        return json.loads(content.decode())


    def fetch_weather(self):    # Unused
        result = self.json_request(path=self.weather_api_path)

        #get temperature from "main" set
        if 'main' in result:
            temperature = int(result['main']['temp'])

        #parse weather conditions
        weather_conditions = []
        weather_context = None
        weather_context_images = []

        if 'weather' in result:
            weather_list = result['weather']
            for condition in weather_list:
                weather_conditions.append(condition['description'].title())
                if condition['main'] in self.weather_types:
                    weather_context_images.append(condition['main'])
                elif condition['id'] in self.weather_cloud_types:
                    weather_context_images.append(self.weather_cloud_types.get(condition['id'], None))

            weather_context = ', '.join(weather_conditions)

            self.weather_last_update = datetime.datetime.now()
            self.weather_cache = {
                                  'temperature': temperature,
                                  'description': weather_context,
                                  'background': weather_context_images[0]
                                  }
            print('updating weather cache at', self.weather_last_update)
            print(self.weather_cache)


    def fetch_advertisement(self):
        print("Fetching Ads")
        try:
            result = requests.get(
                ADTECH_ENDPOINT + "/devices/" + config('deviceUid', default=None, cast=str) + "/carousel", 
                headers = {'Authorization':self.access_token}
            )
            print("Fetch ads Response: ", result.status_code, result.json())
            #TODO: Catch empty playlists and unassociated devices properly
            if result.status_code == 200:
                print("Parsing..")
                try:
                    # Old parsing
                    # for advertisement in result.json():
                    #     # urllib.request.urlretrieve(advertisement.get('url'),  self.cache_dir + advertisement.get('title'))
                    # New parsing
                    for advertisement in result.json().get('adverturls'):
                        title = str(advertisement)[50:]
                        urllib.request.urlretrieve(advertisement,  self.cache_dir + title)

                except Exception as e:
                    # print(e)
                    # print("Empty list.")
                    print("pass1")
                    pass

                self.playlist_associated = True

            elif result.status_code == 404:
                print("No playlist associated with this device yet.")
                self.playlist_associated = False

            self.connected = True
        
        except Exception as e:
            print("Fetch advertisement Error")
            print(e)
            self.connected = False

    def update_advertisement(self):     # Update advertisement by reflecting/removing deleted ads in Images/cache
        print("Updating advertisements")
        try:
            ad_list = []
            result = requests.get(
                ADTECH_ENDPOINT + "/devices/" + config('deviceUid', default=None, cast=str) + "/carousel", 
                headers = {'Authorization':self.access_token}
            )
            print("Updating ads response:", result.status_code, result.text)

            if result.status_code == 200:
                print("A playlist is associated with this device.")
                
                print("Checking playlist...")
                try:
                    # Old parsing
                    # for ad in result.json():
                    #     if ad not in ad_list:
                    #         ad_list.append(ad.get('title', None))
                    # New parsing
                    for ad in result.json().get('adverturls'):
                        if ad not in ad_list:
                            title = str(ad)[50:]
                            ad_list.append(title)
                except Exception as e:
                    print(e)
                    print("Playlist did not change. Nothing to delete")

                print("Ad list: ", ad_list)
                cache_files = os.listdir(self.cache_dir)

                for file in cache_files:
                    if file not in ad_list:
                        print(file)
                        os.remove(self.cache_dir+file)
                self.playlist_associated = True

                if ad_list:     # Check if ad_list is empty
                    print("Playlist has", len(ad_list), "ads.")
                    self.playlist_empty = False
                else:
                    print("Playlist is empty.")
                    self.playlist_empty = True

            elif result.status_code == 404:
                print("No playlist associated with this device yet.")
                self.playlist_associated = False

            self.connected = True

        except Exception as e:
            print("Update Advertisement Error")
            print(e)
            self.connected = False


    def update_eligible_slides(self):
        #reset eligible to default
        self.eligible_slides = self.group_static
        #filter seasonal and daily slides
        # counter = 1
        # for k,v in self.group_seasonal.items():
        #     for x,y in v['slides'].items():
        #         if self.current_date.month in y['months']:
        #             self.eligible_slides[4]['slides'][counter] = y
        #             counter += 1


    def prepare_slide(self):
        #pick a group
        group = random.choice(list(self.eligible_slides))
        #TODO check for slide group method
        slide = random.choice(list(self.eligible_slides[group]['slides']))
        slide_full = self.eligible_slides[group]['slides'][slide]
        path = self.cache_dir

        if self.eligible_slides[group]['method'] == 'draw':
            callback = slide_full['callback']
            getattr(self, callback)()
        elif self.eligible_slides[group]['method'] == 'image':
            # Device has not logged in, has not registered and has no WiFi (First time - One time Setup (no .env file))
            if not self.connected and not self.access_token and not self.device_registered and not self.pre_registered:     
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'setup_instructions.png')
                self.get_image(full_path)

            #TODO: Display Wifi network and status
            # Device is probably registered but there's no internet from the start. (2nd Time onwards)
            elif not self.connected and not self.access_token and not self.device_registered and self.pre_registered:       
                if self.timeout_counter < 10: # Initially wait..
                    self.timeout_counter += 1
                    path = self.dir + '/Images/Static/'
                    full_path = os.path.join(path, 'no_internet_from_start.png')       
                    self.get_image(full_path)
            
                else: # Timeout (Give up.. the wifi creds are probably wrong anyway.)
                    path = self.dir + '/Images/Static/'
                    full_path = os.path.join(path, 'no_internet.png')
                    self.get_image(full_path)

            # Login failed but has internet (Wrong login credentials)
            elif self.connected and not self.access_token and self.pre_login and self.login_failed:              
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'resetup_login_failed.png')
                self.get_image(full_path)

            # Device is not registered but has internet (Login success, but failed to register)
            elif self.connected and not self.access_token and self.pre_registered and not self.device_registered:          
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'resetup_register_failed.png')
                self.get_image(full_path)

            # No playlist associated with this device
            elif self.connected and not self.playlist_associated:      
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'no_playlist.png')
                self.get_image(full_path)   

            # Playlist is associated with the device but it's empty         
            elif self.playlist_associated and self.playlist_empty and self.connected:       
                path = self.dir + '/    Images/Static/'
                full_path = os.path.join(path, 'empty_playlist.png')
                self.get_image(full_path)

            # Device is registered but has no Internet (Functional but then suddenly disconnected)
            elif self.access_token and self.device_registered and not self.connected:          
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'no_internet.png')
                # full_path = os.path.join(path, 'black1280.png')
                self.get_image(full_path)    

            # Device is registered and has both wifi and playlist with ads (Normal operation)
            elif len(os.listdir(path)):                                 
                ## Selecting images/ads randomly
                image = random.choice(os.listdir(path))
                print("Image :", image)
                full_path = os.path.join(path, image)
                self.get_image(full_path)
        
                ## (Iterate) Selecting over adlist sequentially
                # ad_list = os.listdir(path)
                # image = ad_list[self.ad_index]
                # print("Index : ", self.ad_index, "Image :", image)
                # if self.ad_index < len(ad_list)-1:
                #     self.ad_index += 1
                # else:
                #     self.ad_index = 0
                # full_path = os.path.join(path, image)
                # self.get_image(full_path)

            else:   # All else
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'black1280.png')
                self.get_image(full_path)


    def draw_rectangle(self):
        pass


    def slideshow(self):
        now = datetime.date.today()
        #now = datetime.date(2015, 7, 11)        #use for testing different date ranges
        if not self.current_date or now != self.current_date:
            self.current_date = now
            self.update_eligible_slides()

        if not self.weather_last_update or (datetime.datetime.now() - self.weather_last_update > self.weather_update_frequency):
            print("Registered: ", self.device_registered, ", Connected: ", self.connected)
            if not self.access_token:   # Self-restoring
                self.login()
                self.register_device()

            self.fetch_advertisement()
            self.update_advertisement()

        self.prepare_slide()
        self.tk.after(5000, self.slideshow) 


    def get_image(self, path):
        #global tkpi
        image = Image.open(path)
        image = image.resize((self.tk.winfo_screenwidth(), self.tk.winfo_screenheight()))
        self.tk.geometry('%dx%d' % (image.size[0], image.size[1]))
        self.tkpi = ImageTk.PhotoImage(image)

        label = tk.Label(self.tk, image=self.tkpi)
        label.place(x=0,y=0,width=image.size[0], height=image.size[1])


    def drawTOD(self):
        #set bg image to black static
        self.get_image(self.black_path)

        #contextual date / time
        now = datetime.datetime.now()
        hour_check = int(now.strftime('%H'))
        if hour_check > 4 and hour_check < 11:
            context_time = 'Morning'
        elif hour_check >= 11 and hour_check < 14:
            context_time = 'Mid Day'
        elif hour_check >= 14 and hour_check < 17:
            context_time = 'Afternoon'
        elif hour_check >= 17 and hour_check < 19:
            context_time = 'Evening'
        else:
            context_time = 'Night'

        context_tod = '{} {}'.format(now.strftime('%A'), context_time)
        full_tod = '{}\n{}'.format(now.strftime('%I:%M %p'), now.strftime('%B %d, %Y'))

        label = tk.Label(self.tk, text=context_tod, width=0, height=0, fg="#ffffff", bg="#000000", font=("Rouge", 95))
        label.place(relx=0.5, rely=0.3, anchor="center")
        label = tk.Label(self.tk, text=full_tod, width=0, height=0, fg="#ffffff", bg="#000000", font=("Rouge", 78))
        label.place(relx=0.5, rely=0.7, anchor="center")


    def drawWeather(self):  # Unused
        if self.weather_cache:
            #Set background image if available
            if 'background' in self.weather_cache:
                image_dir = os.path.join(self.base_dir, 'Weather', self.weather_cache['background'])
                image = random.choice(os.listdir(image_dir))
                full_path = os.path.join(image_dir, image)
                self.get_image(full_path)
            #else use black bg
            else:
                self.get_image(self.black_path)

            #draw the temp and weather description
            temperature = '{}{}'.format(self.weather_cache['temperature'], u'\N{DEGREE SIGN}')
            description = self.weather_cache['description']
            if temperature and description:
                label = tk.Label(self.tk, text=description, width=0, height=0, fg="#000", bg="#e6e6e6", font=("Rouge", 55))
                label.place(relx=0.5, rely=0.4, anchor="center")
                label = tk.Label(self.tk, text=temperature, width=0, height=0, fg="#000", bg="#e6e6e6", font=("Rouge", 45))
                label.place(relx=0.5, rely=0.6, anchor="center")
        else:
            pass

if __name__ == '__main__':
    w = SlideShowApp()
    w.slideshow()
    w.tk.mainloop()
