import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { searchSongs, submitSong, submitURLSong, SongSubmission } from "./SongSubmission";
import axios from "axios";

// import jest from "jest"
// const MyComponent = require('./myComponent');
// const axios = require('axios');
jest.mock("axios");

const search_songs_response = {
  status: 200,  // Status of the Axios call
  data: {
    search_string: {
      status: 200, // Status of what was actually returned
      results: [
        {
          id: 1,
          uri: "URI 1",
          s_len: 11,
          title: "Title 1",
          artist: "Artist 1",
          album: "Album 1",
        },
        {
          id: 2,
          uri: "URI 2",
          s_len: 22,
          title: "Title 2",
          artist: "Artist 2",
          album: "Album 2",
        },
        {
          id: 3,
          uri: "URI 3",
          s_len: 33,
          title: "Title 3",
          artist: "Artist 3",
          album: "Album 3",
        },
        {
          id: 4,
          uri: "URI 4",
          s_len: 44,
          title: "Title 4",
          artist: "Artist 4",
          album: "Album 4",
        },
        {
          id: 5,
          uri: "URI 5",
          s_len: 55,
          title: "Title 5",
          artist: "Artist 5",
          album: "Album 5",
        },
      ],
    }
  }
};

const submit_song_response = {
  status: 200,  // Status of the Axios call
  data: {
    status: 200, // Status of what was actually returned
  }
};

const url_submit_response = {
  status: 200,
  data: {
    spotify_url: {
      status: 200,
    }
  }
};

const axios_network_error = {
  code: "ERR_NETWORK",
  message: "Network Error",
  name: "AxiosError",
}

const selected_song = {
  id: 2,
  uri: 'URI 2',
  s_len: 'Length 2',
  title: 'Title 2',
  artist: 'Artist 2',
  album: "Album 2"
};

const song_url = "Valid Song URL";
        



// May be good to have things return status and message, 
// if necessary, as JSON so that both either can be used depending on case


describe('Search Bar', () => {

  // Search Bar Related Tests
  it('test-auto-search', async () => {
    
    axios.get.mockResolvedValue(search_songs_response);

    let expected_result = {
      status: 200,
      response: search_songs_response.data.search_string.results
    }

    await expect(searchSongs("T")).resolves.toEqual(expected_result);
    await expect(searchSongs("Th")).resolves.toEqual(expected_result);
    await expect(searchSongs("The")).resolves.toEqual(expected_result);
  });

  it('test-dropdown-select-song', async () => {

    axios.get.mockResolvedValue(search_songs_response); // Setup mock to resolve with `data`

    let expected_result = {
      status: 200,
      response: search_songs_response.data.search_string.results
    }

    await expect(searchSongs("T")).resolves.toEqual(expected_result);
    await expect(searchSongs("Th")).resolves.toEqual(expected_result);
    await expect(searchSongs("The")).resolves.toEqual(expected_result);







    // Add stuff for actually selecting the song from the dropdown
    // Rendering, getting the 5 results by seeing they exist (Take from Full Test)







  });

  it('test-empty-searchBar-query', async () => {

    let expected_error = {
      status: 400,
      response: 'Please enter a song name to search.'
    }

    // Doesn't need to mock anything because it should catch it before it calls axios

    await expect(searchSongs("")).resolves.toEqual(expected_error);
  });

  //Backend API Related Tests
  it('test-bad-oauth', async () => {

    let expected_error = {
      status: 403,
      response: 'Bad OAuth request.'
    }

    // let bad_response = {
    //   status: 200,
    // }

    let bad_search_songs_response = {
      status: 200,  // Status of the Axios call
      data: {
        search_string: {
          status: 403, // Status of what was actually returned
        }
      }
    };

    //Expect error 403 from backend (TODO)
    axios.get.mockResolvedValue(bad_search_songs_response);

    await expect(searchSongs("Test bad OAuth")).resolves.toEqual(expected_error);
  });

  it('test-exceed-rate-limits', async () => {
    // const errorMessage = 'Exceeded Spotify search limit. Please wait a few seconds before retrying.';

    // //Expect error 429 from backend (TODO)
    // axios.get.mockResolvedValue(new Error(errorMessage));

    // await expect(searchSongs("Test Exceed Rate Limit")).resolves.toEqual(errorMessage);

    let expected_error = {
      status: 429,
      response: 'Exceeded Spotify search limit. Please wait a few seconds before retrying.'
    }

    // let bad_response = {
    //   status: 429,
    // }

    let bad_search_songs_response = {
      status: 200,  // Status of the Axios call
      data: {
        search_string: {
          status: 429, // Status of what was actually returned
        }
      }
    };

    //Expect error 403 from backend (TODO)
    axios.get.mockResolvedValue(bad_search_songs_response);

    await expect(searchSongs("Test Exceed Rate Limit")).resolves.toEqual(expected_error);

  });

  it('test-unknown-api-error', async () => {

    let expected_error = {
      status: 500,
      response: "An error has occured in the backend."
    }

    let bad_search_songs_response = {
      status: 200,  // Status of the Axios call
      data: {
        search_string: {
          status: 500, // Status of what was actually returned
        }
      }
    };

    //Expect a network error from axios
    axios.get.mockResolvedValue(bad_search_songs_response);

    await expect(searchSongs("Test Backend Error")).resolves.toEqual(expected_error);
  });

});


describe('Submit Button', () => {

  // Submit Button Related Tests
  it('test-valid-song', async () => {

    let expected_result = {
      status: 200,
      response: "My success message (submitSong)"
    }
    
    axios.post.mockResolvedValue(submit_song_response); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_result);

  });

  it('test-song-null', async () => {

    let expected_error = {
      status: 400,
      response: "No song was selected."
    }

    await expect(submitSong(null)).resolves.toEqual(expected_error);

  });

  it('test-song-no-title', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      // title: 'Title 2',
      artist: 'Artist 2',
      album: "Album 2"
    };

    let expected_error = {
      status: 400,
      response: "Could not find the song’s title."
    }


    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-uri', async () => {

    const selected_song = {
      id: 2,
      // uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      artist: 'Artist 2',
      album: "Album 2"
    };
    
    let expected_error = {
      status: 400,
      response: "Could not find the song’s URI."
    }

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-artist', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      // artist: 'Artist 2',
      album: "Album 2"
    };

    let expected_error = {
      status: 400,
      response: "Could not find the song’s artist."
    }

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-album', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      s_len: 'Length 2',
      title: 'Title 2',
      artist: 'Artist 2',
      // album: "Album 2"
    };

    let expected_error = {
      status: 400,
      response: "Could not find the song’s album."
    }

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });

  it('test-song-no-s_len', async () => {

    const selected_song = {
      id: 2,
      uri: 'URI 2',
      // s_len: 'Length 2',
      title: 'Title 2',
      artist: 'Artist 2',
      album: "Album 2"
    };
    
    let expected_error = {
      status: 400,
      response: "Could not find the song’s length."
    }
    
    // axios.post.mockResolvedValue(data); // Setup mock to resolve with `data`

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  });
  


  //Backend API Related Tests
  // it('test-timeout', async () => {


  //   // I don't think I have a way of distinguishing Axios network errors like timeout and not found.
  //   // Axios just gives a generic network error.


  //   let expected_error = {
  //     status: 408,
  //     response: "Song submission timed out. Please try again."
  //   }

  //   //Expect error 408 from backend (TODO)
  //   axios.post.mockRejectedValue(axios_network_error);

  //   await expect(submitSong(selected_song)).resolves.toEqual(expected_error);
  // });

  // it('test-not-found', async () => {

  //   const data = {
  //     status: 404,
  //   };

  //   let expected_error = {
  //     status: 404,
  //     response: "Could not find host machine. Please try again."
  //   }

  //   //Expect error 404 from backend (TODO)
  //   axios.post.mockResolvedValue(data);

  //   await expect(submitSong(selected_song)).resolves.toEqual(expected_error);

  // });

  it('test-internal-server-error', async () => {

    let bad_submit_song_response = {
      status: 200,  // Status of the Axios call
      data: {
        status: 500, // Status of what was actually returned
      }
    };

    let expected_error = {
      status: 500,
      response: "An internal server error has occurred. Please try again."
    }

    //Expect error 500 from backend (TODO)
    axios.post.mockResolvedValue(bad_submit_song_response);

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);
  });

  it('test-generic-api-error', async () => {

    let expected_error = {
      status: 500,
      response: "A network error has occurred while submitting the song."
    }

    //Expect a network error from axios
    axios.post.mockRejectedValue(axios_network_error);

    await expect(submitSong(selected_song)).resolves.toEqual(expected_error);
  });

});


describe('URL Textbox', () => {

  // URL Textbox Related Tests
  it('test-url-submit', async () => {

    

    let expected_result = {
      status: 200,
      response: "My Success Message (Submit URL Song)"
    }
    
    axios.post.mockResolvedValue(url_submit_response); // Setup mock to resolve with `data`

    await expect(submitURLSong(song_url)).resolves.toEqual(expected_result);
    
  });

  it('test-bad-url-submit', async () => {

    let bad_submit_url_response = {
      status: 200,  // Status of the Axios call
      data: {
        spotify_url: {
          status: 404, // Status of what was actually returned
        }
      }
    };

    let expected_error = {
      status: 404,
      response: "No song was found for that URL."
    }
    
    //Expect error 400 or 500 from backend (TODO)
    axios.post.mockResolvedValue(bad_submit_url_response);

    await expect(submitURLSong("Bad Song URL")).resolves.toEqual(expected_error);
    
  });

  it('test-empty-url-submit', async () => {

    let expected_error = {
      status: 400,
      response: "No URL was provided."
    }

    await expect(submitURLSong("")).resolves.toEqual(expected_error);
    
  });



  //Backend API Related Tests
  // it('test-timeout', async () => {

  //   const data = {
  //     status: 408,
  //   };

  //   let expected_error = {
  //     status: 408,
  //     response: "URL Song submission timed out. Please try again."
  //   }

  //   //Expect error 408 from backend (TODO)
  //   axios.post.mockResolvedValue(data);

  //   await expect(submitURLSong("URL Timeout")).resolves.toEqual(expected_error);
  // });

  // it('test-not-found', async () => {

  //   const data = {
  //     status: 404,
  //   };

  //   let expected_error = {
  //     status: 404,
  //     response: "Could not find host machine. Please try again."
  //   }

  //   //Expect error 404 from backend (TODO)
  //   axios.post.mockResolvedValue(data);

  //   await expect(submitURLSong("Host Machine not Found")).resolves.toEqual(expected_error);
  // });

  it('test-internal-server-error', async () => {

    let bad_submit_url_response = {
      status: 200,  // Status of the Axios call
      data: {
        spotify_url: {
          status: 500, // Status of what was actually returned
        }
      }
    };

    let expected_error = {
      status: 500,
      response: "An internal server error has occurred. Please try again."
    }

    //Expect error 500 from backend (TODO)
    axios.post.mockResolvedValue(bad_submit_url_response);

    await expect(submitURLSong("URL Internal Server Error")).resolves.toEqual(expected_error);

  });

  // it('test-generic-api-error', async () => {

  //   const data = {
  //     status: 599,  // Any error code that is not already handled
  //   };

  //   let expected_error = {
  //     status: 500,
  //     response: "An API error has occurred."
  //   }

  //   //Expect error 500 from backend (TODO)
  //   axios.post.mockResolvedValue(data);

  //   await expect(submitURLSong("URL API Error")).resolves.toEqual(expected_error);

  // });

  it('test-generic-api-error', async () => {

    let expected_error = {
      status: 500,
      response: "A network error has occured while submitting the song URL."
    }

    //Expect a network error from axios
    axios.post.mockRejectedValue(axios_network_error);

    await expect(submitURLSong(selected_song)).resolves.toEqual(expected_error);
  });

});

// Timers to allow for waiting between operations
jest.useFakeTimers(); 

describe('Full System', () => {

  // Setup: Set searchBar_query to an empty String, set selected_song to null, set search_results to an empty array, set all errors to null.
  // Test: “Click” the search bar, enter “T,” then “h,” then “e,” then “click” the first entry in search_results to move it into selected_song, then “click” the submit button
  // Results: Success (200) response from the backend/a mock. All errors are still null. Selected_song should be set to null, search_query an empty string, and search_results should be made an empty array.
  // Notes: If this test is done correctly, it should only succeed if all other tests that expect success succeed. This can be used as a general warning light if something is wrong and that we should investigate specific test cases.
  it('test-search-and-submit', async () => {
    // const { screen.getByTestId } = 
    render(<SongSubmission />);

    // Expect no errors to start
    expect(screen.queryByTestId("SearchBarError")).not.toBeInTheDocument();
    expect(screen.queryByTestId("SubmitButtonError")).not.toBeInTheDocument();

    const searchBar = screen.getByTestId("SearchBar");
    expect(searchBar).toHaveValue('');

    axios.get.mockResolvedValue(search_songs_response); // Setup mock to resolve with `data`

    let expected_search_result = {
      status: 200,
      response: search_songs_response.data.search_string.results
    }

    fireEvent.click(searchBar);

    fireEvent.change(searchBar, { target: { value: "T" } });
    await act(async () => {
      await expect(searchSongs("T")).resolves.toEqual(expected_search_result);
      jest.advanceTimersByTime(200); // Don't wait for debounce to resolve
    });

    expect(screen.queryByTestId("Result0")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result1")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result2")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result3")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result4")).not.toBeInTheDocument();


    fireEvent.change(searchBar, { target: { value: "Th" } });
    await act(async () => {
      await expect(searchSongs("Th")).resolves.toEqual(expected_search_result);
      jest.advanceTimersByTime(500); // Wait for debounce to resolve
    });

    expect(screen.queryByTestId("Result0")).toBeInTheDocument();
    expect(screen.queryByTestId("Result1")).toBeInTheDocument();
    expect(screen.queryByTestId("Result2")).toBeInTheDocument();
    expect(screen.queryByTestId("Result3")).toBeInTheDocument();
    expect(screen.queryByTestId("Result4")).toBeInTheDocument();


    fireEvent.change(searchBar, { target: { value: "The" } });
    await act(async () => {
      await expect(searchSongs("The")).resolves.toEqual(expected_search_result);
      jest.advanceTimersByTime(500); // Wait for debounce to resolve
    });

    expect(screen.queryByTestId("Result0")).toBeInTheDocument();
    expect(screen.queryByTestId("Result1")).toBeInTheDocument();
    expect(screen.queryByTestId("Result2")).toBeInTheDocument();
    expect(screen.queryByTestId("Result3")).toBeInTheDocument();
    expect(screen.queryByTestId("Result4")).toBeInTheDocument();


    let search_results = await searchSongs("The");
    expect(search_results).toEqual(expected_search_result);


    const firstResult = screen.getByTestId("Result0");
    fireEvent.click(firstResult);
    let selected_song = search_results.response[0];

    // Check that the search bar's value now contains the song's name
    expect(searchBar).toHaveValue(selected_song.title);

    // Check that Result0 - Result 4 are gone
    // Commented out for testing testing purposes
    expect(screen.queryByTestId("Result0")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result1")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result2")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result3")).not.toBeInTheDocument();
    expect(screen.queryByTestId("Result4")).not.toBeInTheDocument();


    const submitButton = screen.getByTestId("SubmitButton");

    let expected_submit_result = {
      status: 200,
      response: "My success message (submitSong)"
    }
    
    axios.post.mockResolvedValue(submit_song_response); // Setup mock to resolve with `data`

    fireEvent.click(submitButton);
    await act(async () => {
      jest.advanceTimersByTime(1000); // Wait for it to resolve
      await expect(submitSong(selected_song)).resolves.toEqual(expected_submit_result);
    });
    
      
    // Check that the search bar is now empty
    expect(searchBar).toHaveValue('');
  
    // Check that there are no errors after everything is done
    expect(screen.queryByTestId("SearchBarError")).not.toBeInTheDocument();
    expect(screen.queryByTestId("SubmitButtonError")).not.toBeInTheDocument();
  
  });

  // Setup: Set url_textbox_input to an empty String, set selected_song to null, set search_results to an empty array, set all errors to null.
  // Test: “Click” the url text box bar, enter a valid Spotify song URL then “click” the URL submit button
  // Results: Success (200) response from the backend/a mock. All errors are still null. url_textbox_input should be set to null.
  // Notes: If this test is done correctly, it should only succeed if all other tests that expect success succeed. This can be used as a general warning light if something is wrong and that we should investigate specific test cases.

  it('test-URL-and-submit', async () => {

    render(<SongSubmission />);

    // Expect no errors to start
    expect(screen.queryByTestId("SearchBarError")).not.toBeInTheDocument();
    expect(screen.queryByTestId("SubmitBarError")).not.toBeInTheDocument();

    const URLTextBox = screen.getByTestId("URLTextBox");
    expect(URLTextBox).toHaveValue('');

    // Entering text into the textbox
    // Doesn't need an act(...) because it doesn't have an onChange
    fireEvent.change(URLTextBox, { target: { value: "Valid URL"}});

    const URLSubmitButton = screen.getByTestId("URLSubmitButton");

    let expected_submit_result = {
      status: 200,
      response: "My Success Message (Submit URL Song)"
    }
    
    axios.post.mockResolvedValue(url_submit_response); // Setup mock to resolve with `data`

    fireEvent.click(URLSubmitButton);
    await act(async () => {
      // await expect(searchSongs("Th")).resolves.toEqual(expected_search_result);
      await expect(submitURLSong(selected_song)).resolves.toEqual(expected_submit_result);
      jest.advanceTimersByTime(500); // Wait for debounce to resolve
    });
    
    
    // Check that the search bar is now empty
    expect(URLTextBox).toHaveValue('');
  
    // Check that there are no errors after everything is done
    expect(screen.queryByTestId("SearchBarError")).not.toBeInTheDocument();
    expect(screen.queryByTestId("SubmitBarError")).not.toBeInTheDocument();

  });

});
