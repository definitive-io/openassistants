import { cn } from '../lib/utils';
import { IconArrowRight, IconDefinitive, IconUser } from './ui/icons';
import { ChatMessageAction, ChatMessageActions } from './chat-message-actions';
import { useState } from 'react';
import React from 'react';
import { Message } from './chat-models';
import { Button, Separator, Textarea } from './ui';
import { DataframeTable } from './dataframe-table';
import { RenderVisMessage } from './plotly-vis';
import { FunctionForm } from './function-form';
import { ChatContent } from './chat-content';

export interface DefinitiveChatMessageProps {
  index: number;
  total: number;
  message: Message;
  onEdit?: (message: Message) => Promise<void>;
  append: (message?: Message) => Promise<void>;
  isLoading: boolean;
}

const getIcon = (message: Message) => {
  if (message.role === 'user') {
    return <IconUser />;
  }
  if (message.role === 'assistant') {
    return <IconDefinitive />;
  }
  if (message.role === 'function') {
    return <IconArrowRight />;
  }
  return null;
};

const isCollapsable = (message: Message): boolean => {
  return (
    message.role === 'function' ||
    (message.role === 'assistant' && !!message.function_call)
  );
};

function flattenMessageContent(message: Message): string {
  if("content" in message) {
    if(Array.isArray(message.content)) {
      let result = '';
      message.content.forEach((entry) => {
        if (entry.type === 'text') {
          result += entry.text + '\n';
        } else if (entry.type === 'image_url' && entry.filename) {
          result += 'File: "' + entry.filename + '"\n\n';
        }
      });
      return result.trim();
    } else {
      return message.content?.trim() || "";
    }
  }
  return ""
}

export function OpenAssistantsChatMessage({
  index,
  total,
  message,
  onEdit,
  isLoading,
  append,
  ...props
}: DefinitiveChatMessageProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [submitted, setSubmitted] = React.useState(false);
  const [editedMessageContent, setEditedMessageContent] = useState<string>('');
  const supportedActions: ChatMessageAction[] = [];
  if (!isCollapsable(message) && !isEditing) {
    supportedActions.push('copy');
  }
  if (message.role === 'user' && !isEditing && onEdit) {
    supportedActions.push('edit');
  }
  const outputs = 'outputs' in message ? message.outputs : null;
  // executed function call- ignore
  if (message.role === 'assistant' && message.function_call) {
    return <div></div>;
  }
  // completed input response from user- ignore
  if (message.role === 'user' && message.input_response) {
    return <div></div>;
  }
  return (
    <div>
      <div
        className={cn(
          'group relative flex items-start md:-ml-12 bg-highlight '
        )}
        {...props}
      >
        <div
          className={cn(
            'flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border shadow bg-background'
          )}
        >
          {message && getIcon(message)}
        </div>
        <div className={cn('flex flex-col')}>
          <div className="ml-4 flex-1 space-y-2 overflow-hidden px-1 text-primary">
            {isEditing && message.role === 'user' && (
              <div>
                <Textarea
                  className="w-full p-2 resize-y"
                  value={editedMessageContent}
                  onChange={(e) => setEditedMessageContent(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      setIsEditing(false);
                      onEdit &&
                        onEdit({
                          ...message,
                          content: editedMessageContent,
                        });
                    }
                  }}
                />
                <Button
                  variant="ghost"
                  onClick={() => {
                    setIsEditing(false);
                  }}
                >
                  Cancel
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setIsEditing(false);
                    onEdit &&
                      onEdit({
                        ...message,
                        content: editedMessageContent,
                      });
                  }}
                >
                  Save
                </Button>
              </div>
            )}
            {outputs &&
              outputs.map((output, i) => {
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
                      <RenderVisMessage
                        id={`message-${index}-output-${i}`}
                        data={output.visualization.data}
                        layout={output.visualization.layout}
                      />
                    )}
                    {output.type === 'text' && !isEditing && (
                      <ChatContent content={output.text} />
                    )}
                  </div>
                );
              })}
            {'content' in message && !submitted && (
              <div>
                <ChatContent content={flattenMessageContent(message)} />
                <ChatMessageActions
                  content={flattenMessageContent(message)}
                  actions={supportedActions}
                  onEditClicked={() => {
                    setIsEditing(true);
                    setEditedMessageContent(flattenMessageContent(message));
                  }}
                />
              </div>
            )}
            {message.role === 'assistant' && message.input_request && (
              // add padding
              <div className={cn('px-8')}>
                <FunctionForm
                  message={message}
                  submitted={submitted}
                  onSubmit={(values) => {
                    const newMessage = {
                      role: 'user' as const,
                      input_response: {
                        name: message.input_request!.name,
                        arguments: values,
                      },
                      content: '',
                    };
                    setSubmitted(true);
                    append(newMessage);
                  }}
                ></FunctionForm>
              </div>
            )}
          </div>
        </div>
      </div>
      {index < total - 1 && <Separator className="my-4 " />}
    </div>
  );
}
