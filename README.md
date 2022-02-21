# `hsapiweb` - (Please hire me)
This is a library and Flask UI for querying the Hearthstone card search API

## Setup Instructions
* Clone this repository
* Create a `credentials.yml` file in the root directory of the following format

```
---
client_id: <Battle.net application client ID>
client_secret: <Battle.net application secret>
...
```

* Create a Python virtualenv

```
$ virtualenv env
$ source env/bin/activate
```

* Install requirements.txt libraries

```
$ pip install -r requirements.txt
```

* **Change directory to `src`**
* Set the `FLASK_APP` environment variable to `server`

```
$ export FLASK_APP=server
```

* Run `flask run` to start the server


## Usage
The web frontend can be reached at http://127.0.0.1:5000 by default. The default route should automatically redirect to `/search`. This route can be used to query the Hearthstone card search API by filling out input boxes in the form control and pressing the "Submit" button. Knowledge of the Hearthstone API will be somewhat necessary for tricker queries, but the search specified in the assignment is pre-populated and can be viewed by hitting "Submit" when loading the page.


## Things To Improve
* Frontend Improvements
  * Too many. If I had this to do over again, I would have written it as a single-page React app
  * If sticking with this design, I'd like to have the search page be updated by an AJAX query rather than redirecting
  * Use parsed metadata to generate picker-style fields instead of text boxes for most fields (e.g. Card rarity, set names)
  * Better styling, UX
* Backend Improvements
  * Make HearthstoneCard a base type, extend to spells, minions, and heroes
  * Create means to refresh metadata
  * Check and refresh OAuth token when expired
  * Create a card art caching layer on the server side when Card objects are created