from datetime import datetime,timedelta
from yaml import safe_load
import requests

API_BASE_URL = 'https://us.api.blizzard.com/hearthstone'

class OAuthAcquisitionException(Exception):
    """
    `OAuthAcquisitionException` is raised when we are uanble to retrieve an OAuth token with the
    provided credentials
    """


# TODO: Break this down into better errors
class APIException(Exception):
    """
    `APIException` is raised when a 400 response is received when attempting to query the
    Hearthstone API
    """


class OAuthToken:
    """
    Internal representation of an OAuth token
    TODO: Handle retrieval of new token on expiration
    """
    def __init__(self, token, expiration_seconds):
        self.token = token
        self.expires_on = datetime.now() + timedelta(seconds=expiration_seconds)

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_on


class HSApiClient:
    """
    Hearthstone API client. Documentation can be found at
    https://develop.battle.net/documentation/hearthstone/game-data-apis
    """

    def __init__(self, region='us', locale='en_US', page_size=10):
        self.region = region
        self.locale = locale
        self.page_size = page_size

        with open('../credentials.yml', 'r', encoding='utf-8') as creds_file:
            credentials = safe_load(creds_file)
            self.client_id = credentials['client_id']
            self.client_secret = credentials['client_secret']

        # Get an OAuth Token - example curl request:
        # curl -u {client_id}:{client_secret} -d grant_type=client_credentials
        # https://us.battle.net/oauth/token
        response = requests.post(
            'https://us.battle.net/oauth/token',
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"})

        if not response.ok:
            raise OAuthAcquisitionException(f"Unable to obtain OAuth token: {response.content}")

        response_json = response.json()
        self.oauth_token = OAuthToken(response_json['access_token'], response_json['expires_in'])

        # Retrieve HS metadata
        self.metadata = HSApiMetadata(self.region, self.locale, self.oauth_token)

    def search(self, **args):
        args['access_token'] = self.oauth_token.token
        args['region'] = self.region
        args['locale'] = self.locale
        args['pageSize'] = self.page_size
        response = requests.get(f"{API_BASE_URL}/cards", params=args)

        if not response.ok:
            raise APIException(response.content)

        return [ HearthstoneCard(self.metadata, **card) for card in response.json()['cards'] ]


class HSApiMetadata:
    """
    Container class used to hold card metadata
    """
    def __init__(self, region, locale, oauth_token):
        response = requests.get(
            f"{API_BASE_URL}/metadata",
            params={'access_token': oauth_token.token, 'locale': locale, 'region': region})

        if not response.ok:
            raise APIException(response.content)

        response_json = response.json()

        # Store each metadata type in a dictionary by ID for faster lookup
        self.types = { i['id']: i  for i in response_json['types'] }
        self.rarities = { i['id']: i  for i in response_json['rarities'] }
        self.classes = { i['id']: i  for i in response_json['classes'] }

        # Sets need special logic to ahndle set aliasing
        self.sets = {}
        for i in response_json['sets']:
            self.sets[i['id']] = i
            if 'aliasSetIds' in i:
                for j in i['aliasSetIds']:
                    self.sets[j] = i


class HearthstoneCard:
    """
    Internal representation of a Hearthstone card
    """
    def __init__(self, metadata, **args):
        self.name = args['name']
        self.art = args['image']
        self.holo_art = args['imageGold']
        self.set = metadata.sets[args['cardSetId']]['name']
        self.card_class = metadata.classes[args['classId']]['name']
        self.mana_cost = args['manaCost']
        self.rarity = metadata.rarities[args['rarityId']]['name']
        self.type = metadata.types[args['cardTypeId']]['name']
