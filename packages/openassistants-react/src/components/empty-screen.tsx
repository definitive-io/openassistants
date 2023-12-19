import { ExamplePrompt } from './chat-models';
import { Button } from './ui/button';
import { IconArrowRight } from './ui/icons';
import React from 'react';

export function SuggestedPrompts({
  name,
  welcomeMessage,
  prompts,
  append,
}: {
  name?: string;
  welcomeMessage?: string;
  prompts: ExamplePrompt[];
  append: (value: string) => Promise<void>;
}) {
  return (
    <div className="mx-auto max-w-2xl px-4 mb-4">
      <div className="rounded-lg border bg-background p-8">
        {name && [
          <h1 key={name} className="mb-2 text-lg font-semibold text-primary">
            {name}
          </h1>,
        ]}
        {welcomeMessage && (
          <p className="leading-normal text-muted-foreground">
            {welcomeMessage}
          </p>
        )}
        {prompts && prompts.length > 0 && (
          <div className="mt-4 flex flex-col items-start space-y-2 p-2">
            {prompts.map((message, index) => (
              <Button
                key={index}
                variant="link"
                className="h-auto p-0 text-base"
                onClick={() => append(message.prompt)}
              >
                <IconArrowRight className="mr-2 text-muted-foreground" />
                {message.title}
              </Button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
