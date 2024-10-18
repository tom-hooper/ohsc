#!/usr/bin/python3

import requests

# The URL of the page you're trying to access
url = "https://theircare.fullybookedccms.com.au/family/portlet/bookings.json?start=2024-09-30T00:00:00&end=2024-11-09T00:00:00&timeZone=Australia/Melbourne"

# Define the cookie you have, for example:
cookies = {
    'cookie_name': 'JSESSIONID=1C6C24EE34135275F7180329E6390001; calendarDefaultView=dayGridMonth',  # Replace with actual cookie name and value
}

# You can also include headers if necessary (e.g., user agent, etc.)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Make the GET request with the cookie
response = requests.get(url, headers=headers, cookies=cookies)

# Check the response
if response.status_code == 200:
    print("Page fetched successfully")
    print(response.text)  # This will print the HTML content of the page
else:
    print(f"Failed to fetch the page, status code: {response.status_code}")
