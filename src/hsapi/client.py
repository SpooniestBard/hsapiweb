from yaml import safe_load
import requests
from datetime import datetime,timedelta

class BadCredentialsException(Exception):
    """
    `BadCredentialsException` is raised when the library is uanble to retrieve an OAuth token with the provided
    credentials
    """
    pass


class OAuthToken:
    """
    Internal representation of an OAuth token
    TODO: Handle retrieval of new token on expiration
    """
    def __init__(self, token, expiration_seconds):
        self.token = token
        self.expires_on = datetime.now() + timedelta(seconds=expiration_seconds)
    
    def is_expired(self) -> bool:
        datetime.now() > self.expires_on


class HSApiClient:
    """
    Hearthstone API client. Documentation can be found at
    https://develop.battle.net/documentation/hearthstone/game-data-apis
    """
    API_BASE_URL = 'https://us.api.blizzard.com/hearthstone'

    SEARCH_ALLOWED_FILTERS= [
        "set",
        "class",
        "manaCost",
        "attack",
        "health",
        "collectible",
        "rarity",
        "type",
        "minionType",
        "keyword",
        "textFilter",
        "gameMode",
    ]

    def __init__(self, region='us', locale='en_US'):
        self.region = region
        self.locale = locale

        with open('credentials.yml', 'r') as creds_file:
            credentials = safe_load(creds_file)
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']
        
        # Get an OAuth Token
        # curl -u {client_id}:{client_secret} -d grant_type=client_credentials https://us.battle.net/oauth/token
        response = requests.post(
            'https://us.battle.net/oauth/token',
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"})
        
        if not response.ok:
            raise BadCredentialsException(f"Unable to obtain OAuth token: {response.content}")
        
        response_json = response.json()
        
        self.oauth_token = OAuthToken(response_json['access_token'], response_json['expires_in'])
    
    def search(self, **args):
        args['access_token'] = self.oauth_token.token
        args['region'] = self.region
        args['locale'] = self.locale
        response = requests.get(f"{self.API_BASE_URL}/cards", params=args)

        if not response.ok:
            # TODO: Error handling
            pass
        return response.json()['cards']
