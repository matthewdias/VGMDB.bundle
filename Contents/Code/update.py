from datetime import datetime
from vgmdb import get_album, get_artist

LANGUAGES = {
    'English': 'en',
    'Japanese': 'ja',
    'Romanized Japanese': 'ja-latn',
    'Original': 'og'
}

TRACK_LANGUAGES = {
    'English': 'English',
    'Japanese': 'Japanese',
    'Romanized Japanese': 'Romaji',
    'Original': 'English'
}

def update_album(metadata, media, force):
    result = get_album(metadata.id)

    if metadata.genres is None or force:
        metadata.genres = result['categories']

    if metadata.collections is None or force:
        lang = lang_pref()
        if lang == 'og':
            lang = 'en'
        metadata.collections = map(lambda p: p['names'][lang], result['products'])

    if metadata.rating is None or force:
        metadata.rating = float(result['rating'])

    if metadata.original_title is None or force:
        metadata.original_title = result['name']

    if metadata.title is None or force:
        lang = lang_pref()
        if lang == 'og':
            metadata.title = result['name']
        else:
            metadata.title = result['names'][lang]

    if metadata.summary is None or force:
        metadata.summary = result['notes']

    if metadata.studio is None or force:
        lang = lang_pref()
        if lang == 'og':
            lang = 'en'
        metadata.studio = result['publisher']['names'][lang]

    if metadata.originally_available_at is None or force:
        split = map(lambda s: int(s), result['release_date'].split('-'))
        release_date = datetime(split[0], split[1], split[2])
        metadata.originally_available_at = release_date

    if metadata.posters is None or force:
        get_poster(metadata, result['picture_small'], result['picture_full'])
        for poster in result['covers']:
            if poster['full'] != result['picture_full']:
                get_poster(metadata, poster['thumb'], poster['full'])

    token = Prefs['token']
    if token is not None:
        tracks = {}
        discs = []
        for track in media.children:
            request = HTTP.Request(
                'http://localhost:32400/library/metadata/' + track.id,
                headers = { 'X-Plex-Token': token, 'Accept': 'application/json' }
            )
            try:
                request.load()
                cont = JSON.ObjectFromString(request.content)
                disc = cont['MediaContainer']['Metadata'][0]['parentIndex']
                if disc not in tracks:
                    tracks[disc] = []
                    discs.append(disc)
                tracks[disc].append(track.index)
            except:
                Log.Error('Error getting track data')

        # Multi-disc track naming seems bugged
        # https://forums.plex.tv/t/how-to-get-disc-number-for-tracks/331052

        # Log.Debug(tracks)
        # lang = TRACK_LANGUAGES[Prefs['language']]
        # counter = 1
        # discs.sort()
        # for disc_num in discs:
        #     disc_tracks = tracks[disc_num]
        #     disc = result['discs'][disc_num - 1]
        #     for track_index in disc_tracks:
        #         track_index = int(track_index)
        #         if track_index <= len(disc['tracks']):
        #             track = disc['tracks'][track_index - 1]
        #             Log.Debug('Setting track ' + str(counter) + ' Disc ' + str(disc_num) + ' disctrack ' + str(track_index))
        #             track_name = pick_track_name(track['names'], lang)
        #             if track_name is not None:
        #                 metadata.tracks[counter].name = track_name
        #         counter = counter + 1

        # For now, only name tracks for single-disc albums

        if len(discs) == 1:
            lang = TRACK_LANGUAGES[Prefs['language']]
            disc_tracks = tracks[1]
            disc = result['discs'][0]
            for track_index in disc_tracks:
                track_index = int(track_index)
                if track_index <= len(disc['tracks']):
                    track = disc['tracks'][track_index - 1]
                    track_name = pick_track_name(track['names'], lang)
                    if track_name is not None:
                        metadata.tracks[track_index].name = track_name

def update_artist(metadata, media, force):
    result = get_artist(metadata.id)

    if metadata.rating is None or force:
        metadata.rating = float(result['info']['Weighted album rating'].replace('/10', ''))

    if metadata.title is None or force:
        metadata.title = result['name']

    if metadata.summary is None or force:
        metadata.summary = result['notes']

    if (metadata.posters is None or force) and result['picture_full'] is not None:
        get_poster(metadata, result['picture_small'], result['picture_full'])

def lang_pref():
    lang = Prefs['language']
    return LANGUAGES[lang]

def pick_track_name(track_names, lang):
    if lang in track_names:
        return track_names[lang]
    elif 'English' in track_names:
        return track_names['English']
    elif 'Romaji' in track_names:
        return track_names['Romaji']
    elif 'Japanese' in track_names:
        return track_names['Japanese']

def get_poster(metadata, thumb, full):
    try:
        thumbnail = Proxy.Preview(HTTP.Request(
            thumb, immediate = True
        ).content)
        metadata.posters[full] = thumbnail
    except:
        Log.Error('Error loading poster')
