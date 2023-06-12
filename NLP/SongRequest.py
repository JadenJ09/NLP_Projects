# import sys
# import getpass
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# import pandas as pd

# # Set up Spotify credentials
# client_credentials_manager = SpotifyClientCredentials(client_id='5bfef1fd889641d08e029c22f6e5d899', client_secret='92dafad372dc4145b05cb13b7f29df2b')
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# # Search for tracks by multiple artists
# artists = ['Taylor Swift', 'Ed Sheeran', 'Adele']
# results = sp.search(q='artist:' + ','.join(artists), type='track', limit=50)

# # Extract information about the tracks
# tracks = []
# for track in results['tracks']['items']:
#     track_name = track['name']
#     artist_names = [artist['name'] for artist in track['artists']]
#     album_name = track['album']['name']
#     release_year = track['album']['release_date'][:4]
#     popularity = track['popularity']
#     tracks.append({'track_name': track_name, 'artist_names': artist_names, 'album_name': album_name, 'release_year': release_year, 'popularity': popularity})

# # Print the tracks
# for track in tracks:
#     print(track['track_name'], ' - '.join(track['artist_names']), track['album_name'], track['release_year'], track['popularity'])

# # Convert the data to a pandas DataFrame and save to a CSV file
# songs_df = pd.DataFrame(tracks)
# songs_df.to_csv('songs.csv', index=False)

import pandas as pd
import datetime
from textblob import TextBlob
import googletrans
from googletrans import Translator
import spacy
import en_core_web_sm
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import youtube_dl

# Load the CSV data into a pandas DataFrame
df = pd.read_csv('song_requests.csv')

# Convert the event date data to a standard format
for i in range(len(df)):
    try:
        df.at[i, 'Event Date'] = datetime.datetime.strptime(df.at[i, 'Event Date'], '%d.%m.%Y').strftime('%Y-%m-%d')
    except:
        try:
            df.at[i, 'Event Date'] = datetime.datetime.strptime(df.at[i, 'Event Date'], '%dth %B %Y').strftime('%Y-%m-%d')
        except:
            try:
                df.at[i, 'Event Date'] = datetime.datetime.strptime(df.at[i, 'Event Date'], '%b %d %Y').strftime('%Y-%m-%d')
            except:
                try:
                    df.at[i, 'Event Date'] = datetime.datetime.strptime(df.at[i, 'Event Date'], '%b %d, %Y').strftime('%Y-%m-%d')
                except:
                    df.at[i, 'Event Date'] = ''

# Detect and translate the language of the event location data to English
translator = Translator()
for i in range(len(df)):
    try:
        location = TextBlob(df.at[i, 'Event Location']).translate(to='en')
        df.at[i, 'Event Location'] = translator.translate(str(location)).text
    except:
        df.at[i, 'Event Location'] = ''

# Correct the typo mistakes in the Artist and Song fields by matching them to real Music data from Spotify or YouTube Music
nlp = en_core_web_sm.load()
client_credentials_manager = SpotifyClientCredentials(client_id='YOUR_CLIENT_ID', client_secret='YOUR_CLIENT_SECRET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

for i in range(len(df)):
    artist = df.at[i, 'Artist']
    song = df.at[i, 'Song']
    try:
        result = sp.search(q='artist:' + artist + ' track:' + song, type='track')
        if len(result['tracks']['items']) > 0:
            df.at[i, 'Artist'] = result['tracks']['items'][0]['artists'][0]['name']
            df.at[i, 'Song'] = result['tracks']['items'][0]['name']
        else:
            doc1 = nlp(artist)
            doc2 = nlp(song)
            max_sim_artist = ''
            max_sim_song = ''
            max_similarity = -1
            for filename in os.listdir('music_data'):
                if filename.endswith('.txt'):
                    with open('music_data/' + filename) as file:
                        data = file.read()
                        doc3 = nlp(data)
                        sim_artist = doc1.similarity(doc3)
                        sim_song = doc2.similarity(doc3)
                        if sim_artist > max_similarity:
                            max_similarity = sim_artist
                            max_sim_artist = filename.split('.txt')[0]
                        if sim_song > max_similarity:
                            max_similarity = sim_song
                            max_sim_song = filename.split('.txt')[0]
            df.at[i, 'Artist'] = max_sim_artist
            df.at[i, 'Song'] = max_sim_song
    except:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'music_data/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                video = ydl.extract_info('ytsearch:' + artist + ' ' + song, download=False)['entries'][0]
                url = video['webpage_url']
                os.system('youtube-dl -x --audio-format mp3 --output "music_data/%(title)s.%(ext)s" ' + url)
                df.at[i, 'Artist'] = video['artist']
                df.at[i, 'Song'] = video['title']
            except:
                df.at[i, 'Artist'] = ''
                df.at[i, 'Song'] = ''
                
# Clean and preprocess the data
df = df.dropna()
df = df.drop_duplicates()
df = df.reset_index(drop=True)

# Visualize the data using matplotlib
import matplotlib.pyplot as plt
%matplotlib inline

artists = df['Artist'].value_counts().head(10)
songs = df['Song'].value_counts().head(10)

plt.subplot(1, 2, 1)
plt.barh(artists.index, artists.values)
plt.title('Top 10 Requested Artists')
plt.xlabel('Number of Requests')

plt.subplot(1, 2, 2)
plt.barh(songs.index, songs.values)
plt.title('Top 10 Requested Songs')
plt.xlabel('Number of Requests')

plt.subplots_adjust(wspace=0.5)

# Save the result in PDF format using ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

pdf = canvas.Canvas('song_requests_report.pdf', pagesize=letter)
pdf.setFont('Helvetica', 12)
pdf.drawString(30, 750, 'Top 10 Requested Artists')
for i, artist in enumerate(artists.index):
    pdf.drawString(30, 720 - i * 25, '{}. {}: {}'.format(i+1, artist, artists[artist]))
pdf.drawString(30, 500, 'Top 10 Requested Songs')
for i, song in enumerate(songs.index):
    pdf.drawString(30, 470 - i * 25, '{}. {}: {}'.format(i+1, song, songs[song]))
pdf.save()
