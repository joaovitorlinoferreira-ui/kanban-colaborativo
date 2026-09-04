import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/client';

interface Board {
  id: number;
  title: string;
}

export const BoardsListPage: React.FC = () => {
  const [boards, setBoards] = useState<Board[]>([]);
  const [newBoardTitle, setNewBoardTitle] = useState('');
  const navigate = useNavigate();

  const fetchBoards = async () => {
    try {
      const response = await api.get('/boards/');
      setBoards(response.data);
    } catch (err) {
      console.error('Erro ao buscar boards:', err);
    }
  };

  useEffect(() => {
    fetchBoards();
  }, []);

  const handleCreateBoard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBoardTitle.trim()) return;
    try {
      await api.post('/boards/', { title: newBoardTitle });
      setNewBoardTitle('');
      fetchBoards();
    } catch (err) {
      console.error('Erro ao criar board:', err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Meus Quadros Kanban</h1>
        <button onClick={handleLogout} style={{ padding: '8px 16px' }}>Sair</button>
      </div>

      <form onSubmit={handleCreateBoard} style={{ margin: '20px 0', display: 'flex', gap: '10px' }}>
        <input
          type="text"
          placeholder="Nome do novo quadro..."
          value={newBoardTitle}
          onChange={(e) => setNewBoardTitle(e.target.value)}
          style={{ flex: 1, padding: '8px' }}
        />
        <button type="submit" style={{ padding: '8px 16px', background: '#28a745', color: '#fff', border: 'none' }}>
          Criar Quadro
        </button>
      </form>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {boards.map((board) => (
          <li key={board.id} style={{ padding: '12px', border: '1px solid #ddd', marginBottom: '8px', borderRadius: '4px' }}>
            <Link to={`/boards/${board.id}`} style={{ textDecoration: 'none', fontSize: '18px', fontWeight: 'bold' }}>
              {board.title}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};