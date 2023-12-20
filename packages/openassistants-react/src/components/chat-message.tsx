import remarkGfm from 'remark-gfm';

import { cn } from '../lib/utils';
import { CodeBlock } from './ui/codeblock';
import { MemoizedReactMarkdown } from './markdown';
import { IconArrowRight, IconDefinitive, IconUser } from './ui/icons';
import { ChatMessageAction, ChatMessageActions } from './chat-message-actions';
import { useState } from 'react';
import React from 'react';
import { Message } from './chat-models';
import { Button, Textarea } from './ui';

export interface DefinitiveChatMessageProps {
  message: Message;
  onEdit?: (message: Message) => Promise<void>;
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

function formatCode(input: string): string {
  const trimmed = input
    .replace('BEGIN_CODE', '')
    .replace('END_CODE', '')
    .trim();
  return trimmed
    .split(';')
    .map((line) => line.trim())
    .join(';\n');
}

export const getContent = (message: Message): string => {
  if (message.role === 'function') {
    const textOutput =
      message.outputs.find((output) => output.type === 'text') || {};
    //@ts-ignore
    return 'text' in textOutput ? (textOutput.text as string) : '';
  }
  if (message.role === 'user') {
    if (message.content) {
      return message.content;
    } else {
      return '';
    }
  }
  if (message.role === 'assistant') {
    if (message.function_call) {
      return '';
    }
  }
  if (message.role === 'assistant' && message.content) {
    return message.content;
  }
  return '';
};

export function OpenAssistantsChatMessage({
  message,
  onEdit,
  isLoading,
  ...props
}: DefinitiveChatMessageProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedMessageContent, setEditedMessageContent] = useState<string>('');
  const content = getContent(message);
  const supportedActions: ChatMessageAction[] = [];
  if (!isCollapsable(message) && !isEditing) {
    supportedActions.push('copy');
  }
  if (message.role === 'user' && !isEditing && onEdit) {
    supportedActions.push('edit');
  }
  if (!content) {
    return <div></div>;
  }
  return (
    <div
      className={cn(
        'group relative mb-4 flex items-start md:-ml-12 bg-highlight'
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
        {!isEditing && (
          <div>
            <MemoizedReactMarkdown
              className={`prose break-words prose-p:leading-relaxed prose-pre:p-0`}
              remarkPlugins={[remarkGfm]}
              components={{
                p({ children }) {
                  return <p className="mb-2 last:mb-0">{children}</p>;
                },
                code({ node, inline, className, children, ...props }) {
                  if (children.length) {
                    if (children[0] == '▍') {
                      return (
                        <span className="mt-1 animate-pulse cursor-default">
                          ▍
                        </span>
                      );
                    }

                    children[0] = (children[0] as string).replace('`▍`', '▍');
                  }

                  const match = /language-(\w+)/.exec(className || '');

                  if (inline) {
                    return (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  }
                  return (
                    <div>
                      {
                        <CodeBlock
                          key={Math.random()}
                          language={(match && match[1]) || ''}
                          value={String(children).replace(/\n$/, '')}
                          {...props}
                        />
                      }
                    </div>
                  );
                },
              }}
            >
              {content}
            </MemoizedReactMarkdown>

            {'content' in message && (
              <ChatMessageActions
                content={message.content}
                actions={supportedActions}
                onEditClicked={() => {
                  setIsEditing(true);
                  setEditedMessageContent(message.content || '');
                }}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
