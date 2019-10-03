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
        self.device_registered = False      # flag for registered status
        self.ad_index = 0
        self.login()
        self.test_register()
        # self.register_device()
        self.advertisement_api_path = 'http://54.255.190.93/api/v1/advertisements/device/' + config('deviceId', default=None, cast=str)  #replace 77034 with your zip code
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
            response = requests.post('http://54.255.190.93/api/v1/auth/login', data={'email': config('email', cast=str), 'password': config('password', cast=str)})
            if response.status_code == 200:     # Success
                self.access_token = response.json().get('token')
            elif response.status_code == 404:   # User not found
                print(response.text)
                print("Login error - Must erase env file")
            elif response.status_code == 422:   # Invalid password
                print(response.text)
                print("Login error - Must erase env file")
            elif response.status_code == 400:   # Bad Data
                print(response.text)
                print("Login error - Bad data") 

            self.connected = True 

        except Exception as e:
            print(e)
            print("Login failed. check Internet?")
            self.connected = False


    def register_device(self):
        if config('deviceId', default=None) and config('deviceName', default=None):   # Check if .env file has deviceId and deviceName
            self.pre_registered = True 
            print("Preregistered!")
        else:
            self.pre_registered = False

        try:
            response = requests.post('http://RegisterDeviceEndpoint', data={'deviceId': config('deviceId', cast=str), 'deviceName': config('deviceName', cast=str)})
            if response.status_code == 200:     # Register successful!
                print("Registered Successfully!")
                self.device_registered = True
            elif response.status_code == 302:   # Device already exits
                print("Device already registered!")
                self.device_registered = True
            elif response.status_code == 422:   # Bad Data
                print("Register - Bad data")
                self.device_registered = False
                # Erase something from .env file?
            
            self.connected = True
        
        except Exception as e:
            print(e)
            print("Register failed. check Internet?")
            self.connected = False


    def test_register(self): # Deprecated
        if config('deviceId', default=None) and config('deviceName', default=None):   # Check if .env file has deviceId and deviceName
            self.pre_registered = True 
            print("Preregistered!")
        else:
            self.pre_registered = False

        try:
            response = requests.get('http://54.255.190.93/api/v1/devices', headers = {'Authorization':self.access_token})
            # print(response.text)
            #TODO: Or simply catch request.status==### if device is already registered before setting self.device_registered flag to True
            device_list = response.json().get("devices")
            print(device_list)
            device_id = config('deviceId', cast=str, default=None)
            for device in device_list:      # Check if the deviceId is already registered/existing in the database
                if device_id in device.values():       
                    print(device)
                    print("Device already registered.")
                    self.device_registered = True
        except Exception as e:
            print(e)
            print("No internet")

        if not self.device_registered:
            print("Registering device..")
            #TODO: Register and Try Catch exeptions before setting self.device_registered flag to True.
            # if Register_response.status == 200:
            #   self.device_registered = True
            # else:
            #TODO: Catch wrong credentials (ex: wrong email and password) and other scenarios before setting self.device_registered flag to Flase
            #   self.device_registered = False


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
        print("Fetching Ad")
        try:
            result = requests.get(self.advertisement_api_path, headers = {'Authorization':self.access_token})
            print(result.json())
            for advertisement in result.json():
                urllib.request.urlretrieve(advertisement.get('url'),  self.cache_dir + advertisement.get('title'))
        
            self.connected = True
        except Exception as e:
            print("Fetch advertisement Error")
            print(e)
            self.connected = False

    def update_advertisement(self):     # Update advertisement by reflecting/removing deleted ads in Images/cache
        try:
            ad_list = []
            result = requests.get(self.advertisement_api_path, headers = {'Authorization':self.access_token})
            for ad in result.json():
                if ad not in ad_list:
                    ad_list.append(ad.get('title'))
            # print("Ad list: ", ad_list)
            cache_files = os.listdir(self.cache_dir)

            for file in cache_files:
                if file not in ad_list:
                    print(file)
                    os.remove(self.cache_dir+file)

            self.connected = True

        except Exception as e:
            print("Fetch advertisement Error")
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

            if not self.access_token and not self.device_registered and not self.connected and not self.pre_registered:     # Device is not registered and has no WiFi (First time - One time Setup)
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'setup_instructions.png')
                self.get_image(full_path)

            elif not self.access_token and not self.device_registered and not self.connected and self.pre_registered:       # Device is proabably registered but there's no internet from the start.
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'no_internet.png')       
                self.get_image(full_path)            

            elif not self.access_token and self.connected:              # Login failed but has internet (Wrong login credentials)
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'invalid_login.png')
                self.get_image(full_path)

            elif not self.device_registered and self.connected:          # Device is not registered but has internet (Login success, but failed to register)
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'not_registered.png')
                self.get_image(full_path)

            elif self.device_registered and not self.connected:          # Device is registered but has no Internet (Functional but then suddenly disconnected)
                path = self.dir + '/Images/Static/'
                full_path = os.path.join(path, 'no_internet.png')
                # full_path = os.path.join(path, 'black1280.png')
                self.get_image(full_path)    
 
            elif len(os.listdir(path)):                                 # Device is registered and has wifi (Normal operation)
                ## Selecting images/ads randomly
                # image = random.choice(os.listdir(path))
                # print("Image :", image)
                # full_path = os.path.join(path, image)
                # self.get_image(full_path)
        
                ## (Iterate) Selecting over adlist sequentially
                ad_list = os.listdir(path)
                image = ad_list[self.ad_index]
                print("Index : ", self.ad_index, "Image :", image)
                if self.ad_index < len(ad_list)-1:
                    self.ad_index += 1
                else:
                    self.ad_index = 0
                full_path = os.path.join(path, image)
                self.get_image(full_path)
            else:
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
            if self.device_registered:
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
