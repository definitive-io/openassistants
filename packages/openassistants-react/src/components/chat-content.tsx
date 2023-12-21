import React from 'react';
import { MemoizedReactMarkdown } from './markdown';
import remarkGfm from 'remark-gfm';
import { CodeBlock } from './ui';

export interface ChatContentProps {
  content: string;
}

export const ChatContent = ({ content }: ChatContentProps) => {
  return (
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
                  <span className="mt-1 animate-pulse cursor-default">▍</span>
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
    </div>
  );
};
