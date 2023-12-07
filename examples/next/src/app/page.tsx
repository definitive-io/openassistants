'use client';

import { OpenAssistantsChat } from '@openassistants/ui';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="relative flex h-[calc(100vh_-_theme(spacing.16))] overflow-hidden">
        <div className="group w-full overflow-auto pl-0 animate-in duration-300 ease-in-out peer-[[data-state=open]]:lg:pl-[250px] peer-[[data-state=open]]:xl:pl-[300px]">
          <OpenAssistantsChat
            api="http://localhost:8000/v1alpha/assistants/test/chat"
            name="Example Assistant"
            starterPrompts={[
              {
                title: 'Show recent purchases',
                prompt: 'Show recent purchases',
              },
            ]}
            welcomeMessage="This is a simple starter for deploying a nextjs app with an open assistant chat widget. This is configured to use the example library which builds off a couple csv of employee and purchase data"
            getToken={() => Promise.resolve('token')}
          ></OpenAssistantsChat>
        </div>
      </div>
    </main>
  );
}
