'use client';

import { useChat } from 'ai/react';

export function Chat({ handler }: { handler: any }) {
  const { data, messages, input, handleInputChange, handleSubmit } = useChat({
    api: handler,
  });
  return (
    <div className="flex flex-col w-full max-w-md py-24 mx-auto stretch">
      <ul>
        {messages.map((m, index) => (
          <li key={index}>
            {m.role === 'user' ? 'User: ' : 'AI: '}
            {m.role === 'user' ? m.content : m.ui}
          </li>
        ))}
      </ul>

      <form onSubmit={handleSubmit}>
        <input
          className="fixed bottom-0 w-full max-w-md p-2 mb-8 border border-gray-300 text-black rounded shadow-xl"
          placeholder="Show recent purchases"
          value={input}
          onChange={handleInputChange}
          autoFocus
        />
      </form>
    </div>
  );
}
