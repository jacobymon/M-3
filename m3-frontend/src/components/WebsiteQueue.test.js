import { render, screen } from '@testing-library/react';
import axios from 'axios';

import DisplayedQueue, {requestQueue, requestQueueUpdates} from './WebsiteQueue';
import {REQUEST_QUEUE_CALL, REQUEST_QUEUE_UPDATE_CALL} from './WebsiteQueue';

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

describe("testing RequestQueue functionality", () => {

	jest.useFakeTimers();

	it('requests queue on render', () => {
		axios.get.mockResolvedValue([])
	
		render(<DisplayedQueue />);
	
		expect( axios.get.mock.calls.length ).toBeGreaterThanOrEqual(1)
		// Check that first arg of first call is request queue
		expect( axios.get.mock.calls[0][0]).toBe(REQUEST_QUEUE_CALL)
	});

	it('re-requests queue', () => {
		axios.get.mockRejectedValueOnce({status: 500})
		axios.get.mockResolvedValue([])
		render(<DisplayedQueue />);
	
		expect( axios.get.mock.calls.length ).toBeGreaterThanOrEqual(2)
		// Check that first arg of first call is request queue
		expect( axios.get.mock.calls[0][0]).toBe(REQUEST_QUEUE_CALL)
		// Check that first arg of second call is request queue
		expect( axios.get.mock.calls[1][0]).toBe(REQUEST_QUEUE_CALL)
	});

	it('fills songs correctly', () => {
		axios.get.mockResolvedValue([TESTSONG1, TESTSONG2])

		render(<DisplayedQueue />)

		expect(screen.getByText(TESTSONG1.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG1.artist)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG2.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG2.artist)).toBeInTheDocument();

	});


	it('fills identical songs', () => {
		axios.get.mockResolvedValue([
			TESTSONG1, SECOND_TESTSONG1
		])
		render(<DisplayedQueue />);
	
		expect(screen.getByText(TESTSONG1.name)).toBeInTheDocument();
		expect(screen.getByText(TESTSONG1.artist)).toBeInTheDocument();
	});
});


// describe("testing Request Queue Updates functionality", () => {

// 	jest.useFakeTimers();
	
// 	it('requests queue update on call', () => {
// 		const mockUpdateSongs = jest.fn();

// 		requestQueueUpdates(mockUpdateSongs);
// 		expect( axios.get.mock.calls.length ).toEqual(1)
// 		// TODO: test that call is request queue (and not just request queue update)
// 	});

// 	it('requests queue update on render', () => {
// 		axios.get.mockResolvedValue([])
	
// 		render(<DisplayedQueue />);
	
// 		expect( axios.get.mock.calls.length ).toBeGreaterThanOrEqual(1)
// 		// TODO: test that call is request queue update (and not just request queue)
// 		expect(true).toEqual(false)
// 	});

// 	it('correctly updates songs', () => {
// 		const mockUpdateSongs = jest.fn();
// 		axios.get.mockResolvedValueOnce([TESTSONG1])

// 		requestQueueUpdates(mockUpdateSongs);
	
// 		// The first arg of the first call to mockUpdateSongs was TESTSONG1
// 		expect(mockUpdateSongs.mock.calls[0][0]).toBe(TESTSONG1);
// 	});

// 	it('handles request timeout', () => {
// 		const mockUpdateSongs = jest.fn();
// 		axios.get.mockRejectedValueOnce({status: 408})
// 		axios.get.mockResolvedValueOnce([TESTSONG1])

// 		requestQueueUpdates(mockUpdateSongs);

		
// 		expect( axios.get.mock.calls.length ).toEqual(3)
// 		// TODO: test that call is request queue (and not just request queue update)
// 		expect(true).toEqual(false)
	
// 		// The first arg of the first call to mockUpdateSongs was TESTSONG1
// 		expect(mockUpdateSongs.mock.calls[0][0]).toBe(TESTSONG1);
// 	});
// });

describe("general / full-way-through tests", () => {
	it('renders', () => {
		render(<DisplayedQueue />);
	});
});