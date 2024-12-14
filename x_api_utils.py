import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def get_x_post(post_id):
    # Get API credentials from environment variables
    bearer_token = os.getenv("X_BEARER_TOKEN")

    if not bearer_token:
        print("Error: X_BEARER_TOKEN environment variable not set.")
        return None

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"  # Important for v2!
    }

    url = f"https://api.twitter.com/2/tweets/{post_id}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        json_response = response.json()
        return json_response
    except requests.exceptions.RequestException as e:
      if response.status_code == 401:
          print(f"Error: Unauthorized. Check your Bearer Token. Details: {e}")
      elif response.status_code == 404:
          print(f"Error: Tweet with ID {post_id} not found. Details: {e}")
      elif response.status_code == 429:
          print(f"Error: Too Many Requests. You are being rate limited. Details: {e}")
      else:
          print(f"Error fetching tweet: {e}")
      if hasattr(response, 'text'):
          print(f"Response text: {response.text}")
      return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        if hasattr(response, 'text'):
          print(f"Response text: {response.text}")
        return None
