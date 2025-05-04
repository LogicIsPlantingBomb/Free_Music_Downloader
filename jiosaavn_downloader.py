import requests
import re
import json
import os
from urllib.parse import quote

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

def download_song(url, filename):
    """Download song file"""
    try:
        # Clean filename and ensure it's valid
        filename = re.sub(r'[\\/*?:"<>|]', '', filename)
        # Keep the original mp4 extension as that's what JioSaavn provides
        if not filename.endswith('.mp4'):
            filename += '.mp4'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Referer': 'https://www.jiosaavn.com/'
        }
        
        print(f"Downloading {filename}...")
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            with open(filename, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        f.write(chunk)
                        
                        # Print progress
                        done = int(50 * downloaded / total_size) if total_size > 0 else 0
                        progress = f"[{'=' * done}{' ' * (50 - done)}] {downloaded}/{total_size} bytes"
                        print(f"\r{progress}", end='', flush=True)
                        
        print(f"\n✅ Downloaded: {filename}")
        return filename  # Return the filename for playback
    except Exception as e:
        print(f"\n❌ Download failed: {str(e)}")
        return False

def download_by_direct_url(url, filename=None):
    """Download song using a direct URL"""
    try:
        if not filename:
            # Extract filename from URL but keep the mp4 extension
            filename = url.split('/')[-1]
            # If there's a query string, remove it
            if '?' in filename:
                filename = filename.split('?')[0]
        
        return download_song(url, filename)
    except Exception as e:
        print(f"Direct download error: {str(e)}")
        return False

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
    print("🎵 JioSaavn Automatic Downloader")
    print("--------------------------------")
    
    while True:
        print("\nOptions:")
        print("1. Search and download a song")
        print("2. Download with direct URL")
        print("3. Quit")
        
        try:
            choice = int(input("\nEnter your choice (1-3): "))
            
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
                for i, song in enumerate(songs[:5], 1):
                    title = song.get('title', 'Unknown')
                    artist = song.get('primary_artists', song.get('singers', 'Unknown'))
                    print(f"{i}. {title} - {artist}")
                    
                try:
                    song_choice = int(input("\nSelect song (1-5) or 0 to cancel: "))
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
                    downloaded_file = download_song(download_url, filename)
                    
                    if downloaded_file:
                        play_choice = input("\nDo you want to play this song now? (y/n): ").strip().lower()
                        if play_choice == 'y':
                            play_song(downloaded_file)
                    
                except (ValueError, IndexError):
                    print("Invalid selection")
                except Exception as e:
                    print(f"Error: {str(e)}")
                    
            elif choice == 2:
                url = input("\nEnter direct JioSaavn MP4 URL: ").strip()
                if not url or not url.startswith('http'):
                    print("Please enter a valid URL")
                    continue
                    
                custom_filename = input("Enter custom filename (leave blank for auto): ").strip()
                downloaded_file = download_by_direct_url(url, custom_filename if custom_filename else None)
                
                if downloaded_file:
                    play_choice = input("\nDo you want to play this song now? (y/n): ").strip().lower()
                    if play_choice == 'y':
                        play_song(downloaded_file)
                
            elif choice == 3:
                print("\nThank you for using JioSaavn Downloader! Goodbye!")
                break
                
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
        except ValueError:
            print("Please enter a number")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
