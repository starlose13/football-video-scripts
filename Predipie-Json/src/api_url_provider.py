# # api_url_provider.py
# from datetime import datetime, timedelta

# class ApiUrlProvider:
#     """Class to calculate API URLs based on current and previous dates."""

#     def __init__(self, base_url='https://data-provider.ledoso.com/predipie/well-known'):
#         self.base_url = base_url

#     def get_current_date_url(self):
#         """Return API URL for the current date."""
#         current_date = datetime.now().strftime('%Y-%m-%d')
#         return f'{self.base_url}?startAfter={current_date}'

#     def get_previous_date_url(self):
#         """Return API URL for the previous date."""
#         previous_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
#         return f'{self.base_url}?startAfter={previous_date}'
