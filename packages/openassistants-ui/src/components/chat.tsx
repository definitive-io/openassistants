import { cn, nanoid } from '../lib/utils';
import { ChatPanel } from './chat-panel';
import { SuggestedPrompts } from './empty-screen';
import { ChatScrollAnchor } from './chat-scroll-anchor';
import { ExamplePrompt, Message } from './chat-models';
import React from 'react';
import { useDefinitiveChat } from '../lib/hooks/use-definitive-chat';
import { Label } from '@radix-ui/react-label';
import { Button, IconArrowRight } from './ui';
import { OpenAssistantsChatList } from './chat-list';

export interface DefinitiveChatProps {
  // Name of the assistant
  name: string;
  // Welcome message to display when the chat is empty
  welcomeMessage: string;
  // Example prompts to display when the chat is empty
  starterPrompts: ExamplePrompt[];
  // Initial messages to display. Useful if loading a conversation from a database
  initialMessages?: Message[];
  // Api route that handles chat requests
  api: string;
  // A promise that resolves a token to be passed as a bearer token to the api
  getToken: () => Promise<string>;
}

export function OpenAssistantsChat({
  name,
  welcomeMessage,
  starterPrompts,
  initialMessages,
  api,
  getToken,
}: DefinitiveChatProps): React.ReactElement {
  const buildHeaders = (
    getToken: () => Promise<string>
  ): (() => Promise<Record<string, string>>) => {
    return async () => {
      const token = await getToken();
      return {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      };
    };
  };

  const SIDEKICK_CHAT_WITH_GOLDEN_PATH = `${api}`;

  const { messages, setMessages, append, stop, isLoading, error } =
    useDefinitiveChat(
      {
        baseUrl: SIDEKICK_CHAT_WITH_GOLDEN_PATH,
        buildHeaders: buildHeaders(getToken),
      },
      initialMessages?.filter((m) => !!m && !!m.role) || []
    );

  const stopExecuting = () => {
    stop();
  };

  const appendMessageValue = async (value?: string): Promise<void> => {
    await append({
      role: 'user',
      content: value,
    });
  };

  const lastMessage =
    messages && messages.length > 0 && messages[messages.length - 1];
  const lastOutputs =
    lastMessage && 'outputs' in lastMessage ? lastMessage.outputs : null;
  const followupsArr = lastOutputs?.filter(
    (output) => output.type === 'follow_ups'
  );
  const followupField =
    followupsArr && followupsArr.length > 0 ? followupsArr[0] : [];
  const followups =
    'follow_ups' in followupField
      ? (followupField.follow_ups as ExamplePrompt[])
      : [];

  return (
    <div className="flex flex-col h-full flex-1 bg-background">
      <div className={cn('pb-[200px] pt-4 md:pt-10 flex-1 overflow-auto')}>
        {messages && (
          <OpenAssistantsChatList
            messages={messages}
            setMessages={setMessages}
            append={append}
            isLoading={isLoading}
          />
        )}
        <ChatScrollAnchor trackVisibility={isLoading} />
        {(!messages || messages.length === 0) && (
          <SuggestedPrompts
            key={'suggestions'}
            name={name}
            welcomeMessage={welcomeMessage}
            prompts={starterPrompts}
            append={appendMessageValue}
          />
        )}

        {error && <Label className="px-8 text-destructive">{error}</Label>}
      </div>
      <div
        className={cn(
          'max-w-2xl w-full mt-auto flex flex-col mx-auto opacity-80'
        )}
      >
        {!isLoading &&
          followups?.map(({ title, prompt }) => (
            <div key={title}>
              <Button
                variant="link"
                type="button"
                onClick={() => appendMessageValue(prompt)}
              >
                <IconArrowRight className="mr-2 text-muted-foreground" />
                {title}
              </Button>
            </div>
          ))}
      </div>

      <ChatPanel
        isLoading={isLoading}
        stop={stopExecuting}
        append={appendMessageValue}
        saveDisabled={false}
        messages={messages as any}
        clearMessages={
          followups?.length
            ? undefined
            : async () => {
                setMessages([]);
              }
        }
        v1alpha={true}
      />
    </div>
  );
}
