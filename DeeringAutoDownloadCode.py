##############################
#
#   Jack Carroll
#   27 May 2020
#   Deering, AK Imagery Download Code
#
##############################
import os
import json
import time
import pathlib
import requests
from datetime import datetime
from dotenv import load_dotenv

import os
import json
import time
import pathlib
import requests
from datetime import datetime
from dotenv import load_dotenv

   

# Retrieve API keys from local .env file
# TODO: Change env_path, JACK_KEY and FRANK_KEY to the respective path and variable names on your system
env_path = r'C:\Users\Flomi\.spyder-py3\API_Keys.env'
load_dotenv(dotenv_path=env_path)

# Provides two different Planet user's API keys that can be choosen as 
# Planet_Key variable to access the Planet Labs API
JACK_KEY = os.getenv("JACK_KEY")
FRANK_KEY = os.getenv("FRANK_KEY")

# Save desired API key to variable
Planet_Key = JACK_KEY

# Setup Planet Data API base URL
URL = "https://api.planet.com/data/v1"

# Setup boundry region of Deering, AK (Could be imported; Included here for simplicity)
# TODO:Change this to import the GeoJSON file
geojson_geometry = {
       "type":"Polygon","coordinates":[
         [
           [-162.80862808227536,66.05894122802519],
           [-162.67404556274414,66.05636369184131],
           [-162.67919540405273,66.07085023305528],
           [-162.7140426635742,66.07669822834144],
           [-162.73550033569333,66.08216210323748],
           [-162.74871826171872,66.09256457840145],
           [-162.73558616638186,66.09760772349222],
           [-162.73798942565915,66.10125903100771],
           [-162.74631500244138,66.10338002568206],
           [-162.76588439941403,66.09764250032609],
           [-162.76399612426752,66.09576448313807],
           [-162.79583930969235,66.08953821061128],
           [-162.81051635742185,66.09166018442527],
           [-162.80862808227536,66.05894122802519]
         ]
       ]
}

# Helper function to printformatted JSON using the json module
def p(data):
    print(json.dumps(data, indent=2))

# This function is designed to get start date and end date, Check that these dates are correct.
# It performs the following checks:
# 1. Converts the date strings to datetime objects using datetime.strptime.
#     1.1. Checks if the month is between 1 and 12.
#     1.2. Ensures the day is correct between 1 and 30 or 31 depending on the month.
#     1.3. Checks for February month if it's 28 or 29 days.
#     1.4. Check Date in this format "YYYY-MM-DD" (Dashes, Numbers, Order of year month day )
# 2. Verifies that the start date is before the end date.
# 3. Validates that both the start and end dates are 2009 or later.
def validate_and_compare_dates(): #(*NEW*)
    try:
        # Get dates input from user
        start_date_input = input("Enter start date (yyyy-mm-dd): ")
        end_date_input = input("Enter end date (yyyy-mm-dd): ")
        
        # Attempt to parse the input strings as dates in the format "yyyy-mm-dd"
        start_date = datetime.strptime(start_date_input, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_input, '%Y-%m-%d')
        print("Valid date format.")
        
        date_valid = True
        # Check if start and end years are 2009 or later
        if start_date.year < 2009 or end_date.year < 2009:
            print("Invalid: Start and End year must be 2009 or later.")
            date_valid = False
        
        # Check if start date is before end date
        if start_date >= end_date:
            print("Invalid: Start date must be before end date.")
            date_valid = False
        
        # Convert start_date and end_date to strings in "YYYY-MM-DD" format
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        return date_valid, start_date_str, end_date_str
    
    except ValueError:
        print("Invalid date format. Please write the date correctly (YYYY-MM-DD).")
        return False, None, None
                
            
# Initializes the server request
# Inputs are the user-defined start and end date to search through
# Start and end dates must be entered in the form year-mo-dy
    
# TODO: This code also is built to support the download of REScenes, if download capacity is large enough
def request_init(start_date, end_date):
    
    # Specify the sensors/satellites or "item types" to include in our results
    # TODO: To include REScenes in the search results, replace the next line with
    # item_types = ["PSScene4Band", "REScene"]
    item_types = ["PSScene4Band"]
    
    # Get filter
    and_filter = get_filter(start_date, end_date)
    
    # Setup the request
    temp_request = {
        "item_types" : item_types,
        "filter" : and_filter
    }
    
    # Return final request
    return temp_request


# Initializes additional request to return only PSScene3Band images
def request_init_3band(start_date, end_date):
    
    # Specify the sensors/satellites or "item types" to include in our results
    item_types = ["PSScene3Band"]
    
    # Get filter
    and_filter = get_filter(start_date, end_date)

    # Setup the request
    temp_request = {
        "item_types" : item_types,
        "filter" : and_filter
    }
    
    # Return request
    return temp_request

# Helper function to get query filter
def get_filter(start_date, end_date):
    
    # Setup Cloud filter; Filters images with over 10% cloud cover
    cloud_filter = {
       "type": "RangeFilter",
       "field_name": "cloud_cover",
       "config": {
         "lte": 0.1
       }
     }
       
    # Setup Geometry filter; Filters images to those that are
    # contained within Deering, AK
    geom_filter = {
       "type": "GeometryFilter",
       "field_name": "geometry",
       "config": geojson_geometry
    }

    
    # Set up DateRangeFilter
    # Find imagery within user-defined dates
    start = start_date + "T00:00:00Z"
    end = end_date + "T23:59:59Z"
    
    date_filter = {
      "type": "DateRangeFilter",
      "field_name": "acquired",
      "config": {
        "gt": start,
        "lte": end
      }
    }

        
    # Setup And logical filter; Combines all filters into one
    and_filter = {
            "type": "AndFilter",
            "config": [cloud_filter, geom_filter, 
                        date_filter]
    }
    
    return and_filter


# Prompts user and gets the number of images they would like to download
def get_download_num():
    num = input("\nHow many images would you like to download?\n(Enter 0 to download all images, -1 to cancel)\n")
    return num
    

# Prompts user and gets starting image index for download
def get_starting_num():
    num = input("\nIs there an image index you would like to start the download at?\nEx: If you have already downloaded the first 15 images in this date range, enter 16\nOtherwise enter 0, or -1 to quit\n")
    return num
    
# Function to print a link to an image's thumbnail
# TODO: Remove this function for release; For testing only
def preview(feature):
    link = feature["_links"]
    thumbnail = link["thumbnail"]
    print(thumbnail, "?api_key=", Planet_Key)


# Function to store all search image ids into the image_ids array
# Geojson is post response, res is server connection
def init_image_arr(geojson, res, image_ids):

    while True:
        
        # Add each image id to the list
        features = geojson["features"]
        for i in range(0, len(geojson["features"])):
            feature = features[i]
            image_ids.append(feature["id"])
        
        # Return link of next result page
        next_url = geojson["_links"]["_next"]
        
        # Send POST request to next result page
        res = session.get(next_url)
        
        # Assign response to a variable
        geojson = res.json()
        
        # Exit if page has no further results
        if len(geojson["features"]) == 0:
            break


# RE_format: This function take id of RE image and return the date as date time object
# ID like this => 2018-12-03T083453_RE4_1B_band1.tif
def RE_format(image_id):
    time = image_id[:17] 
    time = datetime.strptime(time, "%Y-%m-%dT%H%M%S")
    return time

# PS_format: This function take id of PS image and return the date as date time object
# ID like this => 20181203T083453_PS_1B_band1.tif
def PS_format(image_id):
    time = image_id[:15] 
    time = datetime.strptime(time, "%Y%m%dT%H%M%S")
    return time


# Function to remove images of the winter months (Oct 16 to May 15)
# Oct 16 = 290 day of year , May 15 = 136 day of year
# Returns id array of images after removing winter months
# TODO: Alter to desired winter month range
def rem_winter(ids = []):
   clear_ids = []
   
   for i in range(0, len(ids)):
       
        # Reformat current min for comparison
        # Check for RE image
        if ids[i][4] == '-':
            time = RE_format(ids[i])
            
        # Else is PS image
        else:
            time = PS_format(ids[i])
            
        day_of_year = time.timetuple().tm_yday # Get the day of the year from the datetime object

        if 136 < day_of_year < 290:
            clear_ids.append(ids[i])
   return clear_ids



# Function to merge the PSScene3band ids array when image_ids
# Doesn't already contain a 4 banded version of the image
# Returns number of added 3band images
# NOTE: This function is only necessary if both 3 banded and 4 banded images are being searched for
def merge_ids(image_ids = [], scope3band_ids = []):
    
    # Counter to keep track of 3banded images added
    counter_3band = 0
    
    # Loop through each item in scope3band_ids
    for i in range(0, len(scope3band_ids)):
        
        # Bool to keep track of whether item is duplicate
        new = True
        
        # Loop through each item in image_ids, change bool value if image is dupe
        for j in range(0, len(image_ids)):
            if scope3band_ids[i] == image_ids[j]:
                new = False

        # If image is new, append to image_ids list, increment counter_3band
        if new:
            image_ids.append(scope3band_ids[i])
            counter_3band = counter_3band + 1
    
    # Return number of 3band images added
    return counter_3band

            
# Function to sort the image ids based on date
# Returns image ids list after sorting, list with locations of PSScene3band images
# NOTE: scope3band_count will always be 0 unless 3 banded images are also included in the search
def date_sort(image_ids, scope3band_count):
    
    locations = ([0]* (len(image_ids) - scope3band_count)) + [1]* scope3band_count
    dates = []
    
    for i in range(0, len(image_ids)):
        
        # Check for RE image
        if ids[i][4] == '-':
            time = RE_format(ids[i])
            
        # Else is PS image
        else:
            time = PS_format(ids[i])

        dates.append(time)
    
    combined_list = list(zip(dates, image_ids, locations))
    sorted_images = sorted(combined_list)
    
    # Extract the sorted dates, image_id , locations 
    dates = [item[0] for item in sorted_images]
    image_ids = [item[1] for item in sorted_images]
    locations = [item[2] for item in sorted_images]

    # Return locations of PSScene 3 band images
    return image_ids, locations
                



# Creates the order to submit to Planet database
# NOTE: Much of this code is built around the potential to also include 
# RE or Planetscope 3 Banded imagery
def create_order(ids, locations, download_num, start, end, starting_num):
    
    # Create arrays for each item type
    PS3Band = []
    PS4Band = []
    RE = []
    
    
    # Add images to respective array
    for i in range(starting_num, download_num + starting_num):
        
        # Check for RE image
        if ids[i][4] == '-':
            RE.append(ids[i])
            
        # Check for PS3Band image
        elif locations[i] == 1:
            PS3Band.append(ids[i])
            
        # Else must be a PS4Band image
        else:
            PS4Band.append(ids[i])
      
    # Create order name    
    name = str(download_num) + " AOI Images " + start + " to " + end
    
    # Create product list
    products = []
    
    # Create PSScene3Band product
    if len(PS3Band) > 0:
        PS3Product = create_product(PS3Band, "PSScene3Band")
        products.append(PS3Product)
    
    # Create PSScene4Band product
    if len(PS4Band) > 0:
        PS4Product = create_product(PS4Band, "PSScene4Band")
        products.append(PS4Product)
        
    # Create REScene product
    if len(RE) > 0:
        REProduct = create_product(RE, "REScene")
        products.append(REProduct)
        
    # Creates order
    if len(products) > 0:
        order = {
            # Sets order delivery to be downloadable as a zip
            "delivery": {'archive_type': 'zip', 'single_archive': True},
            "name": name,
            "products": products
            }
        return order
    
    else:
        print("\nImproper order setup")
        return None
      
        

# Helper function to create each product bundle
# NOTE: If an error is encountered downloading PS images, it is likely due to
# an improper item type declaration; Check here first
# NOTE: For the orthorectification process, RPC data is required, which is only
# present in the basic_analytic bundle, which is why this bundle is required regardless of sattelite type.
def create_product(item, item_type):
            
    product = {
       "item_ids": item,
       "item_type": item_type,
       "product_bundle": "basic_analytic"
    }
    return product


# Function that polls for success, returns when order is ready to download
def poll(geojson):
    
    # Poll server until state is no longer queued
    while(True):
        
        # Refresh order status URL
        status_url = geojson['_links']['_self']
        res = session.get(status_url)
        
        # Assign response to a variable
        geojson = res.json()
        
        # Assign order state to a variable
        state = geojson['state']
        
        # Check if order is finished processing
        if state in ['success', 'failed', 'partial']:
            return state
        
        # Else print notice
        print("\nProccessing, order state", state)
        
        # Wait before repeating loop
        time.sleep(60)


# Function to download results
# Code taken from https://github.com/planetlabs/notebooks/blob/master/jupyter-notebooks/orders/ordering_and_delivery.ipynb
def download_results(results, overwrite=False):
    results_urls = [r['location'] for r in results]
    results_names = [r['name'] for r in results]
    print('{} items to download'.format(len(results_urls)))
    
    for url, name in zip(results_urls, results_names):
        path = pathlib.Path(os.path.join('data', name))
        
        if overwrite or not path.exists():
            print('downloading {} to {}'.format(name, path))
            r = requests.get(url, allow_redirects=True)
            path.parent.mkdir(parents=True, exist_ok=True)
            open(path, 'wb').write(r.content)
        else:
            print('{} already exists, skipping {}'.format(path, name))
            
            
# =============================================================================
# MAIN CODE BLOCK
# =============================================================================

# NOTE: This code also supports the ability to download 3 Banded PlanetScope imagery when
# 4 Banded images are unavailable. This functionality has been removed from this main block,
# due to the fact that certain permissions are required to download basic_analytic files for
# 3 Banded imagery, which we currently do not have access to. However, the methods in this code 
# still have the capability to do so in case someone else using this code has those permissions.
# Please see this commit for how to include this functionality in the main code block:
# https://github.com/fwitmer/CoastlineExtraction/commit/6b90bd9034e6089434d82e9d8e581ad6e0bdfd79



# Setup the session
session = requests.Session()

# Authenticate
session.auth = (Planet_Key, "")

# Make a GET request to the Planet Data API
res = session.get(URL)

# Check connection
if res.status_code == 200:
    print('Connected to server')
else:
    print('Connection failed, error status code: ', res.status_code)
    exit()
    
# Setup the quick search endpoint url
quick_url = "{}/quick-search".format(URL)

# Setup the orders endpoint url
orders_url = 'https://api.planet.com/compute/ops/orders/v2'

# Array to store IDs of all images
image_ids = []

# Integer to store the number of scope3band images that don't have 
# 4 band copies already in image_ids
# Requiring a scope3band_count is outdated as of 7/24/20 When PSScope3Band functionality is 
# Removed from the main block
scope3band_count = 0

# Bool array to store the positions of scope3band images in the image_ids array
locations = []

# Loops until user inputs meaningful date range (*New*)
while True:
    print("Print date in format of YYYY-MM-DD")
    print("1. Ensure start date is before end date")
    print("2. Year is after 2009 ")
    
    date_valid, start, end = validate_and_compare_dates()
    
    if date_valid:
        print(f"Start date: {start_date}, End date: {end_date}")
        break

while True:
   
    # Creates the request
    request = request_init(start, end)
    
    # Send the POST request to the API quick search endpoint
    res = session.post(quick_url, json=request)
    
    # Assign the response to a variable
    geojson = res.json()
    
    # Puts available images into image_ids array
    try:
        print("\nProcessing...")
        init_image_arr(geojson, res, image_ids)
        print("Images found")
        break
    except:
        #TODO: This except might also trigger if server rejects the request; 
        #Potentially there should be an additional message added here
        print(res)
        print("\nThere is no data available of your AOI in that date range, please try again!")


# Removes all images from Oct 16 - May 15
# TODO: Remove this call if this additional filter isn't desired
image_ids = rem_winter(image_ids)
    

# Sorts ids based on date
image_ids, locations = (image_ids, scope3band_count)


print("\nThere are", len(image_ids),"images availabe to download in your AOI from", start, "to", end)


# Gets max number of images to download
while(True):
    download_num = get_download_num()
    
    # Check user input is valid
    if type(download_num) is str:
        try:
            download_num = int(download_num)
            break;
        except:
          print("\nInvalid input")  
    else:
        print("\nInvalid input")
        
# Check for user exit
if download_num < 0:
    print("\nUser has terminated the program")
    exit()
    

# Checks if there is an image download start point
while(True):
    starting_num = get_starting_num()
    
    # Check user input is valid
    if type(starting_num) is str:
        try:
            starting_num = int(starting_num)
            
            # Check starting num is possible
            if starting_num + download_num > len(image_ids):
                print("\n starting index too large for number of image downloads requested")
            else:
                break
            
        except:
          print("\nInvalid input")  
    else:
        print("\nInvalid input")

# Check for user exit
if starting_num < 0:
    print("\nUser has terminated the program")
    exit()
    
# Downloads all images if zero entered
elif download_num == 0:
    download_num = len(image_ids)
    print("\nDownloading", download_num, "images")
    
# Downloads all images and prints response if input number is too large
elif download_num > len(image_ids):
    download_num = len(image_ids)
    print("\nInput number too large; Downloading all available images")
    print("\nDownloading", download_num, "images")


# Creates order for download
order = create_order(image_ids, locations, download_num, start, end, starting_num)

# Send the order request to planet orders_url endpoint
res = session.post(orders_url, json=order)

# Assign the response to a variable
geojson = res.json()

# Check if order went through
try: 
    print("\nOrder submitted successfully: Order status", geojson['state'])
except:
    print("\nOrder submission failed, please ensure order size does not exceed your remaining download quota")
    exit()


# Wait until order is ready to download
while True:
    try:
        print("\nBeginning session poll")
        final_state = poll(geojson)
        # Ensure order is no longer being processed:
        if final_state != "queued" and final_state != "processing":
            break
        else:
            print("\nAn error has occured when processing your request.")
            print("\nYour current order state is: ", final_state)
            print("Waiting for 2 minutes, then attempting to reconnect to server")
            time.sleep(120)
    
    # Sometimes server will reject multiple session requests, this catches the error
    except:
        print("\nAn error has occured when processing your request.")
        print("\nYour current order state is: ", final_state)
        print("Waiting for 2 minutes, then attempting to reconnect to server")
        time.sleep(120)




# Refresh order status URL
status_url = geojson['_links']['_self']
res = session.get(status_url)

# Assign response to a variable
geojson = res.json()

 
               
# Check final order state    
# Check if success
if final_state == "success":
    
    # Downloads complete order
    print("\nOrder activated successfully! Commencing download")
    results = geojson['_links']['results']
    download_results(results)
    
# Check if partial success
elif final_state == "partial":
    
    # Downloads partial order
    print("\nOrder partially successfully! Commencing download")
    results = geojson['_links']['results']
    download_results(results)
    
# Otherwise, order failed
else:
    print("\nOrder was not activated successfully.", "Final order status:", final_state)
    





   

   
   
   
   
   
   
   
   
   
   
   
   
   
   
 
