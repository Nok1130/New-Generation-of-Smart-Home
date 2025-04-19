import spotipy 
import webbrowser

username = ''
clientID = ''
clientSecret = ''
redirect_uri = ''

def play_song(song_name):
    oauth_object = spotipy.SpotifyOAuth(clientID, clientSecret, redirect_uri) 
    token_dict = oauth_object.get_access_token() 
    token = token_dict['access_token'] 
    spotifyObject = spotipy.Spotify(auth=token) 
    user_name = spotifyObject.current_user() 
    search_song = song_name
    results = spotifyObject.search(search_song, 1, 0, "track") 
    songs_dict = results['tracks'] 
    song_items = songs_dict['items'] 
    song = song_items[0]['external_urls']['spotify'] 

    webbrowser.open(song) 