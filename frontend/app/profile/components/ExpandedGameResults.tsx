import { useState } from 'react';
import { GameHistoryItem } from '@/shared/schemas';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/cjs/styles/prism';

interface ExpandedGameResultsProps {
  game: GameHistoryItem;
}

export default function ExpandedGameResults({ game } : ExpandedGameResultsProps) {
  const [selectedParticipant, setSelectedParticipant] = useState(game.participants[0]);

  return (
    <div className='flex flex-col mt-4'>
      <div className='flex items-center justify-start gap-4'>
        {game.participants.map((participant) => (
          <button 
            key={participant.player_name}
            className={`pb-2 transition-colors duration-200 cursor-pointer ${
              selectedParticipant.player_name === participant.player_name 
                ? 'border-b-2 border-blue-500 text-blue-600 font-semibold' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
            onClick={() => setSelectedParticipant(participant)}
          >
            {participant.player_name} results
          </button>
        ))}
      </div>
      
      <div className='p-4 mt-4 border rounded-lg bg-background2'>
        <h3 className='mb-2 text-lg font-semibold'>
          {selectedParticipant.player_name}'s Results
        </h3>
        
        {/* Replace this with your actual content structure */}
        <div className='space-y-2'>
          <p><strong>Time:</strong> {selectedParticipant.implement_time || 'N/A'}</p>
          <p><strong>Complexity:</strong> {selectedParticipant.time_complexity || 'N/A'}</p>
          <p><strong>Score:</strong> {selectedParticipant.final_time || 'N/A'}</p>
          <h3>Code:</h3>
          <SyntaxHighlighter
          language={"python"}
          style={vscDarkPlus}
          showLineNumbers={true}
          wrapLines={true}
          customStyle={{
            borderRadius: '8px',
            fontSize: '14px',
          }}
        >
          {selectedParticipant.player_code}
        </SyntaxHighlighter>

          {/* Add more participant-specific content here */}
        </div>
      </div>
    </div>
  );
}