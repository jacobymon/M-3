import React, { useState } from 'react';
// import './myComponent.css'; 
``
const MyComponent = ({ data, onRowSelected }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'forward' });
  const [selectedRowId, setSelectedRowId] = useState(null);

  const headers = data.length > 0 ? Object.keys(data[0]) : [];

  

  // Adjusted handler for row click to use row's unique identifier
  const handleRowClick = (id, rowData) => {
    setSelectedRowId(id); // Update state to reflect the selected row by its ID
    if (onRowSelected) {
      onRowSelected(rowData); // If there's a function passed as a prop, call it with the row data
    }
    console.log(rowData);
  };

  return (
    <h1>Hello</h1>
  );
};

export default MyComponent;