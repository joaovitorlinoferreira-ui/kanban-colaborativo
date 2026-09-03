import React, { useState } from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { CardItem } from './CardItem';
import { Plus } from 'lucide-react';

interface ColumnProps {
  column: { id: number; title: string; cards: Array<any> };
  onAddCard: (columnId: number, title: string) => void;
  onDeleteCard: (cardId: number) => void;
}

export const BoardColumn: React.FC<ColumnProps> = ({ column, onAddCard, onDeleteCard }) => {
  const { setNodeRef } = useDroppable({ id: column.id });
  const [newCardTitle, setNewCardTitle] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCardTitle.trim()) return;
    onAddCard(column.id, newCardTitle);
    setNewCardTitle('');
    setIsAdding(false);
  };

  return (
    <div className="w-80 bg-gray-100 rounded-xl p-4 flex flex-col max-h-full">
      <h3 className="font-bold text-gray-700 text-sm mb-3 flex justify-between items-center">
        <span>{column.title}</span>
        <span className="text-xs bg-gray-200 px-2 py-0.5 rounded-full text-gray-600">
          {column.cards.length}
        </span>
      </h3>

      <div ref={setNodeRef} className="flex-1 overflow-y-auto space-y-2 min-h-[100px] pr-1">
        <SortableContext items={column.cards.map((c) => c.id)} strategy={verticalListSortingStrategy}>
          {column.cards.map((card) => (
            <CardItem key={card.id} card={card} onDelete={onDeleteCard} />
          ))}
        </SortableContext>
      </div>

      {isAdding ? (
        <form onSubmit={handleSubmit} className="mt-3">
          <input
            type="text"
            autoFocus
            placeholder="Título do card..."
            value={newCardTitle}
            onChange={(e) => setNewCardTitle(e.target.value)}
            className="w-full text-sm p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div className="flex gap-2 mt-2">
            <button type="submit" className="bg-indigo-600 text-white text-xs px-3 py-1.5 rounded-md hover:bg-indigo-700">
              Adicionar
            </button>
            <button type="button" onClick={() => setIsAdding(false)} className="text-xs text-gray-500 px-2 py-1.5">
              Cancelar
            </button>
          </div>
        </form>
      ) : (
        <button
          onClick={() => setIsAdding(true)}
          className="mt-3 flex items-center justify-center gap-1 w-full py-2 border border-dashed border-gray-300 rounded-lg text-xs font-semibold text-gray-500 hover:bg-gray-200 transition"
        >
          <Plus size={14} /> Adicionar Card
        </button>
      )}
    </div>
  );
};