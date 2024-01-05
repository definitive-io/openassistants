import * as React from 'react';
import Textarea from 'react-textarea-autosize';

import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { IconArrowElbow, IconUpload } from './ui/icons';
import { useEnterSubmit } from '../lib/hooks/use-enter-submit';

export interface PromptProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (value: string | {}[]) => Promise<void>;
  isLoading: boolean;
  placeholder?: string;
}

export function PromptForm({
  onSubmit,
  input,
  setInput,
  isLoading,
}: PromptProps) {
  const { formRef, onKeyDown } = useEnterSubmit();
  const inputRef = React.useRef<HTMLTextAreaElement>(null);
  const [uploadedFileBase64, setUploadedFileBase64] = React.useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      return;
    }
    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = reader.result;
      if (typeof base64 === 'string') {
        setUploadedFileBase64(base64);
      }
    };
  };

  return (
    <form
      onSubmit={async (e) => {
        e.preventDefault();
        if (!input?.trim() && !uploadedFileBase64) {
          return;
        }
        setInput('');
        if (uploadedFileBase64) {
          await onSubmit([
            {"type": "image_url", "image_url": uploadedFileBase64, "filename": uploadedFileName},
            {"type": "text", "text": input}
          ]);
          setUploadedFileBase64(null);
          setUploadedFileName(null);
        } else {
          await onSubmit(input);
        }
      }}
      ref={formRef}
    >
      <div className="relative flex max-h-60 w-full grow flex-col overflow-hidden bg-background px-8 sm:rounded-md sm:border sm:px-12 lg:min-w-600px">
        <div className="absolute left-4 top-4">
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileUpload}
          />
          <label htmlFor="file-upload">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  size="icon"
                  onClick={triggerFileInput}
                >
                  <IconUpload />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Upload image</TooltipContent>
            </Tooltip>
          </label>
        </div>
        <Textarea
          ref={inputRef}
          tabIndex={0}
          onKeyDown={onKeyDown}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Send a message."
          spellCheck={false}
          className="min-h-[60px] w-full resize-none bg-transparent px-4 py-[1.3rem] focus-within:outline-none sm:text-sm"
        />
        {uploadedFileName && (
          <div className="text-sm text-gray-500 px-4 py-2">
            File to upload: {uploadedFileName}
          </div>
        )}
        <div className="absolute right-0 top-4 sm:right-4">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="submit"
                size="icon"
                disabled={isLoading || input === ''}
              >
                <IconArrowElbow />
                <span className="sr-only">Send message</span>
              </Button>
            </TooltipTrigger>
            <TooltipContent>Send message</TooltipContent>
          </Tooltip>
        </div>
      </div>
    </form>
  );
}
