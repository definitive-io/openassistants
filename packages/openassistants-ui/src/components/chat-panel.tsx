import { Button } from './ui/button';
import { PromptForm } from './prompt-form';
import { IconDownload, IconRefresh, IconStop } from './ui/icons';
import { useState } from 'react';
import React from 'react';
import { useCopyToClipboard } from '../lib/hooks/use-copy-to-clipboard';
import { Message } from './chat-models';

export interface ChatPanelProps {
  isLoading: boolean;
  stop: () => void;
  append: (value: string) => Promise<void>;
  messages: Message[];
  onSave?: () => Promise<void>;
  saveDisabled: boolean;
  clearMessages: (() => Promise<void>) | undefined;
  v1alpha: boolean;
}

export function ChatPanel({
  isLoading,
  stop,
  append,
  messages,
  saveDisabled,
  onSave,
  clearMessages,
}: ChatPanelProps) {
  const [inputPrompt, setInputPrompt] = useState<string>('');

  return (
    <div className="shrink-0 inset-x-0 bottom-0 bg-gradient-to-b from-muted/10 from-10% to-muted/30 to-50%">
      <div className="mx-auto sm:max-w-2xl sm:px-4">
        <div className="flex items-center justify-center">
          <div className="flex h-10 items-center justify-center text-primary">
            {isLoading && (
              <Button
                variant="outline"
                onClick={() => stop()}
                className="bg-background"
              >
                <IconStop className="mr-2" />
                Stop generating
              </Button>
            )}
          </div>
          <div className="flex h-10 items-center justify-center text-primary">
            {!isLoading && messages && !!messages.length && onSave && (
              <Button
                variant="outline"
                disabled={saveDisabled}
                onClick={() => {
                  onSave();
                }}
                className="bg-background"
              >
                <IconDownload className="mr-2" />
                Save
              </Button>
            )}
          </div>
          <div className="flex h-10 items-center justify-center text-primary">
            {!isLoading && messages && !!messages.length && clearMessages && (
              <Button
                variant="outline"
                onClick={() => {
                  clearMessages();
                }}
                className="bg-background"
              >
                <IconRefresh className="mr-2" />
                Clear Messages
              </Button>
            )}
          </div>
        </div>
        <div className="space-y-4 border-t bg-background px-4 py-2 shadow-lg sm:rounded-t-xl sm:border md:py-4">
          <PromptForm
            onSubmit={async (value) => {
              await append(value);
            }}
            input={inputPrompt}
            setInput={setInputPrompt}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
