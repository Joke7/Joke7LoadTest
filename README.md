# API Load Testing Script

This script is designed to simulate a load test against the Jock7 API. It reads user data from a CSV file, performs a series of API requests for each user in parallel, and saves the results to a new CSV file.

## Prerequisites

- Python 3
- `pip` for installing packages

## Setup

1.  **Install Dependencies**:
    Navigate to the `load-test` directory and run the following command to install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Prepare the Input CSV**:
    Make sure you have a `users_export_2025-11-01.csv` file in the same directory. This file must contain a `phone` column with the phone numbers of the users to be tested.

## Configuration

The script can be configured by modifying the following variables at the top of `load-test.py`:

-   `CSV_FILE`: The name of the input CSV file containing user data. (Default: `users_export_2025-11-01.csv`)
-   `OUTPUT_CSV_FILE`: The name of the file where the test results will be saved. (Default: `users_export_2025-11-01_results.csv`)
-   `MAX_WORKERS`: The number of parallel threads to use for the load test. (Default: `10`)
-   `BASE_URL`: The base URL of the API to be tested.

## Usage

To run the load test, execute the following command from the `load-test` directory:

```bash
python load-test.py
```

The script will start processing the users in parallel and print the progress. Once finished, the results will be saved in the specified output CSV file.

## Script Logic

For each user in the input CSV, the script performs the following actions:

1.  **Login**: Authenticates the user using their phone number and a hardcoded password (`123456`) to obtain an access token.
2.  **Get Profile**: Fetches the user's profile data.
3.  **Get Stats**: Fetches the user's game statistics.
4.  **Submit Code**: Submits a randomly generated code.

The results of these actions, including the status of each request, the submitted code, and the total execution time, are written to the output CSV file.
