#!/usr/bin/python3

import requests, os
import json
import keyring
from ics import Calendar, Event
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import getpass


"""def create_ics_file(events_data):
    
    Creates an .ics file with multiple events from a list of event data.

    Args:
        events_data (list): List of dictionaries containing event data.
        ics_filename (str): The filename of the .ics file to save the events.
    
    # Create a new calendar
    cal = Calendar()

    # Iterate through each event data dictionary
    for event_data in events_data:
        # Create a new event
        event = Event()
        event.name = event_data['title']
        event.description = event_data['description']
        
        # Parse the start and end times
        event.begin = datetime.strptime(event_data['start'], "%Y-%m-%dT%H:%M:%S.%fZ")
        event.end = datetime.strptime(event_data['end'], "%Y-%m-%dT%H:%M:%S.%fZ")

        # Add the event to the calendar
        cal.events.add(event)

    # Save the calendar to an .ics file
    #with open(ics_filename, 'w') as f:
    #    f.writelines(cal)
    return cal
"""
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


#def read_ics_file(ics_file):
#    """Read the .ics file and extract event data."""
#    #with open(ics_file, 'r') as file:
#    #    calendar = Calendar(file.read())
#    print('-------------------------------------------------------')
#    print(ics_file)
#    events = []
#    for event in ics_file.events:
#        event_data = {
#            'summary': event.name,
#            'description': event.description,
#            'start': event.begin.datetime.isoformat(),
#            'end': event.end.datetime.isoformat()
#        }
#        events.append(event_data)
#    return events
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


import keyring
import requests

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
    """Logs into the TheirCare website and returns the session object and JSESSIONID."""
    login_url = "https://theircare.fullybookedccms.com.au/family/login"
    
    # Start a session
    session = requests.Session()

    # Define the payload with your login credentials
    payload = {
        'username': username,  # Adjust the field name if necessary
        'password': password,  # Adjust the field name if necessary
    }

    # Send a POST request to log in
    response = session.post(login_url, data=payload)

    # Check if login was successful
    if response.ok and "Logout" in response.text:  # Adjust this based on actual response
        print("Login successful!")

        # Retrieve JSESSIONID cookie
        jsessionid = session.cookies.get('JSESSIONID')
        print(f"JSESSIONID: {jsessionid}")  # Store or use this value as needed
        
        return session, jsessionid  # Return both session and JSESSIONID
    else:
        print("Login failed.")
        return None, None

if __name__ == "__main__":
    # Replace with your actual service name
    service_name = "TheirCareService"

    # Uncomment the following lines to store your credentials for the first time
    # username = "your_username"
    # password = "your_password"
    # store_credentials(service_name, username, password)

    # Retrieve credentials securely
    username = "your_username"  # Replace with your actual username
    password = get_credentials(service_name, username)

    if password:  # Proceed if password was retrieved successfully
        session, jsessionid = login_to_theircare(username, password)

        if session:
            # Example of making a request after login
            dashboard_url = "https://theircare.fullybookedccms.com.au/family/dashboard"  # Example URL
            dashboard_response = session.get(dashboard_url)
            print(dashboard_response.text)  # Print the dashboard HTML or further process it



SCOPES = ['https://www.googleapis.com/auth/calendar']
def main():
 #setup for login to theircare
    service_name = "TheirCareService"

    # Uncomment the following lines to store your credentials for the first time
    username = "chantellefinderup@gmail.com"
    
    # Retrieve credentials securely
    #username = "your_username"  # Replace with your actual username
    password = get_credentials(service_name, username)

    if password:  # Proceed if password was retrieved successfully
        session = login_to_theircare(username, password)
    else:
        password = getpass.getpass(prompt="Enter your password: ")
        store_credentials(service_name, username, password)
        session = login_to_theircare(username, password)

        if session:
            # Example of making a request after login
            dashboard_url = "https://theircare.fullybookedccms.com.au/family/dashboard"  # Example URL
            dashboard_response = session.get(dashboard_url)
            print(dashboard_response.text)  # Print the dashboard HTML or further process it



    # The URL of the page you're trying to access
 #   url = "https://theircare.fullybookedccms.com.au/family/portlet/bookings.json?start=2024-09-30T00:00:00&end=2024-11-09T00:00:00&timeZone=Australia/Melbourne"

    # Define the cookie you have, for example:
#    cookies = {
#        'JSESSIONID': '661876440897F7D0336C0DBF2AE41EFD',
#        'calendarDefaultView': 'dayGridMonth'  # Replace with actual cookie name and value
 #   }

    # You can also include headers if necessary (e.g., user agent, etc.)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    # Make the GET request with the cookie
    response = requests.get(url, headers=headers, cookies=cookies)

    # Check the response
  #  if response.status_code == 200:
        # Get the response content as JSON
 #       json_content = response.json()

    # Pretty-print the JSON content
#        print(json.dumps(json_content, indent=4))
 #   else:
 #       print(f"Failed to fetch the page, status code: {response.status_code}")

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
