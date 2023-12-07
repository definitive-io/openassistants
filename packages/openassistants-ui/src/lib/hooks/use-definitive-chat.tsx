import { useEffect, useState } from 'react';
import { applyPatch } from 'fast-json-patch';
import {
  EventSourceMessage,
  fetchEventSource,
} from '@microsoft/fetch-event-source';
import axios from 'axios';
import { Message } from '../../components/chat-models';

export interface UseChat {
  error: string | null;
  messages: Message[] | undefined;
  append: (message?: Message) => Promise<void>;
  stop: () => void;
  setMessages: (messages: Message[]) => void;
  isLoading: boolean;
}

let abortController = new AbortController();

class ApiError extends Error {
  code: string;
  detail: string;

  constructor(code: string, detail: string) {
    super(detail);
    this.code = code;
    this.detail = detail;
  }
}

export type ApiConfig = {
  baseUrl: string;
  buildHeaders: () => Promise<Record<string, string>>;
};

export const useDefinitiveChat = (
  apiConfig: ApiConfig,
  initialMessages: Message[]
): UseChat => {
  const [messages, setMessages] = useState(initialMessages);
  const [reloadFlag, setReloadFlag] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const stop = () => {
    abortController.abort();
    abortController = new AbortController();
  };

  const append = async (message?: Message) => {
    // const stream = false; // useful for development
    const stream = true;
    setError('');
    const headers = await apiConfig.buildHeaders();
    const newMessages = [...messages];
    if (message) {
      const newMessage = { ...message };
      newMessages.push(newMessage);
    }
    setMessages(newMessages);
    setIsLoading(true);

    const requestBody = {
      messages: newMessages,
      stream,
    };

    // const url = new URL(`${apiConfig.baseUrl}/v1alpha/sidekicks/mock/chat`);
    const url = new URL(apiConfig.baseUrl);
    if (!stream) {
      try {
        const response = await axios.post(url.href, requestBody, { headers });
        const respMessages = response.data.messages;
        setMessages([...newMessages, ...respMessages]);
      } catch (e) {
        if (e instanceof ApiError) {
          setError(e.detail || 'Unknown error');
        }
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // streaming
    const responseMessage = { messages: [] };
    try {
      await fetchEventSource(url.href, {
        method: 'POST',
        body: JSON.stringify(requestBody),
        headers: headers,
        onopen: async (response) => {
          if (!response.ok) {
            // eslint-disable-next-line no-magic-numbers
            if (response.status === 429) {
              throw new Error('rate limited');
            }
            throw new Error(`Bad Response Status Code ${response.status}`);
          }
        },
        onmessage: (event: EventSourceMessage) => {
          console.debug(`[EventSource: ${url.href}]`, event);
          if (!event.data || event.event === 'ping') {
            // keep alive message, ignore
            return;
          }
          const data = JSON.parse(event.data);
          if (data.error) {
            console.log('onmessage error', data.error);
            const apiError = new ApiError(data.error.code, data.error.detail);
            throw apiError;
          }
          applyPatch(responseMessage, data.patch);
          const { messages } = responseMessage;

          setMessages([...newMessages, ...messages]);
        },
        onerror: (err: unknown) => {
          console.log('onerror', err);
          throw err;
        },
        onclose: () => {
          // nothing
        },
        signal: abortController.signal,
        openWhenHidden: true,
      });
    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.detail || 'Unknown error');
      }
    } finally {
      setIsLoading(false);
    }
  };
  const setMessagesAndReload = async (messages: Message[]) => {
    setMessages(messages);
    setReloadFlag(true);
  };

  useEffect(() => {
    if (reloadFlag) {
      setReloadFlag(false);
      append();
    }
  }, [reloadFlag]);

  return {
    error,
    messages,
    setMessages: setMessagesAndReload,
    append,
    stop,
    isLoading,
  };
};
