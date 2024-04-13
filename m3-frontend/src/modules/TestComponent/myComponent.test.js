import React from 'react';
import { getFirstAlbumTitle } from "./myComponent";
import axios from "axios";

// import jest from "jest"
// const MyComponent = require('./myComponent');
// const axios = require('axios');
jest.mock("axios");

describe('getFirstAlbumTitle', () => {
  it('gets the first album from the results', async () => {
    const data = 
        [
            {
              userId: 1,
              id: 1,
              title: 'My First Album'
            },
            {
              userId: 1,
              id: 2,
              title: 'Album: The Sequel'
            }
        ];

    axios.get.mockResolvedValue({ data }); // Setup mock to resolve with `data`

    await expect(getFirstAlbumTitle()).resolves.toEqual(data[0].title);
  });

  it('fetches erroneously data from an API', async () => {
    const errorMessage = 'Network Error';

    axios.get.mockRejectedValue(new Error(errorMessage));

    await expect(getFirstAlbumTitle()).rejects.toThrow(errorMessage);
  });
});

// it('returns the title of the first album', async () => {
//   axios.get.mockResolvedValue({
//     data: [
//       {
//         userId: 1,
//         id: 1,
//         title: 'My First Album'
//       },
//       {
//         userId: 1,
//         id: 2,
//         title: 'Album: The Sequel'
//       }
//     ]
//   });

//   const title = await myComponent.getFirstAlbumTitle();
//   expect(title).toEqual('My First Album');
// });