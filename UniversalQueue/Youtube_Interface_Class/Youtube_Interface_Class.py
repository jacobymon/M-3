"""
This module implements the YouTube Interface class for handling YouTube playback
similar to the Spotify Interface Class
"""
"""
This module implements the YouTube Interface class for handling YouTube playback
similar to the Spotify Interface Class
"""
import logging
import time
import os
import threading
from typing import Optional, Dict, Any
from googleapiclient.discovery import build  

class YouTube_Interface_Class:
    """
    Serves as a standard interface/wrapper class around YouTube IFrame Player API
    This class manages the state and provides methods similar to Spotify interface
    """
    
    def __init__(self, socketio=None):
        """
        Creates a YouTube interface object
        """
        path = os.path.dirname(os.path.abspath(__file__))
        CONFIG_FILE = os.path.join(path, '../api_credentials.config')  # CHANGE: New path
        
        self.api_key = None
        self.youtube = None
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as file:
                    for line in file:
                        if "YOUTUBE_API_KEY" in line and "=" in line:
                            self.api_key = line.split("=", 1)[1].strip()
                            break
                            
            if self.api_key and self.api_key.strip():
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logging.info("YouTube interface initialized successfully")
            else:
                logging.warning("YouTube API key not found in config file")
                
        except Exception as e:
            logging.error(f"Failed to initialize YouTube interface: {e}")

        self.current_video_id: Optional[str] = None
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.current_position: float = 0.0
        self.video_duration: float = 0.0
        self.play_start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.socketio = socketio
    
    def is_api_key_valid(self) -> bool:
        """
        Check if YouTube API key is valid and working
        
        @return: True if API key works, False otherwise
        """
        if not self.youtube or not self.api_key:
            return False
            
        try:
            # Test the API key with a simple request
            request = self.youtube.search().list(
                part="snippet",
                q="test",
                maxResults=1,
                type="video"
            )
            request.execute()
            return True
        except Exception as e:
            logging.error(f"YouTube API key validation failed: {e}")
            return False

    def play(self, video_id: str, start_time: float = 0.0) -> int:
        """
        Initiates playback of a YouTube video and signals frontend
        
        @param video_id: The YouTube video ID to play
        @param start_time: Position to start playback (in seconds)
        @return: 0 on success, 1 on failure
        """
        try:
            print(f"YouTube Interface: Playing video {video_id}")
            
            self.current_video_id = video_id
            self.is_playing = True
            self.is_paused = False
            self.current_position = start_time
            self.play_start_time = time.time() - start_time
            self.pause_time = None
            
            # Send signal to frontend via WebSocket
            if self.socketio:
                self.socketio.emit('youtube_play', {
                    'video_id': video_id,
                    'start_time': start_time,
                    'action': 'play'
                })
                print(f"Sent play signal to frontend for video: {video_id}")
            
            return 0
        except Exception as e:
            print(f"Error playing YouTube video {video_id}: {str(e)}")
            return 1
    
    def pause(self) -> int:
        """
        Pauses YouTube video playback and signals frontend
        
        @return: 0 on success, 1 on failure
        """
        try:
            if not self.is_playing:
                print("YouTube Interface: Video is not currently playing")
                return 1
                
            print("YouTube Interface: Pausing video")
            
            # Calculate current position when pausing
            if self.play_start_time:
                self.current_position = time.time() - self.play_start_time
            
            self.is_playing = False
            self.is_paused = True
            self.pause_time = time.time()
            
            # Send signal to frontend via WebSocket
            if self.socketio:
                self.socketio.emit('youtube_pause', {
                    'video_id': self.current_video_id,
                    'current_position': self.current_position,
                    'action': 'pause'
                })
                print("Sent pause signal to frontend")
            
            return 0
        except Exception as e:
            print(f"Error pausing YouTube video: {str(e)}")
            return 1
    
    def unpause(self) -> int:
        """
        Resumes YouTube video playback and signals frontend
        
        @return: 0 on success, 1 on failure
        """
        try:
            if not self.is_paused:
                print("YouTube Interface: Video is not currently paused")
                return 1
                
            print("YouTube Interface: Resuming video")
            
            self.is_playing = True
            self.is_paused = False
            
            # Adjust play_start_time to account for pause duration
            if self.pause_time and self.play_start_time:
                pause_duration = time.time() - self.pause_time
                self.play_start_time += pause_duration
            
            self.pause_time = None
            
            # Send signal to frontend via WebSocket
            if self.socketio:
                self.socketio.emit('youtube_unpause', {
                    'video_id': self.current_video_id,
                    'current_position': self.current_position,
                    'action': 'unpause'
                })
                print("Sent unpause signal to frontend")
            
            return 0
        except Exception as e:
            print(f"Error resuming YouTube video: {str(e)}")
            return 1
    
    def stop(self) -> int:
        """
        Stops YouTube video playback and signals frontend
        
        @return: 0 on success, 1 on failure
        """
        try:
            print("YouTube Interface: Stopping video")
            
            old_video_id = self.current_video_id
            
            self.current_video_id = None
            self.is_playing = False
            self.is_paused = False
            self.current_position = 0.0
            self.play_start_time = None
            self.pause_time = None
            
            # Send signal to frontend via WebSocket
            if self.socketio:
                self.socketio.emit('youtube_stop', {
                    'video_id': old_video_id,
                    'action': 'stop'
                })
                print("Sent stop signal to frontend")
            
            return 0
        except Exception as e:
            print(f"Error stopping YouTube video: {str(e)}")
            return 1
    
    def get_current_playback_info(self) -> Dict[str, Any]:
        """
        Returns current playback information similar to Spotify interface
        
        @return: Dictionary containing current playback state
        """
        current_pos_ms = 0
        
        if self.is_playing and self.play_start_time:
            # Calculate current position in milliseconds
            current_pos_ms = int((time.time() - self.play_start_time) * 1000)
        elif self.is_paused:
            current_pos_ms = int(self.current_position * 1000)
        
        return {
            'video_id': self.current_video_id,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'progress_ms': current_pos_ms,
            'duration_ms': int(self.video_duration * 1000),
            'position_seconds': current_pos_ms / 1000
        }
    
    def set_video_duration(self, duration_seconds: float):
        """
        Sets the duration of the current video
        
        @param duration_seconds: Video duration in seconds
        """
        self.video_duration = duration_seconds
        print(f"YouTube Interface: Set video duration to {duration_seconds} seconds")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extracts video ID from various YouTube URL formats
        
        @param url: YouTube URL
        @return: Video ID or None if invalid
        """
        try:
            if 'youtube.com/watch?v=' in url:
                return url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in url:
                return url.split('youtu.be/')[1].split('?')[0]
            else:
                # Assume it's already a video ID
                return url if len(url) == 11 else None
        except Exception:
            return None
    
    def get_remaining_time_ms(self) -> int:
        """
        Gets remaining time in the current video in milliseconds
        
        @return: Remaining time in milliseconds
        """
        if not self.is_playing or not self.play_start_time:
            return 0
            
        current_pos = time.time() - self.play_start_time
        remaining_seconds = max(0, self.video_duration - current_pos)
        return int(remaining_seconds * 1000)