# Free Music Downloader(weekend side project)

A Python script to search, download, and play songs from JioSaavn without needing to manually extract URLs from the browser.(Just a JioSaavan bug... its working until they fix it)

## Screenshot
![Screenshot_2025-05-04_11-52-24](https://github.com/user-attachments/assets/24278023-db64-432a-b918-e69dba0b1cd9)


## Features

- 🔍 Search for songs directly within the script
- ⬇️ Download songs in high quality (320kbps when available)
- ▶️ Automatically play downloaded songs
- 📲 Support for direct URL downloads
- 📊 Real-time download progress display
- 💻 Cross-platform compatibility (Windows, macOS, Linux)

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - requests
  - json
  - re
  - os

## Installation

1. Clone this repository or download the `jiosaavn_downloader.py` file

```bash
git clone https://github.com/yourusername/jiosaavn-downloader.git
# or simply download the jiosaavn_downloader.py file
```

2. Install the required packages:

```bash
pip install requests
```

## Usage

### Running the Script

Simply run the Python script:

```bash
python jiosaavn_downloader.py
```

### Main Menu Options

The script provides three options:

1. **Search and download a song**
   - Enter song name
   - Select from search results
   - Download and optionally play the song

2. **Download with direct URL**
   - Paste a direct JioSaavn MP4 URL
   - Optionally provide a custom filename
   - Download and optionally play the song

3. **Quit**
   - Exit the application

### Playing Songs

The script can automatically play downloaded songs using your system's media players:

- **Linux**: Tries xdg-open, audacious, vlc, mplayer, or mpv
- **macOS**: Uses the default "open" command
- **Windows**: Uses the default "start" command

## Examples

### Example 1: Search and Download

```
🎵 JioSaavn Automatic Downloader
--------------------------------

Options:
1. Search and download a song
2. Download with direct URL
3. Quit

Enter your choice (1-3): 1

Enter song name: Tum Hi Ho

Searching for songs...

Search Results:
1. Tum Hi Ho - Arijit Singh
2. Tum Hi Ho (Acoustic) - Arijit Singh
3. Tum Hi Ho (From "Aashiqui 2") - Arijit Singh
4. Tum Hi Ho Female Version - Samira Koppikar
5. Tum Hi Ho (Traditional) - Varun Jain

Select song (1-5) or 0 to cancel: 1

Selected: Tum Hi Ho by Arijit Singh
Fetching download URL...
Downloading Tum Hi Ho - Arijit Singh.mp4...
[==================================================] 4218379/4218379 bytes
✅ Downloaded: Tum Hi Ho - Arijit Singh.mp4

Do you want to play this song now? (y/n): y
Playing with audacious...
```

### Example 2: Direct URL Download

```
Options:
1. Search and download a song
2. Download with direct URL
3. Quit

Enter your choice (1-3): 2

Enter direct JioSaavn MP4 URL: https://aac.saavncdn.com/430/5c5ea5cc00e3bff45616013226f376fe_160.mp4
Enter custom filename (leave blank for auto): 

Downloading 5c5ea5cc00e3bff45616013226f376fe_160.mp4...
[==================================================] 4218379/4218379 bytes
✅ Downloaded: 5c5ea5cc00e3bff45616013226f376fe_160.mp4

Do you want to play this song now? (y/n): y
Playing with audacious...
```

## Troubleshooting

### Common Issues:

- **"No songs found"**
  - Try a different spelling or include artist name
  - Example: "tum hi ho arijit" instead of just "tum hi ho"

- **"Couldn't get download URL"**
  - JioSaavn's API might have changed or is temporarily unavailable
  - Try using a direct URL from the Network tab in browser developer tools

- **"Failed to play the song"**
  - Ensure you have a compatible media player installed
  - For Linux users: install audacious, vlc, mplayer, or mpv

### Media Player Not Found (Linux)

If the script can't find a suitable media player on Linux, install one of these:

```bash
# Install Audacious
sudo apt-get install audacious

# Or install VLC
sudo apt-get install vlc

# Or install MPV
sudo apt-get install mpv
```

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and artists' rights by using the downloaded content legally. JioSaavn's terms of service may prohibit automated downloading. Use at your own risk.

## Developed with ❤️ BY DHRUV BHARDWAJ
