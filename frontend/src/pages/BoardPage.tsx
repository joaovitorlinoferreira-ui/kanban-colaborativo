import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, DragEndEvent, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import api from '../api/client';
import { useBoardSocket } from '../hooks/useBoardSocket';
import { BoardColumn } from '../components/BoardColumn';
import { ArrowLeft } from 'lucide-react';

export const BoardPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [board, setBoard] = useState<any>(null);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const fetchBoard = async () => {
    try {
      const res = await api.get(`/boards/${id}`);
      setBoard(res.data);
    } catch (err) {
      navigate('/boards');
    }
  };

  useEffect(() => {
    fetchBoard();
  }, [id]);

  useBoardSocket(id, (event) => {
    if (['CARD_CREATED', 'CARD_MOVED', 'CARD_DELETED'].includes(event)) {
      fetchBoard();
    }
  });

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || !board) return;

    const cardId = Number(active.id);
    const targetColumnId = Number(over.id);

    const previousBoard = JSON.parse(JSON.stringify(board));

    setBoard((prev: any) => {
      let movedCard: any = null;
      const newCols = prev.columns.map((col: any) => {
        const remainingCards = col.cards.filter((c: any) => {
          if (c.id === cardId) {
            movedCard = c;
            return false;
          }
          return true;
        });
        return { ...col, cards: remainingCards };
      });

      return {
        ...prev,
        columns: newCols.map((col: any) => {
          if (col.id === targetColumnId && movedCard) {
            return { ...col, cards: [...col.cards, movedCard] };
          }
          return col;
        }),
      };
    });

    try {
      await api.put(`/cards/${cardId}/move`, {
        target_column_id: targetColumnId,
        new_order: 0,
      });
    } catch (err) {
      setBoard(previousBoard);
    }
  };

  const handleAddCard = async (columnId: number, title: string) => {
    await api.post(`/cards/column/${columnId}`, { title });
    fetchBoard();
  };

  const handleDeleteCard = async (cardId: number) => {
    await api.delete(`/cards/${cardId}`);
    fetchBoard();
  };

  if (!board) return <div className="p-8">Carregando quadro...</div>;

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate('/boards')} className="text-gray-500 hover:text-gray-800">
          <ArrowLeft size={18} />
        </button>
        <h1 className="text-xl font-bold text-gray-800">{board.title}</h1>
      </header>

      <main className="flex-1 overflow-x-auto p-6">
        <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
          <div className="flex gap-6 h-full items-start">
            {board.columns.map((column: any) => (
              <BoardColumn
                key={column.id}
                column={column}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </div>
        </DndContext>
      </main>
    </div>
  );
};