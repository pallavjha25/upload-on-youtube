import os
import time
import logging
from pathlib import Path
from typing import List, Set
from dataclasses import dataclass
from abc import ABC, abstractmethod

# YouTube API imports
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class VideoFile:
    """Represents a video file with its metadata"""
    path: Path
    name: str
    size: int
    modified_time: float
    
    def __post_init__(self):
        self.extension = self.path.suffix.lower()
    
    def is_valid_video(self) -> bool:
        """Check if the file has a valid video extension"""
        valid_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        return self.extension in valid_extensions
    
    def get_file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.size / (1024 * 1024)


class FileMonitor(ABC):
    """Abstract base class for file monitoring"""
    
    @abstractmethod
    def scan_directory(self) -> List[VideoFile]:
        pass
    
    @abstractmethod
    def is_new_file(self, video_file: VideoFile) -> bool:
        pass


class VideoFileMonitor(FileMonitor):
    """Monitors a directory for video files"""
    
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.processed_files: Set[str] = set()
        
        if not self.folder_path.exists():
            raise ValueError(f"Folder path does not exist: {folder_path}")
        
        if not self.folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")
    
    def scan_directory(self) -> List[VideoFile]:
        """Scan directory for video files"""
        video_files = []
        
        try:
            for file_path in self.folder_path.iterdir():
                if file_path.is_file():
                    stat_info = file_path.stat()
                    video_file = VideoFile(
                        path=file_path,
                        name=file_path.name,
                        size=stat_info.st_size,
                        modified_time=stat_info.st_mtime
                    )
                    
                    if video_file.is_valid_video():
                        video_files.append(video_file)
        
        except PermissionError:
            logger.error(f"Permission denied accessing folder: {self.folder_path}")
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
        
        return video_files
    
    def is_new_file(self, video_file: VideoFile) -> bool:
        """Check if this is a new file we haven't processed"""
        file_key = f"{video_file.name}_{video_file.modified_time}"
        return file_key not in self.processed_files
    
    def mark_as_processed(self, video_file: VideoFile):
        """Mark file as processed"""
        file_key = f"{video_file.name}_{video_file.modified_time}"
        self.processed_files.add(file_key)


class YouTubeUploader:
    """Handles YouTube API authentication and video uploads"""
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    current_dir = os.getcwd()
                    print(f"Credentials file not found at: {os.path.abspath(self.credentials_file)}")
                    print(f"Current working directory: {current_dir}")
                    print("Please ensure credentials.json is in the same directory as this script, check file name or extenstion.")
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download it from Google Cloud Console and place it in the current directory"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.youtube_service = build('youtube', 'v3', credentials=creds)
        logger.info("YouTube API authentication successful")
    
    def upload_video(self, video_file: VideoFile, title: str = None, 
                    description: str = "", tags: List[str] = None, 
                    privacy_status: str = "private") -> bool:
        """Upload video to YouTube"""
        
        if not self.youtube_service:
            logger.error("YouTube service not authenticated")
            return False
        
        if title is None:
            title = video_file.name
        
        if tags is None:
            tags = []
        
        # Video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '22'  # People & Blogs category
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(
            str(video_file.path),
            chunksize=-1,
            resumable=True
        )
        
        try:
            logger.info(f"Starting upload for: {video_file.name}")
            
            # Execute upload
            upload_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = upload_request.execute()
            
            if response:
                video_id = response.get('id')
                logger.info(f"Upload successful! Video ID: {video_id}")
                logger.info(f"Video URL: https://www.youtube.com/watch?v={video_id}")
                return True
            
        except HttpError as e:
            logger.error(f"HTTP error during upload: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
        
        return False


class UserInterface:
    """Handles user interactions"""
    
    @staticmethod
    def get_user_confirmation(video_file: VideoFile) -> bool:
        """Ask user if they want to upload the video"""
        print(f"\n{'='*60}")
        print(f"Video file found: {video_file.name}")
        print(f"Size: {video_file.get_file_size_mb():.2f} MB")
        print(f"Path: {video_file.path}")
        print(f"{'='*60}")
        
        while True:
            response = input("Do you want to upload this video to YouTube? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    @staticmethod
    def get_video_details(video_file: VideoFile) -> dict:
        """Get video details from user"""
        print(f"\nEnter details for: {video_file.name}")
        
        title = input(f"Title (press Enter for default: {video_file.name}): ").strip()
        if not title:
            title = video_file.name
        
        description = input("Description (optional): ").strip()
        
        tags_input = input("Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []
        
        print("\nPrivacy options:")
        print("1. Private")
        print("2. Unlisted")
        print("3. Public")
        
        while True:
            privacy_choice = input("Choose privacy setting (1-3, default: 1): ").strip()
            if privacy_choice == '1' or privacy_choice == '':
                privacy_status = 'private'
                break
            elif privacy_choice == '2':
                privacy_status = 'unlisted'
                break
            elif privacy_choice == '3':
                privacy_status = 'public'
                break
            else:
                print("Please enter 1, 2, or 3.")
        
        return {
            'title': title,
            'description': description,
            'tags': tags,
            'privacy_status': privacy_status
        }


class VideoMonitorApp:
    """Main application class that orchestrates the video monitoring and uploading"""
    
    def __init__(self, folder_path: str, check_interval: int = 60):
        self.folder_path = folder_path
        self.check_interval = check_interval
        self.file_monitor = VideoFileMonitor(folder_path)
        self.uploader = None
        self.ui = UserInterface()
        self.running = False
    
    def initialize_uploader(self):
        """Initialize YouTube uploader (lazy loading)"""
        if self.uploader is None:
            try:
                self.uploader = YouTubeUploader()
            except Exception as e:
                logger.error(f"Failed to initialize YouTube uploader: {e}")
                return False
        return True
    
    def process_video_files(self, video_files: List[VideoFile]):
        """Process each video file and ask user for upload confirmation"""
        if not video_files:
            return
        
        new_files = [vf for vf in video_files if self.file_monitor.is_new_file(vf)]
        
        if not new_files:
            return
        
        print(f"\nFound {len(new_files)} new video file(s)!")
        
        for video_file in new_files:
            try:
                if self.ui.get_user_confirmation(video_file):
                    # Initialize uploader only when needed
                    if not self.initialize_uploader():
                        print("Failed to initialize YouTube uploader. Skipping upload.")
                        continue
                    
                    # Get video details from user
                    video_details = self.ui.get_video_details(video_file)
                    
                    # Upload video
                    success = self.uploader.upload_video(
                        video_file,
                        title=video_details['title'],
                        description=video_details['description'],
                        tags=video_details['tags'],
                        privacy_status=video_details['privacy_status']
                    )
                    
                    if success:
                        print(f"✅ Successfully uploaded: {video_file.name}")
                    else:
                        print(f"❌ Failed to upload: {video_file.name}")
                else:
                    print(f"⏭️ Skipped: {video_file.name}")
                
                # Mark as processed regardless of upload success
                self.file_monitor.mark_as_processed(video_file)
                
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break
            except Exception as e:
                logger.error(f"Error processing {video_file.name}: {e}")
    
    def run_single_scan(self):
        """Run a single scan of the directory"""
        logger.info(f"Scanning directory: {self.folder_path}")
        video_files = self.file_monitor.scan_directory()
        self.process_video_files(video_files)
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring"""
        self.running = True
        print(f"Starting continuous monitoring of: {self.folder_path}")
        print(f"Check interval: {self.check_interval} seconds")
        print("Press Ctrl+C to stop monitoring\n")
        
        try:
            while self.running:
                self.run_single_scan()
                time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            print("\nStopping video monitor...")
            self.running = False
        except Exception as e:
            logger.error(f"Error in continuous monitoring: {e}")
            self.running = False
    
    def stop(self):
        """Stop the monitoring"""
        self.running = False


def main():
    """Main function to run the application"""
    print("YouTube Video Monitor and Uploader")
    print("=" * 40)
    
    # Get folder path from user
    folder_path = input("Enter the folder path to monitor: ").strip()
    
    if not folder_path:
        print("No folder path provided. Exiting.")
        return
    
    try:
        # Create application instance
        app = VideoMonitorApp(folder_path)
        
        # Choose monitoring mode
        print("\nChoose monitoring mode:")
        print("1. Single scan")
        print("2. Continuous monitoring")
        
        while True:
            choice = input("Enter choice (1 or 2): ").strip()
            if choice == '1':
                app.run_single_scan()
                break
            elif choice == '2':
                interval = input("Enter check interval in seconds (default: 60): ").strip()
                if interval.isdigit():
                    app.check_interval = int(interval)
                app.run_continuous_monitoring()
                break
            else:
                print("Please enter 1 or 2.")
    
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()