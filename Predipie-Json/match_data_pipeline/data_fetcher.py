import requests

class DataFetcher:
    """Handles data fetching from the API with retry capability."""
    
    def __init__(self, url, retries=3, timeout=10):
        self.url = url
        self.retries = retries
        self.timeout = timeout

    def fetch_data(self):
        """Fetches data from the API with a specified number of retries."""
        attempt = 0
        while attempt < self.retries:
            try:
                response = requests.get(self.url, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                attempt += 1
                print(f"Attempt {attempt} - API request error: {e}")
        print(f"Failed to fetch data after {self.retries} attempts.")
        return []
