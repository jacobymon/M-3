import React, { useState } from 'react';
import { useQueue } from './QueueContext';

const YOUTUBE_API_KEY = process.env.REACT_APP_YOUTUBE_API_KEY;

export default function YouTubeSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const { addToQueue } = useQueue();

  const searchYouTube = async () => {
    if (!query) return;

    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=8&q=${encodeURIComponent(
      query
    )}&key=${YOUTUBE_API_KEY}`;

    try {
      console.log('Fetching:', url);
      const res = await fetch(url);
      const data = await res.json();

      const videos = data.items.map((item) => ({
        id: item.id.videoId,
        title: item.snippet.title,
        artist: item.snippet.channelTitle,
        thumbnail: item.snippet.thumbnails.medium.url,
        source: 'youtube',
        videoId: item.id.videoId,
      }));

      setResults(videos);
    } catch (error) {
      console.error('YouTube search error:', error);
    }
  };

  return (
    <div>
      <input
        placeholder="Search YouTube..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && searchYouTube()}
      />
      <button onClick={searchYouTube}>Search</button>

      <ul>
        {results.map((track) => (
          <li key={track.id} style={{ marginBottom: 10 }}>
            <img src={track.thumbnail} alt={track.title} width="120" />
            <div>
              <strong>{track.title}</strong> <br />
              <em>{track.artist}</em> <br />
              <button onClick={() => addToQueue(track)}>Add to Queue</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
