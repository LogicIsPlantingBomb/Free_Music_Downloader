import requests
import re
import json
import os
import time
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

def search_songs(query):
    """Search JioSaavn and return results"""
    url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&query={quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://www.jiosaavn.com/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = json.loads(response.text.strip('()'))
        return data.get('songs', {}).get('data', [])
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def search_artists(query):
    """Search JioSaavn for artists and return results"""
    url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&query={quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://www.jiosaavn.com/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = json.loads(response.text.strip('()'))
        return data.get('artists', {}).get('data', [])
    except Exception as e:
        print(f"Artist search error: {str(e)}")
        return []

def search_albums(query):
    """Search JioSaavn for albums/movies and return results"""
    url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&query={quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://www.jiosaavn.com/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = json.loads(response.text.strip('()'))
        return data.get('albums', {}).get('data', [])
    except Exception as e:
        print(f"Album search error: {str(e)}")
        return []

def get_artist_songs(artist_id, limit=50):
    """Get songs by an artist"""
    url = f"https://www.jiosaavn.com/api.php?__call=artist.getArtistMoreSong&artistId={artist_id}&page=1&n={limit}&category=&sort_order=desc&includeMetaTags=0&ctx=wap6dot0&_format=json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://www.jiosaavn.com/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = json.loads(response.text.strip('()'))
        return data.get('songs', [])
    except Exception as e:
        print(f"Error getting artist songs: {str(e)}")
        return []

def get_album_songs(album_id):
    """Get songs from an album/movie"""
    url = f"https://www.jiosaavn.com/api.php?__call=content.getAlbumDetails&albumid={album_id}&_format=json"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://www.jiosaavn.com/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = json.loads(response.text.strip('()'))
        return data.get('songs', [])
    except Exception as e:
        print(f"Error getting album songs: {str(e)}")
        return []

def get_download_url(song_id):
    """Get direct download URL for a song"""
    url = f"https://www.jiosaavn.com/api.php?__call=song.getDetails&_format=json&pids={song_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://www.jiosaavn.com/'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response_text = response.text.strip('()')
        song_data = json.loads(response_text)[song_id]
        
        # Extract encrypted media URL
        encrypted_url = song_data.get('encrypted_media_url')
        if not encrypted_url:
            return None
            
        # Decrypt the URL
        decrypt_url = f"https://www.jiosaavn.com/api.php?__call=song.generateAuthToken&url={encrypted_url}&bitrate=320&_format=json"
        decrypt_response = requests.get(decrypt_url, headers=headers)
        decrypt_data = json.loads(decrypt_response.text.strip('()'))
        
        # Get the actual MP4 URL
        media_url = decrypt_data.get('auth_url')
        if not media_url:
            # Fallback to direct extraction from network analysis pattern
            if 'media_preview_url' in song_data:
                media_url = song_data['media_preview_url'].replace('preview', 'aac')
                # Replace with higher quality if available
                for quality in ['320', '160', '96']:
                    test_url = media_url.replace('_96.mp4', f'_{quality}.mp4')
                    if requests.head(test_url, headers=headers).status_code == 200:
                        return test_url
        
        return media_url
    except Exception as e:
        print(f"Error getting download URL: {str(e)}")
        # Try direct method from network pattern
        try:
            song_details_url = f"https://www.jiosaavn.com/api.php?__call=webapi.get&token={song_id}&type=song&_format=json"
            song_response = requests.get(song_details_url, headers=headers)
            song_json = json.loads(song_response.text.strip('()'))
            
            # Extract song details from the response
            song_info = song_json.get('songs', [])[0]
            encrypted_media_url = song_info.get('encrypted_media_url')
            
            if encrypted_media_url:
                decrypt_api = f"https://www.jiosaavn.com/api.php?__call=song.generateAuthToken&url={encrypted_media_url}&bitrate=320&_format=json"
                decrypt_response = requests.get(decrypt_api, headers=headers)
                decrypt_data = json.loads(decrypt_response.text.strip('()'))
                return decrypt_data.get('auth_url')
            
            # Last resort - try to construct URL based on ID pattern
            song_id_clean = song_id.split('_')[0] if '_' in song_id else song_id
            for quality in ['320', '160', '96']:
                constructed_url = f"https://aac.saavncdn.com/songs/{song_id_clean}_{quality}.mp4"
                if requests.head(constructed_url, headers=headers).status_code == 200:
                    return constructed_url
            
        except Exception as inner_e:
            print(f"Fallback method also failed: {str(inner_e)}")
        
        return None

def download_song(url, filename, show_progress=True, folder="downloads"):
    """Download song file"""
    try:
        # Create downloads folder if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # Clean filename and ensure it's valid
        filename = re.sub(r'[\\/*?:"<>|]', '', filename)
        # Keep the original mp4 extension as that's what JioSaavn provides
        if not filename.endswith('.mp4'):
            filename += '.mp4'
        
        # Create full path
        filepath = os.path.join(folder, filename)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Referer': 'https://www.jiosaavn.com/'
        }
        
        if show_progress:
            print(f"Downloading {filename}...")
        
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        f.write(chunk)
                        
                        # Print progress
                        if show_progress:
                            done = int(50 * downloaded / total_size) if total_size > 0 else 0
                            progress = f"[{'=' * done}{' ' * (50 - done)}] {downloaded}/{total_size} bytes"
                            print(f"\r{progress}", end='', flush=True)
                        
        if show_progress:
            print(f"\n✅ Downloaded: {filename}")
        else:
            print(f"✅ Downloaded: {filename}")
            
        return filepath  # Return the filepath for playback
    except Exception as e:
        print(f"\n❌ Download failed for {filename}: {str(e)}")
        return False

def download_by_direct_url(url, filename=None, folder="downloads"):
    """Download song using a direct URL"""
    try:
        if not filename:
            # Extract filename from URL but keep the mp4 extension
            filename = url.split('/')[-1]
            # If there's a query string, remove it
            if '?' in filename:
                filename = filename.split('?')[0]
        
        return download_song(url, filename, folder=folder)
    except Exception as e:
        print(f"Direct download error: {str(e)}")
        return False

def download_multiple_songs(song_ids, folder="downloads"):
    """Download multiple songs in parallel"""
    results = []
    # Define a helper function for ThreadPoolExecutor
    def download_single(song_id):
        try:
            print(f"Processing song ID: {song_id}")
            download_url = get_download_url(song_id)
            if not download_url:
                print(f"❌ Couldn't get download URL for song ID: {song_id}")
                return False
                
            # Get song details to use as filename
            url = f"https://www.jiosaavn.com/api.php?__call=song.getDetails&_format=json&pids={song_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Referer': 'https://www.jiosaavn.com/'
            }
            
            response = requests.get(url, headers=headers)
            song_data = json.loads(response.text.strip('()'))[song_id]
            title = song_data.get('title', 'Unknown')
            artist = song_data.get('primary_artists', song_data.get('singers', 'Unknown'))
            filename = f"{title} - {artist}"
            
            # Download with minimal progress display
            result = download_song(download_url, filename, show_progress=False, folder=folder)
            return result
        except Exception as e:
            print(f"Error processing song {song_id}: {str(e)}")
            return False
    
    # Use ThreadPoolExecutor for parallel downloads
    print(f"\nDownloading {len(song_ids)} songs...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(download_single, song_ids))
    
    successful = sum(1 for r in results if r)
    print(f"\n✅ Successfully downloaded {successful} out of {len(song_ids)} songs")
    return results

def play_song(filename):
    """Play the downloaded song using an appropriate media player"""
    try:
        import platform
        import subprocess
        
        system = platform.system()
        
        print(f"Attempting to play {filename} using your system's media player...")
        
        if system == "Linux":
            # Try different Linux media players
            players = ["xdg-open", "audacious", "vlc", "mplayer", "mpv"]
            
            for player in players:
                try:
                    subprocess.run(["which", player], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"Playing with {player}...")
                    subprocess.Popen([player, filename])
                    return True
                except subprocess.CalledProcessError:
                    continue
            
            print("Could not find a suitable media player. Please install one of: audacious, vlc, mplayer, mpv")
            return False
            
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", filename])
            return True
            
        elif system == "Windows":
            subprocess.Popen(["start", filename], shell=True)
            return True
            
        else:
            print(f"Unsupported platform: {system}")
            return False
            
    except Exception as e:
        print(f"Failed to play the song: {str(e)}")
        return False


def main():
    print("🎵 JioSaavn Advanced Downloader")
    print("--------------------------------")
    
    # Create downloads folder
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    while True:
        print("\nOptions:")
        print("1. Search and download a song")
        print("2. Download multiple songs")
        print("3. Download all songs by an artist")
        print("4. Download all songs from a movie/album")
        print("5. Download with direct URL")
        print("6. Quit")
        
        try:
            choice = int(input("\nEnter your choice (1-6): "))
            
            if choice == 1:
                query = input("\nEnter song name: ").strip()
                if not query:
                    print("Please enter a song name")
                    continue
                    
                print("Searching for songs...")
                songs = search_songs(query)
                if not songs:
                    print("No songs found")
                    continue
                    
                print("\nSearch Results:")
                for i, song in enumerate(songs[:10], 1):
                    title = song.get('title', 'Unknown')
                    artist = song.get('primary_artists', song.get('singers', 'Unknown'))
                    print(f"{i}. {title} - {artist}")
                    
                try:
                    song_choice = int(input("\nSelect song (1-10) or 0 to cancel: "))
                    if song_choice == 0:
                        continue
                        
                    selected = songs[song_choice-1]
                    print(f"\nSelected: {selected['title']} by {selected.get('primary_artists', selected.get('singers', 'Unknown'))}")
                    print("Fetching download URL...")
                    
                    download_url = get_download_url(selected['id'])
                    if not download_url:
                        print("❌ Couldn't get download URL")
                        continue
                        
                    filename = f"{selected['title']} - {selected.get('primary_artists', selected.get('singers', 'Unknown'))}"
                    downloaded_file = download_song(download_url, filename, folder="downloads")
                    
                    if downloaded_file:
                        play_choice = input("\nDo you want to play this song now? (y/n): ").strip().lower()
                        if play_choice == 'y':
                            play_song(downloaded_file)
                    
                except (ValueError, IndexError):
                    print("Invalid selection")
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            elif choice == 2:
                # Download multiple songs
                query = input("\nEnter search term for songs: ").strip()
                if not query:
                    print("Please enter a search term")
                    continue
                
                print("Searching for songs...")
                songs = search_songs(query)
                if not songs:
                    print("No songs found")
                    continue
                
                print("\nSearch Results:")
                for i, song in enumerate(songs[:15], 1):
                    title = song.get('title', 'Unknown')
                    artist = song.get('primary_artists', song.get('singers', 'Unknown'))
                    print(f"{i}. {title} - {artist}")
                
                selections = input("\nSelect songs (comma-separated numbers, e.g., 1,3,5) or 'all' for all: ").strip()
                if selections.lower() == 'all':
                    selected_indices = range(len(songs[:15]))
                else:
                    try:
                        selected_indices = [int(x.strip()) - 1 for x in selections.split(',')]
                    except ValueError:
                        print("Invalid input format")
                        continue
                
                try:
                    selected_songs = [songs[i] for i in selected_indices if 0 <= i < len(songs)]
                    if not selected_songs:
                        print("No valid songs selected")
                        continue
                    
                    print(f"\nSelected {len(selected_songs)} songs for download")
                    
                    # Create a custom folder for this batch
                    folder_name = input("\nEnter folder name (leave blank for default): ").strip()
                    if not folder_name:
                        folder_name = f"downloads/{query.replace(' ', '_')}_{int(time.time())}"
                    else:
                        folder_name = f"downloads/{folder_name}"
                    
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    
                    # Extract song IDs and download
                    song_ids = [song['id'] for song in selected_songs]
                    download_multiple_songs(song_ids, folder=folder_name)
                    
                except Exception as e:
                    print(f"Error: {str(e)}")
            
            elif choice == 3:
                # Download all songs by an artist
                artist_query = input("\nEnter artist name: ").strip()
                if not artist_query:
                    print("Please enter an artist name")
                    continue
                
                print("Searching for artists...")
                artists = search_artists(artist_query)
                if not artists:
                    print("No artists found")
                    continue
                
                print("\nSearch Results:")
                for i, artist in enumerate(artists[:5], 1):
                    print(f"{i}. {artist.get('name', 'Unknown Artist')}")
                
                try:
                    artist_choice = int(input("\nSelect artist (1-5) or 0 to cancel: "))
                    if artist_choice == 0:
                        continue
                    
                    selected_artist = artists[artist_choice-1]
                    artist_name = selected_artist.get('name', 'Unknown')
                    artist_id = selected_artist.get('id', '')
                    
                    print(f"\nSelected: {artist_name}")
                    print("Fetching artist songs...")
                    
                    # Get songs by the artist
                    limit = input("Enter maximum number of songs to download (default 20): ").strip()
                    try:
                        limit = int(limit) if limit else 20
                    except ValueError:
                        limit = 20
                    
                    artist_songs = get_artist_songs(artist_id, limit=limit)
                    if not artist_songs:
                        print("No songs found for this artist")
                        continue
                    
                    print(f"\nFound {len(artist_songs)} songs by {artist_name}")
                    
                    # Create folder for artist
                    folder_name = f"downloads/{artist_name.replace(' ', '_')}"
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    
                    # Extract song IDs
                    song_ids = [song['id'] for song in artist_songs]
                    
                    # Ask for confirmation
                    confirm = input(f"Download {len(song_ids)} songs by {artist_name}? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                    
                    # Download all songs
                    download_multiple_songs(song_ids, folder=folder_name)
                    
                except (ValueError, IndexError):
                    print("Invalid selection")
                except Exception as e:
                    print(f"Error: {str(e)}")
            
            elif choice == 4:
                # Download all songs from a movie/album
                album_query = input("\nEnter movie/album name: ").strip()
                if not album_query:
                    print("Please enter a movie/album name")
                    continue
                
                print("Searching for albums...")
                albums = search_albums(album_query)
                if not albums:
                    print("No albums found")
                    continue
                
                print("\nSearch Results:")
                for i, album in enumerate(albums[:5], 1):
                    album_name = album.get('title', 'Unknown Album')
                    artist = album.get('music', album.get('primary_artists', 'Unknown Artist'))
                    print(f"{i}. {album_name} - {artist}")
                
                try:
                    album_choice = int(input("\nSelect album (1-5) or 0 to cancel: "))
                    if album_choice == 0:
                        continue
                    
                    selected_album = albums[album_choice-1]
                    album_name = selected_album.get('title', 'Unknown Album')
                    album_id = selected_album.get('id', '')
                    
                    print(f"\nSelected: {album_name}")
                    print("Fetching album songs...")
                    
                    # Get songs from the album
                    album_songs = get_album_songs(album_id)
                    if not album_songs:
                        print("No songs found in this album")
                        continue
                    
                    print(f"\nFound {len(album_songs)} songs in {album_name}")
                    
                    # Create folder for album
                    folder_name = f"downloads/{album_name.replace(' ', '_')}"
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    
                    # Extract song IDs
                    song_ids = [song['id'] for song in album_songs]
                    
                    # Ask for confirmation
                    confirm = input(f"Download all {len(song_ids)} songs from {album_name}? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                    
                    # Download all songs
                    download_multiple_songs(song_ids, folder=folder_name)
                    
                except (ValueError, IndexError):
                    print("Invalid selection")
                except Exception as e:
                    print(f"Error: {str(e)}")
                
            elif choice == 5:
                url = input("\nEnter direct JioSaavn MP4 URL: ").strip()
                if not url or not url.startswith('http'):
                    print("Please enter a valid URL")
                    continue
                    
                custom_filename = input("Enter custom filename (leave blank for auto): ").strip()
                downloaded_file = download_by_direct_url(url, custom_filename if custom_filename else None, folder="downloads")
                
                if downloaded_file:
                    play_choice = input("\nDo you want to play this song now? (y/n): ").strip().lower()
                    if play_choice == 'y':
                        play_song(downloaded_file)
                
            elif choice == 6:
                print("\nThank you for using Dhruv Bhardwaj's Advanced Downloader! Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
                
        except ValueError:
            print("Please enter a number")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
