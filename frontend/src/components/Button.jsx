import React from 'react';

const Button = ({ onClick, children }) => (
  <button onClick={onClick} style={{ padding: '8px 16px', cursor: 'pointer' }}>
    {children}
  </button>
);

export default Button;