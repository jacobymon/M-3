import { render, screen } from '@testing-library/react';
import axios from 'axios';
import { act } from 'react-dom/test-utils';

import DisplayedQueue, {requestQueue, requestQueueUpdates,
	REQUEST_QUEUE_CALL, REQUEST_QUEUE_UPDATE_CALL,
	Song, DeleteButton
} from './WebsiteQueue';

jest.mock('axios');

// axios.get.mockResolvedValue({data: {...}}) : returns 200, data
// == axios.get.mockImplementation(() => Promise.resolve({status: int, data: {}}));
// axios.get.mockRejectedValue
// == axios.get.mockImplementation(() => Promise.reject({ ... }));

const TESTSONG1 = {
	"id": "3v66DjMBSdWY0jy5VVjHI2",
	"name": "All I Want For Christmas Is You",
	"artist": "Mariah Carey",
	"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF1000,1000_QL80_.jpg",
	"submissionID": 1
}
const SECOND_TESTSONG1 = {
	"id": "3v66DjMBSdWY0jy5VVjHI2",
	"name": "All I Want For Christmas Is You",
	"artist": "Mariah Carey",
	"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF1000,1000_QL80_.jpg",
	"submissionID": 2
}
const TESTSONG2 = {
	"id": "xkcdykcd",
	"name": "testsong",
	"artist": "totaly real artist",
	"albumcover": "https://m.media-amazon.com/images/I/71X9F2m7-kL._UF2000,1000_QL80_.jpg",
	"submissionID": 3
}

const AXIOS_RQ_RESPONSE_EMPTY = {
	status: 200,
	data: {
		songs: []
	}
}
const AXIOS_RQ_RESPONSE_1 = {
	status: 200,
	data: {
		songs: [TESTSONG1]
	}
}
const AXIOS_RQ_RESPONSE_12 = {
	status: 200,
	data: {
		songs: [TESTSONG1, TESTSONG2]
	}
}
const AXIOS_RQ_RESPONSE_11 = {
	status: 200,
	data: {
		songs: [TESTSONG1, SECOND_TESTSONG1]
	}
}

describe("testing RequestQueue functionality", () => {

	jest.useFakeTimers();

	it('requests queue on render', async () => {
		axios.get.mockResolvedValue(AXIOS_RQ_RESPONSE_EMPTY)
	
		// wrapping the render in this act function forces the test to wait for
		// everything to finish rendering before making any assertions. 
		await act(async () => {
			render(<DisplayedQueue />)
		});
	
		expect(axios.get).toBeCalledWith(REQUEST_QUEUE_CALL)
	});

	it('re-requests queue', async () => {
		axios.get.mockRejectedValueOnce({status: 500})
		axios.get.mockResolvedValue(AXIOS_RQ_RESPONSE_EMPTY)

		// wrapping the render in this act function forces the test to wait for
		// everything to finish rendering before making any assertions. 
		await act(async () => {
			render(<DisplayedQueue />)
		});
		
	
		// Find all calls with the first argument equal to REQUEST_QUEUE_CALL
		var calls = axios.get.mock.calls.filter((call)=>call[0]==REQUEST_QUEUE_CALL)
		expect(calls.length).toBe(2)
	});

	it('fills songs correctly', async () => {
		axios.get.mockResolvedValue(AXIOS_RQ_RESPONSE_12)

		await act(async () => {
			render(<DisplayedQueue />)
		});

		expect(screen.getByText(TESTSONG1.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG1.artist)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG2.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG2.artist)).toBeInTheDocument();

	});


	it('fills identical songs', async () => {
		axios.get.mockResolvedValue(AXIOS_RQ_RESPONSE_11)
		
		await act(async () => {
			render(<DisplayedQueue />)
		});
	
		var times_name_showed_up = screen.queryAllByText(TESTSONG1.name).length
		var times_artist_showed_up = screen.queryAllByText(TESTSONG1.artist).length
		expect(times_name_showed_up).toBe(2)
		expect(times_artist_showed_up).toBe(2)
	});
});


// describe("testing Request Queue Updates functionality", () => {

// 	jest.useFakeTimers();
	
// 	it('requests queue update on call', () => {
// 		const mockUpdateSongs = jest.fn();

// 		requestQueueUpdates(mockUpdateSongs);
// 		expect( axios.get.mock.calls.length ).toEqual(1)
// 		// Test that the call is request_queue_update
// 		expect( axios.get.mock.calls[0][0]).toBe(REQUEST_QUEUE_UPDATE_CALL)
// 	});

// 	it('requests queue update on render', () => {
// 		axios.get.mockResolvedValue(AXIOS_RQ_RESPONSE_EMPTY)
	
// 		render(<DisplayedQueue />);
	
// 		expect( axios.get.mock.calls.length ).toBeGreaterThanOrEqual(1)
// 		// TODO: test that call is request queue update (and not just request queue)
// 		expect(true).toEqual(false)
// 	});

// 	it('correctly updates songs', () => {
// 		const mockUpdateSongs = jest.fn();
// 		axios.get.mockResolvedValueOnce(AXIOS_RQ_RESPONSE_1)

// 		requestQueueUpdates(mockUpdateSongs);
	
// 		// The first arg of the first call to mockUpdateSongs was TESTSONG1
// 		expect(mockUpdateSongs.mock.calls[0][0]).toBe(TESTSONG1);
// 	});

// 	it('handles request timeout', () => {
// 		const mockUpdateSongs = jest.fn();
// 		axios.get.mockRejectedValueOnce({status: 408})
// 		axios.get.mockResolvedValueOnce(AXIOS_RQ_RESPONSE_1)

// 		requestQueueUpdates(mockUpdateSongs);

		
// 		expect( axios.get.mock.calls.length ).toEqual(3)
// 		// TODO: test that call is request queue (and not just request queue update)
// 		expect(true).toEqual(false)
	
// 		// The first arg of the first call to mockUpdateSongs was TESTSONG1
// 		expect(mockUpdateSongs.mock.calls[0][0]).toBe(TESTSONG1);
// 	});
// });


describe("Song subcomponent testing", () => {
	jest.useFakeTimers();

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

	it('includes the album cover', () => {
		render(<Song albumcover = {TESTSONG1.albumcover}></Song>)
		expect(screen.getByText(TESTSONG1.albumcover)).toBeInTheDocument();
	});
});

describe("full-way-through tests", () => {
	jest.useFakeTimers();
	
	it('renders', async () => {
		axios.get.mockResolvedValue(AXIOS_RQ_RESPONSE_EMPTY)
		await act(async () => {
			render(<DisplayedQueue />)
		});
	});
})
