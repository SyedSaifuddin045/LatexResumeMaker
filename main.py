import webview
import os
from api import Bridge
import sys
from utils import resource_path

def main():
    api = Bridge()
    
    # Path to HTML
    # We assume 'gui' is relative to this script
    index_path = resource_path('gui/index.html')
    
    if not os.path.exists(index_path):
        print(f"Error: GUI not found at {index_path}")
        return

    # Create Window
    webview.create_window(
        'ATS Resume Genius', 
        url=index_path,
        js_api=api,
        width=1200,
        height=800,
        resizable=True,
        background_color='#0f172a' # Matches CSS
    )
    
    # Start loop
    webview.start(debug=False)

if __name__ == '__main__':
    main()
