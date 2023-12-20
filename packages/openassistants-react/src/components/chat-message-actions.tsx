import { Button } from './ui/button';
import { IconCheck, IconCopy, IconEdit } from './ui/icons';
import { cn } from '../lib/utils';
import React from 'react';
import { useCopyToClipboard } from '../lib/hooks/use-copy-to-clipboard';

export type ChatMessageAction = 'copy' | 'edit';
interface ChatMessageActionsProps extends React.ComponentProps<'div'> {
  content?: string;
  actions: ChatMessageAction[];
  onEditClicked: () => void;
}

export function ChatMessageActions({
  content,
  actions,
  onEditClicked,
  className,
  ...props
}: ChatMessageActionsProps) {
  const { isCopied, copyToClipboard } = useCopyToClipboard({ timeout: 2000 });

  const onCopy = () => {
    if (isCopied) return;
    copyToClipboard(content || '');
  };

  return (
    <div
      className={cn(
        'flex items-center justify-end transition-opacity group-hover:opacity-100 md:absolute md:-right-20 md:-top-2 md:opacity-0 text-primary',
        className
      )}
      {...props}
    >
      {actions.includes('edit') && (
        <Button variant="ghost" size="icon" onClick={onEditClicked}>
          <IconEdit></IconEdit>
          <span className="sr-only">Edit message</span>
        </Button>
      )}
      {actions.includes('copy') && (
        <Button variant="ghost" size="icon" onClick={onCopy}>
          {isCopied ? <IconCheck /> : <IconCopy />}
          <span className="sr-only">Copy message</span>
        </Button>
      )}
    </div>
  );
}
