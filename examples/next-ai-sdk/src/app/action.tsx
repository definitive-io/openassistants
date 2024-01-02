'use server';

import {
  AIStream,
  AIStreamCallbacksAndOptions,
  AIStreamParser,
  experimental_StreamingReactResponse,
  Message,
} from 'ai';
import { applyPatch } from 'fast-json-patch';

interface ApiMessage {
  role: string;
  outputs: any[];
}

export async function handler({
  messages,
  data,
}: {
  messages: Message[];
  data: Record<string, string>;
}) {
  const api = `${
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }/v1alpha/assistants/hooli/chat`;
  const fetchResponse = await fetch(api, {
    method: 'POST',
    body: JSON.stringify({ messages: messages, stream: true }),
    headers: {
      'Content-Type': 'application/json',
    },
  });
  const resp: { messages: ApiMessage[] } = {
    messages: [],
  };
  const stream = OpenAssistantsStream(fetchResponse, {
    onStart: async () => {
      console.log('Stream started');
    },
    onCompletion: async (completion) => {
      console.log('Completion completed');
    },
    onFinal: async (completion) => {
      console.log('Stream completed');
    },
    onToken: async (token) => {
      try {
        const json = JSON.parse(token);
        if (json.error) {
          console.log('json error', json.error);
          return;
        }
        if (json.patch) {
          applyPatch(resp, json.patch);
        }
      } catch (e) {
        console.log('Error parsing token', e);
      }
    },
  });

  return new experimental_StreamingReactResponse(stream, {
    ui({}) {
      // get the dataframe to show a simple example
      const fnMessage = resp.messages?.find((m) => m.role === 'function');
      const dataframe = fnMessage?.outputs?.find(
        (output) => output.type === 'dataframe'
      )?.dataframe;
      const content = fnMessage?.outputs?.find(
        (output) => output.type === 'text'
      )?.text;

      return (
        <div>
          {dataframe && (
            <div>
              <table>
                <thead>
                  <tr>
                    {dataframe.columns.map((c: string) => (
                      <th key={c}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataframe.data.map((r: string, i: number) => (
                    <tr key={i}>
                      {dataframe.columns.map((c: string, j: number) => (
                        <td key={c}>{r[j]}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {content && <div>{content}</div>}
        </div>
      );
    },
  });
}

function parseOpenAssistantsStream(): AIStreamParser {
  return (data) => {
    return data;
  };
}

function OpenAssistantsStream(
  res: Response,
  cb?: AIStreamCallbacksAndOptions
): ReadableStream {
  return AIStream(res, parseOpenAssistantsStream(), cb);
}
