import { FunctionForm } from './function-form';
import { Message } from './chat-models';
import React from 'react';
import { DataframeTable } from './dataframe-table';
import { IconSpinner, Separator } from './ui';
import { OpenAssistantsChatMessage, getContent } from './chat-message';
import { RenderVisMessage } from './plotly-vis';

export interface DefinitiveChatList {
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  append: (message?: Message) => Promise<void>;
  isLoading: boolean;
}

export function OpenAssistantsChatList({
  messages,
  setMessages,
  append,
  isLoading,
}: DefinitiveChatList) {
  if (!messages.length) {
    return null;
  }

  // This drops all messages after this one and replaces it with the new one
  const onEdit = async (i: number, updated: Message): Promise<void> => {
    const newMessages = messages.slice(0, i);
    newMessages.push(updated);
    setMessages(newMessages);
  };

  return (
    <div className="relative mx-auto max-w-2xl px-4">
      {messages.map((message, index) => {
        return (
          <div key={index}>
            <OpenAssistantsChatMessage
              key={index}
              total={messages.length}
              index={index}
              message={message}
              append={append}
              onEdit={(m) => onEdit(index, m)}
              isLoading={isLoading}
            />
          </div>
        );
      })}
      {isLoading && <IconSpinner className="mt-4"></IconSpinner>}
    </div>
  );
}
