import { FC, memo } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

import { IconCheck, IconCopy, IconDownload } from './icons';
import { Button } from './button';
import React from 'react';
import { useCopyToClipboard } from '../../lib/hooks/use-copy-to-clipboard';

interface Props {
  language: string;
  value: string;
}

interface languageMap {
  [key: string]: string | undefined;
}

export const programmingLanguages: languageMap = {
  javascript: '.js',
  python: '.py',
  java: '.java',
  c: '.c',
  cpp: '.cpp',
  'c++': '.cpp',
  'c#': '.cs',
  ruby: '.rb',
  php: '.php',
  swift: '.swift',
  'objective-c': '.m',
  kotlin: '.kt',
  typescript: '.ts',
  go: '.go',
  perl: '.pl',
  rust: '.rs',
  scala: '.scala',
  haskell: '.hs',
  lua: '.lua',
  shell: '.sh',
  sql: '.sql',
  html: '.html',
  css: '.css',
  json: '.json',
  // add more file extensions here, make sure the key is same as language prop in CodeBlock.tsx component
};

export const generateRandomString = (length: number, lowercase = false) => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXY3456789'; // excluding similar looking characters like Z, 2, I, 1, O, 0
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return lowercase ? result.toLowerCase() : result;
};

const CodeBlock: FC<Props> = memo(({ language, value }) => {
  const { isCopied, copyToClipboard } = useCopyToClipboard({ timeout: 2000 });

  const downloadAsFile = () => {
    if (typeof window === 'undefined') {
      return;
    }
    const fileExtension = programmingLanguages[language] || '.file';
    const suggestedFileName = `file-${generateRandomString(
      3,
      true
    )}${fileExtension}`;
    const fileName = window.prompt('Enter file name' || '', suggestedFileName);

    if (!fileName) {
      // User pressed cancel on prompt.
      return;
    }

    const blob = new Blob([value], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = fileName;
    link.href = url;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const onCopy = () => {
    if (isCopied) return;
    copyToClipboard(value);
  };

  return (
    <div className="relative w-full font-sans bg-gray-200">
      <div className="flex w-full items-center justify-between px-6 py-2 pr-4">
        <span className="text-xs lowercase text-primary">{language}</span>
        <div className="flex items-center space-x-1">
          <Button
            variant="ghost"
            className="text-primary text-xs hover:bg-gray-300 hover:text-primary"
            onClick={downloadAsFile}
            size="icon"
          >
            <IconDownload />
            <span className="sr-only">Download</span>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-primary text-xs hover:bg-gray-300 hover:text-primary"
            onClick={onCopy}
          >
            {isCopied ? <IconCheck /> : <IconCopy />}
            <span className="sr-only">Copy code</span>
          </Button>
        </div>
      </div>
      <SyntaxHighlighter
        language={language}
        PreTag="div"
        showLineNumbers
        wrapLines={true}
        customStyle={{
          margin: 0,
          width: '100%',
          background: 'transparent',
          padding: '1.5rem 1rem',
        }}
        codeTagProps={{
          style: {
            fontSize: '0.9rem',
            fontFamily: 'var(--font-mono)',
          },
        }}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
});
CodeBlock.displayName = 'CodeBlock';

export { CodeBlock };
