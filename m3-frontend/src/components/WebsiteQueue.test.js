import { render, screen } from '@testing-library/react';
import axios from 'axios';

import DisplayedQueue, {requestQueueUpdates} from './WebsiteQueue';

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

describe("testing RequestQueue functionality", () => {

	jest.useFakeTimers();

	it('requests queue on render', () => {
		axios.get.mockResolvedValue([])
	
		render(<DisplayedQueue />);
	
		expect( axios.get.mock.calls.length ).toEqual(1)
		// TODO: test that call is request queue (and not just request queue update)
		expect(true).toEqual(false)
	});

	it('re-requests queue', () => {
		axios.get.mockRejectedValueOnce({status: 500})
		axios.get.mockResolvedValue([])
		render(<DisplayedQueue />);
	
		expect( axios.get.mock.calls.length ).toEqual(2)
		// TODO: test that call is request queue (and not just request queue update)
		expect(true).toEqual(false)
	});

	it('fills songs correctly', () => {
		axios.get.mockResolvedValue([
			// Songs here
		])
		render(<DisplayedQueue />);
	
		// TODO: check songs are filled correctly
		expect(true).toEqual(false)
	});


	it('fills identical songs', () => {
		axios.get.mockResolvedValue([
			// Songs here
		])
		render(<DisplayedQueue />);
	
		// TODO: check songs are filled correctly
		expect(true).toEqual(false)
	});
});


describe("testing Request Queue Updates functionality", () => {

	jest.useFakeTimers();
	
	it('requests queue update on call', () => {
		const mockUpdateSongs = jest.fn();

		requestQueueUpdates(mockUpdateSongs);
		expect( axios.get.mock.calls.length ).toEqual(1)
		// TODO: test that call is request queue (and not just request queue update)
	});

	it('requests queue update on render', () => {
		axios.get.mockResolvedValue([])
	
		render(<DisplayedQueue />);
	
		expect( axios.get.mock.calls.length ).toEqual(1)
		// TODO: test that call is request queue update (and not just request queue)
		expect(true).toEqual(false)
	});

	it('correctly updates songs', () => {
		const mockUpdateSongs = jest.fn();
		axios.get.mockResolvedValueOnce([TESTSONG1])

		requestQueueUpdates(mockUpdateSongs);
	
		// The first arg of the first call to mockUpdateSongs was TESTSONG1
		expect(mockUpdateSongs.mock.calls[0][0]).toBe(TESTSONG1);
	});

	it('handles request timeout', () => {
		const mockUpdateSongs = jest.fn();
		axios.get.mockRejectedValueOnce({status: 408})
		axios.get.mockResolvedValueOnce([TESTSONG1])

		requestQueueUpdates(mockUpdateSongs);

		
		expect( axios.get.mock.calls.length ).toEqual(3)
		// TODO: test that call is request queue (and not just request queue update)
		expect(true).toEqual(false)
	
		// The first arg of the first call to mockUpdateSongs was TESTSONG1
		expect(mockUpdateSongs.mock.calls[0][0]).toBe(TESTSONG1);
	});
});

describe("general / full-way-through tests", () => {
	it('renders', () => {
		render(<DisplayedQueue />);
	});
});