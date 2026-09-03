import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Trash2 } from 'lucide-react';

interface CardItemProps {
  card: { id: number; title: string; description?: string };
  onDelete: (id: number) => void;
}

export const CardItem: React.FC<CardItemProps> = ({ card, onDelete }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: card.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-white p-3 rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing flex justify-between items-start group hover:border-indigo-300"
    >
      <div>
        <h4 className="text-sm font-semibold text-gray-800">{card.title}</h4>
        {card.description && (
          <p className="text-xs text-gray-500 mt-1">{card.description}</p>
        )}
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(card.id);
        }}
        className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-600 transition"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
};