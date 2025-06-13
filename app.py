from flask import Flask, render_template, jsonify, request
import requests
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token
import os
import logging
import google.auth # Import google.auth
from google.auth.exceptions import DefaultCredentialsError # Import specific exception

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BACKEND_URL = "https://challenge-server-service-648143003204.us-central1.run.app"
DATABASE_URL = "https://database-service-648143003204.us-central1.run.app"
PORT = int(os.environ.get('PORT', 8080))

@app.route('/')
def index():
    header_to_check = 'X-Goog-Authenticated-User-Email'
    header_exists_simple = header_to_check in request.headers
    header_exists_case_insensitive = False
    for header_name in request.headers.keys():
        if header_name.lower() == header_to_check.lower():
            header_exists_case_insensitive = True
            break
    header_value = request.headers.get(header_to_check)
    print(header_value)
    header_value_case_insensitive = None
    for header_name, value in request.headers.items():
        if header_name.lower() == header_to_check.lower():
            header_value_case_insensitive = value
            break
    return render_template(
        'index.html',
        header_to_check=header_to_check,
        header_exists_simple=header_exists_simple,
        header_exists_case_insensitive=header_exists_case_insensitive,
        header_value=header_value,
        header_value_case_insensitive=header_value_case_insensitive
    )

def get_data():
    token = None
    try:
        target_audience = DATABASE_URL
        auth_req = GoogleAuthRequest()

        logging.info(f"Attempting to fetch ID token for target audience: {target_audience}")

        try:
            token = id_token.fetch_id_token(auth_req, target_audience)
            if not token:
                logging.error("id_token.fetch_id_token returned an empty or None token.")
                return jsonify({"error": "Failed to obtain ID token: Token is empty."}), 500
            logging.info(f"Successfully fetched ID Token (first 10 chars): {token[:10]}...")

        except Exception as e:
            logging.error(f"Error fetching ID token: {e}")
            logging.error("Please ensure your environment is authenticated (e.g., `gcloud auth application-default login` locally, or proper service account setup on GCP).")
            return jsonify({"error": f"Failed to obtain ID token: {e}"}), 500

        headers = {
            "Authorization": f"Bearer {token}"
        }
        logging.info(f"Constructed headers: {list(headers.keys())}") # Use list() for clearer logging of keys

        logging.info(f"Making GET request to: {DATABASE_URL}")
        response = requests.get(f"{DATABASE_URL}", headers=headers)

        logging.info(f"Actual headers sent by requests library: {response.request.headers}")

        response.raise_for_status()

        logging.info(f"Request successful. Status Code: {response.status_code}")
        matching_data = response.json()
        return matching_data

    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with backend (requests.exceptions.RequestException): {e}")
        if e.response is not None:
            logging.error(f"Backend response status: {e.response.status_code}, text: {e.response.text}")
        return jsonify({"error": f"Error communicating with backend: {e}"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred in get_matching_data: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


@app.route('/get_matching_data', methods=['GET'])
def get_matching_data():
    token = None
    try:
        target_audience = BACKEND_URL
        auth_req = GoogleAuthRequest()

        logging.info(f"Attempting to fetch ID token for target audience: {target_audience}")

        try:
            token = id_token.fetch_id_token(auth_req, target_audience)
            if not token:
                logging.error("id_token.fetch_id_token returned an empty or None token.")
                return jsonify({"error": "Failed to obtain ID token: Token is empty."}), 500
            logging.info(f"Successfully fetched ID Token (first 10 chars): {token[:10]}...")

        except Exception as e:
            logging.error(f"Error fetching ID token: {e}")
            logging.error("Please ensure your environment is authenticated (e.g., `gcloud auth application-default login` locally, or proper service account setup on GCP).")
            return jsonify({"error": f"Failed to obtain ID token: {e}"}), 500

        headers = {
            "Authorization": f"Bearer {token}"
        }
        logging.info(f"Constructed headers: {list(headers.keys())}") # Use list() for clearer logging of keys

        logging.info(f"Making POST request to: {BACKEND_URL}")
        body = get_data()
        response = requests.post(f"{BACKEND_URL}", headers=headers, json = body)

        logging.info(f"Actual headers sent by requests library: {response.request.headers}")

        response.raise_for_status()

        logging.info(f"Request successful. Status Code: {response.status_code}")
        matching_data = response.json()
        return jsonify(matching_data)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with backend (requests.exceptions.RequestException): {e}")
        if e.response is not None:
            logging.error(f"Backend response status: {e.response.status_code}, text: {e.response.text}")
        return jsonify({"error": f"Error communicating with backend: {e}"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred in get_matching_data: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)