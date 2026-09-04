import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

export const LoginForm: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isRegister) {
        await api.post('/auth/register', { email, password, name });
      }
      
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      localStorage.setItem('token', response.data.access_token);
      navigate('/boards');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ocorreu um erro ao autenticar.');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>{isRegister ? 'Criar Conta' : 'Login'}</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        {isRegister && (
          <div style={{ marginBottom: '10px' }}>
            <label>Nome:</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} required style={{ width: '100%', padding: '8px' }} />
          </div>
        )}
        <div style={{ marginBottom: '10px' }}>
          <label>Email:</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ width: '100%', padding: '8px' }} />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label>Senha:</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={{ width: '100%', padding: '8px' }} />
        </div>
        <button type="submit" style={{ width: '100%', padding: '10px', background: '#007bff', color: '#fff', border: 'none', borderRadius: '4px' }}>
          {isRegister ? 'Cadastrar' : 'Entrar'}
        </button>
      </form>
      <p style={{ marginTop: '15px', cursor: 'pointer', color: '#007bff' }} onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? 'Já tem uma conta? Entre aqui' : 'Não tem conta? Crie uma aqui'}
      </p>
    </div>
  );
};