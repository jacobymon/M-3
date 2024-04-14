import React, { useState } from 'react';
import axios from "axios";
// import './myComponent.css'; 

export async function getFirstAlbumTitle() {
  const response = await axios.get('https://jsonplaceholder.typicode.com/albums');
  console.log("Ran the function")
  return response.data[0].title;
}

const MyComponent = ({ data }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'forward' });
  const [selectedRowId, setSelectedRowId] = useState(null);

  return (
    <div>
      <h1>Hello there</h1>
      <button onClick={getFirstAlbumTitle}>
        Click me!
      </button>
    </div>
    
  );

};

export default MyComponent;