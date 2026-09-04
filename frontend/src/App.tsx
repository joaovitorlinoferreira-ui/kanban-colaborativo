import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { LoginForm } from './components/LoginForm';
import { BoardsListPage } from './pages/BoardsListPage';
import BoardPage from './pages/BoardPage';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" replace />;
};

export const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginForm />} />
      <Route path="/boards" element={<PrivateRoute><BoardsListPage /></PrivateRoute>} />
      <Route path="/boards/:id" element={<PrivateRoute><BoardPage /></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/boards" replace />} />
    </Routes>
  );
};

export default App;