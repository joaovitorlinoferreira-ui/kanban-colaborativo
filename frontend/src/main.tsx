import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { BoardPage } from './pages/BoardPage';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/boards/:id" element={<BoardPage />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);