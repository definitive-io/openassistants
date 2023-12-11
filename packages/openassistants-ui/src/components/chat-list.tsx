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
        const outputs = 'outputs' in message ? message.outputs : null;
        return (
          <div key={index}>
            {outputs &&
              outputs.map((output, i) => {
                console.log(`output.type=${output.type} output=${JSON.stringify(output)}`)
                return (
                  <div key={`message_${index}_output_${i}`} className="mb-4">
                    {output.type === 'dataframe' && (
                      <DataframeTable
                        key={`message_${index}_df_${i}`}
                        title={output.title || ''}
                        dataframe={output.dataframe}
                      ></DataframeTable>
                    )}
                    {output.type === 'visualization' && (
                      <RenderVisMessage id={`message-${index}-output-${i}`} data={output.visualization.data} layout={output.visualization.layout} />
                    )}
                  </div>
                );
              })}

            {getContent(message) && (
              <div key={index}>
                <OpenAssistantsChatMessage
                  key={index}
                  message={message}
                  onEdit={(m) => onEdit(index, m)}
                  isLoading={isLoading}
                />
                {index < messages.length - 1 && <Separator className="my-4 " />}
              </div>
            )}

            {message.role === 'assistant' && message.input_request && (
              <FunctionForm
                message={message}
                onSubmit={(values) => {
                  const newMessage = {
                    role: 'user' as const,
                    input_response: {
                      name: message.input_request!.name,
                      arguments: values,
                    },
                    content: '',
                  };
                  append(newMessage);
                }}
              ></FunctionForm>
            )}
          </div>
        );
      })}
      {isLoading && <IconSpinner className="mt-4"></IconSpinner>}
    </div>
  );
}
