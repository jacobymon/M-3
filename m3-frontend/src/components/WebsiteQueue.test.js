import { render, screen, fireEvent, act} from '@testing-library/react';
import axios from 'axios';

import DisplayedQueue, {requestQueue, 
	REQUEST_QUEUE_CALL, VERIFY_HOST_CALL,
	Song } from './WebsiteQueue';

jest.mock('axios');

// axios.get.mockResolvedValue({data: {...}}) : returns 200, data
// == axios.get.mockImplementation(() => Promise.resolve({status: int, data: {}}));
// axios.get.mockRejectedValue
// == axios.get.mockImplementation(() => Promise.reject({ ... }));

const TESTSONG1 = {
	"name": "All I Want For Christmas Is You",
	"artist": "Mariah Carey",
	"albumname": "Mariah Carey's Best Hits",
	"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF1000,1000_QL80_.jpg",
	"submissionID": 1
}
const SECOND_TESTSONG1 = {
	"name": "All I Want For Christmas Is You",
	"artist": "Mariah Carey",
	"albumname": "Mariah Carey's Best Hits",
	"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF1000,1000_QL80_.jpg",
	"submissionID": 2
}
const TESTSONG2 = {
	"name": "testsong",
	"artist": "totaly real artist",
	"albumname": "100% real album",
	"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF2000,1000_QL80_.jpg",
	"submissionID": 3
}

const AXIOS_ISHOST = {
	status: 200,
	data: [true, "chocolate chip"]
}
const AXIOS_ISNOTHOST = {
	status: 200,
	data: [false, ""]
}
const AXIOS_RESPONSE_EMPTY = {
	status: 200,
	data: []
}
const AXIOS_RESPONSE_1 = {
	status: 200,
	data: [TESTSONG1]
}
const AXIOS_RESPONSE_12 = {
	status: 200,
	data: [TESTSONG1, TESTSONG2]
}
const AXIOS_RESPONSE_11 = {
	status: 200,
	data: [TESTSONG1, SECOND_TESTSONG1]
}

const AXIOS_POST_RESPONSE = {
	status: 200
}

const AXIOS_REJECT_408 = { status: 408 }
const AXIOS_REJECT_500 = { status: 500 }




describe("RequestQueue helper function", () => {

	it('sends request on call', async () => {
		axios.get.mockResolvedValue(AXIOS_RESPONSE_EMPTY)
		const mockUpdateQueueError = jest.fn();
		const mockUpdateSongs = jest.fn();
		
		requestQueue(mockUpdateQueueError, mockUpdateSongs);
	
		expect(axios.get).toBeCalledWith(REQUEST_QUEUE_CALL, {timeout:5000})
	});

	it('updates songs on call', async () => {
		axios.get.mockResolvedValue(AXIOS_RESPONSE_12)
		const mockUpdateQueueError = jest.fn();
		const mockUpdateSongs = jest.fn();
		
		await requestQueue(mockUpdateQueueError, mockUpdateSongs);
	
		expect(mockUpdateSongs).toBeCalledWith([TESTSONG1, TESTSONG2])
	});

	it('updates error code on failure', async () => {
		axios.get.mockRejectedValue(AXIOS_REJECT_500)
		const mockUpdateQueueError = jest.fn();
		const mockUpdateSongs = jest.fn();

		await requestQueue(mockUpdateQueueError, mockUpdateSongs)
		
		expect(mockUpdateQueueError).toBeCalledWith(500)
	});
});

describe("Song subcomponent", () => {
	it('renders a Song', () => {
		render(<Song></Song>)
	});

	it('includes the song name', () => {
		render(<Song name = {TESTSONG1.name}></Song>)
		expect(screen.getByText(TESTSONG1.name)).toBeInTheDocument();
	});

	it('includes the artist', () => {
		render(<Song artist = {TESTSONG1.artist}></Song>)
		expect(screen.getByText(TESTSONG1.artist)).toBeInTheDocument();
	});

	it('includes the album name', () => {
		render(<Song albumname = {TESTSONG1.albumname}></Song>)
		expect(screen.getByText(TESTSONG1.albumname)).toBeInTheDocument();
	});
});

describe("DisplayedQueue as a whole", () => {
	jest.useFakeTimers();

	it('can render', async () => {
		await act(async () => {
			render(<DisplayedQueue />)
		});
	})

	it('calls request queue when rendered', async () => {
		axios.get.mockImplementation((call) => {
			// If you request queue, return songs.
			if (call==REQUEST_QUEUE_CALL) return Promise.resolve(AXIOS_RESPONSE_EMPTY)
			// if you're asking if you're the host, return that you are
			if (call==VERIFY_HOST_CALL) return Promise.resolve(AXIOS_ISHOST)
		})

		await act(async () => {
			render(<DisplayedQueue />)
		});

		expect(axios.get).toBeCalledTimes(1)
		expect(axios.get).toBeCalledWith(REQUEST_QUEUE_CALL)
	});
	
	it('renders songs in the queue', async () => {

		axios.get.mockImplementation((call) => {
			if (call==REQUEST_QUEUE_CALL) return Promise.resolve(AXIOS_RESPONSE_12)
			if (call==VERIFY_HOST_CALL) return Promise.resolve(AXIOS_ISHOST)
		})

		await act(async () => {
			render(<DisplayedQueue />)
		});

		// Check that the songs are in the list.
		expect(screen.getByText(TESTSONG1.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG1.artist)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG2.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG2.artist)).toBeInTheDocument();
	});
	
	it('renders identical songs', async () => {

		axios.get.mockImplementation((call) => {
			if (call==REQUEST_QUEUE_CALL) return Promise.resolve(AXIOS_RESPONSE_11)
			if (call==VERIFY_HOST_CALL) return Promise.resolve(AXIOS_ISHOST)
		})

		await act(async () => {
			render(<DisplayedQueue />)
		});

		// Check that the songs are in the list.
		var times_name_showed_up = screen.queryAllByText(TESTSONG1.name).length
		var times_artist_showed_up = screen.queryAllByText(TESTSONG1.artist).length
		expect(times_name_showed_up).toBe(2)
		expect(times_artist_showed_up).toBe(2)
	});
})

describe("Remove Song Button", () => {
	it('sends remove song api call when clicked', async () => {
		axios.get.mockImplementation((call) => {
			if (call==REQUEST_QUEUE_CALL) return Promise.resolve(AXIOS_RESPONSE_1)
			if (call==VERIFY_HOST_CALL) return Promise.resolve(AXIOS_ISHOST)
		})
		axios.post.mockResolvedValue(AXIOS_POST_RESPONSE);
		await act(async () => {
			render(<DisplayedQueue />)
		});

		const remove_button = screen.getByTestId("removeSongButton");
		fireEvent.click(remove_button);

		expect(axios.post).toBeCalledTimes(1)
		expect(axios.post.mock.calls[0][1].submissionID).toBe(TESTSONG1.submissionID)

	})
})


