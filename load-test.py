import csv
import requests
import time
import random
import string
import concurrent.futures
from datetime import datetime

# Configuration
CSV_FILE = 'users-export.csv'
MAX_WORKERS = 100  # Number of parallel threads
BASE_URL = 'https://jock7-api.promosport.tn/api/v1'
LOGIN_URL = f'{BASE_URL}/auth/login'
PROFILE_URL = f'{BASE_URL}/auth/profile'
STATS_URL = f'{BASE_URL}/games/analytics/my-stats'
SUBMIT_CODE_URL = f'{BASE_URL}/games/submit-code'

def generate_random_code(length=19):
    """Generates a random alphanumeric code."""
    # The format seems to be 18 digits and a final character (letter or digit).
    # Example: 084181246081600198c
    numeric_part = ''.join(random.choices(string.digits, k=length - 1))
    last_char = random.choice(string.ascii_lowercase + string.digits)
    return f"{numeric_part}{last_char}"

def process_user(user):
    """Processes a single user: login, get profile, get stats, and submit code."""
    phone = user.get('phone')
    password = "123456"

    if not phone:
        return {
            'login_status': 'Failed: Missing phone',
            'profile_status': 'Skipped',
            'stats_status': 'Skipped',
            'submit_code_status': 'Skipped',
            'submitted_code': 'N/A',
            'execution_time': 0
        }

    start_time = time.time()
    results = {}
    headers = {}
    access_token = None

    # 1. Login
    try:
        response = requests.post(LOGIN_URL, json={'phone': phone, 'password': password})
        if response.status_code == 201 or response.status_code == 200:
            results['login_status'] = f'Success ({response.status_code})'
            access_token = response.json().get('accessToken')
            headers = {'Authorization': f'Bearer {access_token}'}
        else:
            results['login_status'] = f'Failed ({response.status_code}) - {response.text[:100]}'
    except requests.RequestException as e:
        results['login_status'] = f'Failed (Exception) - {e}'

    # If login failed, skip other requests
    if not access_token:
        results['profile_status'] = 'Skipped'
        results['stats_status'] = 'Skipped'
        results['submit_code_status'] = 'Skipped'
        results['submitted_code'] = 'N/A'
        results['execution_time'] = round(time.time() - start_time, 2)
        return results

    # 2. Get Profile
    try:
        response = requests.get(PROFILE_URL, headers=headers)
        results['profile_status'] = f'Success ({response.status_code})' if response.ok else f'Failed ({response.status_code})'
    except requests.RequestException as e:
        results['profile_status'] = f'Failed (Exception) - {e}'

    # 3. Get Stats
    try:
        response = requests.get(STATS_URL, headers=headers)
        results['stats_status'] = f'Success ({response.status_code})' if response.ok else f'Failed ({response.status_code})'
    except requests.RequestException as e:
        results['stats_status'] = f'Failed (Exception) - {e}'

    # 4. Submit Code
    random_code = generate_random_code()
    results['submitted_code'] = random_code
    try:
        response = requests.post(SUBMIT_CODE_URL, headers=headers, json={'code': random_code})
        results['submit_code_status'] = f'Success ({response.status_code})' if response.ok else f'Failed ({response.status_code}) - {response.text[:100]}'
    except requests.RequestException as e:
        results['submit_code_status'] = f'Failed (Exception) - {e}'

    results['execution_time'] = round(time.time() - start_time, 2)
    return results

def main():
    """Main function to run the load test."""
    try:
        with open(CSV_FILE, mode='r', newline='') as infile:
            reader = csv.DictReader(infile)
            users_data = list(reader)
            fieldnames = reader.fieldnames
    except FileNotFoundError:
        print(f"Error: The file {CSV_FILE} was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    new_columns = ['login_status', 'profile_status', 'stats_status', 'submit_code_status', 'submitted_code', 'execution_time']
    # Add new columns to fieldnames if they don't exist
    for col in new_columns:
        if col not in fieldnames:
            fieldnames.append(col)

    # Process users in parallel
    print(f"Starting load test with {len(users_data)} users and {MAX_WORKERS} parallel workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Use map to process users and get results in order
        results = list(executor.map(process_user, users_data))

    # Combine original user data with the results
    for i, user in enumerate(users_data):
        user.update(results[i])

    # Generate a unique filename with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"results_{timestamp}.csv"

    # Write the updated data to the new CSV file
    try:
        with open(output_filename, mode='w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users_data)
        print(f"\nLoad test finished. Results have been saved to {output_filename}.")
    except Exception as e:
        print(f"An error occurred while writing to the CSV file: {e}")

if __name__ == '__main__':
    main()
