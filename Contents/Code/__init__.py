from search import search_albums, search_artists
from update import update_album, update_artist

EN = Locale.Language.English

def Start():
    HTTP.CacheTime = CACHE_1DAY

class VGMDBAlbum(Agent.Album):
    name = 'VGMDB'
    languages = [ EN ]
    primary_provider = True
    fallback_agent = False
    accepts_from = None
    contributes_to = None

    def search(self, results, media, lang, manual):
        search_albums(results, media, lang)

    def update(self, metadata, media, lang, force):
        update_album(metadata, media, force)

class VGMDBArtist(Agent.Artist):
    name = 'VGMDB'
    languages = [ EN ]
    primary_provider = True
    fallback_agent = False
    accepts_from = None
    contributes_to = None

    def search(self, results, media, lang, manual):
        search_artists(results, media, lang)

    def update(self, metadata, media, lang, force):
        update_artist(metadata, media, force)
