#!/usr/bin/python3

import requests, os, sys, getpass
import json, time
import keyring
from datetime import datetime, timedelta
from ics import Calendar, Event
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options



# If modifying these SCOPES, delete the token.json file.


def authenticate_google_calendar():
    """Authenticate the user and return a service object for Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service


def check_event_exists(service, event_data):
    print("checking event-----------------------------")
    
    """Check if an event exists in Google Calendar within the specified time range."""
    # Parse the start and end times
    start_time = event_data['start'].replace("Z", "+1000")
    end_time = event_data['end']
    print("Start Time: {} ".format(start_time))
    print

    # Search for events in the specified time range
    print("getting results")
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    print(events)

    # Check if there are any events with the same title
    for event in events:
        print(event)
        print("Summary:  ")
        print(event['summary'])
        print("Title:  ")
        print(event_data['title'])
        if event['summary'] == event_data['title']:
            return True  # Event already exists
        else:
            print("no event")
            #return False  # No existing event found



def create_google_calendar_event(service, event_data):
    """Creates an event in Google Calendar using the provided event_data dictionary."""
    event = {
        'summary': event_data['title'],
        'description': event_data['description'],
        'start': {
            'dateTime': event_data['start'],
            'timeZone': 'Australia/Melbourne',
        },
        'end': {
            'dateTime': event_data['end'],
            'timeZone': 'Australia/Melbourne',
        },
        'colorId': '10',  # Optional, to match the color in the provided data
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {created_event.get('htmlLink')}")




def fetch_events(service, event_data):
    """Fetch events for a specific time range."""
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=event_data['start'],  # Convert to ISO format with 'Z' for UTC
        timeMax=event_data['end'],
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    
    # Check for events with the same title and overlapping time
    for event in events:
        if event['summary'] == event_data['title']:
            print("Summary:  ")
            print(event['summary'])
            print("Title:  ")
            print(event_data['title'])
            return True  # Event already exists
        else:
            print("Summary:  ")
            print(event['summary'])
            print("Title:  ")
            print(event_data['title'])
            return False  # No existing event found

def store_credentials(service_name, username, password):
    """Stores the login credentials securely using the keyring library."""
    keyring.set_password(service_name, username, password)
    print("Credentials stored successfully.")

def get_credentials(service_name, username):
    """Retrieves stored credentials securely."""
    password = keyring.get_password(service_name, username)
    if password is None:
        print("No credentials found.")
    return password


def login_to_theircare(username, password):
    # Specify the path to the ChromeDriver
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    # Navigate to the login page
    driver.get("https://theircare.fullybookedccms.com.au/family/login")
    print ("Headless Firefox Initialized")
    # Wait for the page to load (you can use explicit wait instead of sleep for better practice)
    time.sleep(3)

    # Find the username and password input fields by their name or id
    username_field = driver.find_element(By.NAME, 'j_username')  # Adjust the field name
    password_field = driver.find_element(By.NAME, 'j_password')  # Adjust the field name

    # Enter the username and password
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Submit the form (you can simulate hitting Enter or clicking the login button)
    password_field.send_keys(Keys.RETURN)

    # Wait for the login to process and the next page to load
    time.sleep(5)

    # Check the title of the page or for an element that verifies a successful login
    if "Logout" in driver.page_source:  # Adjust this based on the actual page structure
        print("Login successful!")

        # Retrieve cookies and store the JSESSIONID
        cookies = driver.get_cookies()
        jsessionid = None
        for cookie in cookies:
            if cookie['name'] == 'JSESSIONID':
                jsessionid = cookie['value']
                break
        
        if jsessionid:
            print(f"JSESSIONID: {jsessionid}")
            
        else:
            print("JSESSIONID not found.")
    else:
        print("Login failed.")
        print("Login failed.")
        sys.exit(0)
    # Close the browser
    driver.quit()
    return jsessionid


def get_start_end_of_current_month():
    # Get the current date
    current_date = datetime.now()

    # Calculate the first day of the current month
    start_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calculate the last day of the current month
    next_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = (next_month - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Format the dates to the desired format
    start_of_month_str = start_of_month.strftime('%Y-%m-%dT%H:%M:%S')
    end_of_month_str = end_of_month.strftime('%Y-%m-%dT%H:%M:%S')

    return start_of_month_str, end_of_month_str

def create_url_with_dates(start, end):
    url = f"https://theircare.fullybookedccms.com.au/family/portlet/bookings.json?start={start}&end={end}&timeZone=Australia/Melbourne"
    return url




SCOPES = ['https://www.googleapis.com/auth/calendar']
def main():
 #setup for login to theircare
    service_name = "TheirCareService"

    # Uncomment the following lines to store your credentials for the first time
    username = "" #input email here for login
    
    # Retrieve credentials securely
    password = get_credentials(service_name, username)

    if password:  # Proceed if password was retrieved successfully
        JSESSIONID = login_to_theircare(username, password)
    else:
        password = getpass.getpass(prompt="Enter your password: ")
        store_credentials(service_name, username, password)
        JSESSIONID = login_to_theircare(username, password)

        if JSESSIONID:
            # Example of making a request after login
            dashboard_url = "https://theircare.fullybookedccms.com.au/family/dashboard"  # Example URL
            dashboard_response = session.get(dashboard_url)
            print(dashboard_response.text)  # Print the dashboard HTML or further process it



    # Get the start and end of the current month
    start, end = get_start_end_of_current_month()

    # Generate URL with the start and end dates
    url = create_url_with_dates(start, end)

    # The URL of the page you're trying to access

    # Define the cookie you have, for example:
    cookies = {
        'JSESSIONID': JSESSIONID,
        'calendarDefaultView': 'dayGridMonth'  # Replace with actual cookie name and value
   }

    # You can also include headers if necessary (e.g., user agent, etc.)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Make the GET request with the cookie
    response = requests.get(url, headers=headers, cookies=cookies)

    # Check the response
    if response.status_code == 200:
        # Get the response content as JSON
        json_content = response.json()
    # Pretty-print the JSON content
        print(json.dumps(json_content, indent=4))
    else:
        print(f"Failed to fetch the page, status code: {response.status_code}")

    service = authenticate_google_calendar()
    # Create events in Google Calendar
    for event_data in json_content:
        
        if check_event_exists(service, event_data):
            print(f"Event '{event_data['title']}' already exists.")
        else:
            # Create the event in Google Calendar
            event_data['start'] = event_data['start'].replace("Z", "+1000")
            event_data['end'] = event_data['end'].replace("Z", "+1000")
            create_google_calendar_event(service, event_data)
            
if __name__ == '__main__':
    main()
