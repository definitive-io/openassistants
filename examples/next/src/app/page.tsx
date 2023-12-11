'use client';

import { OpenAssistantsChat } from '@definitive-io/openassistants-ui';

export default function Home() {
  return (
    <main className="flex h-full flex-col items-center justify-between">
      <div className="relative flex w-full h-full overflow-hidden">
        <div className="group w-full pl-0 animate-in duration-300 ease-in-out peer-[[data-state=open]]:lg:pl-[250px] peer-[[data-state=open]]:xl:pl-[300px]">
          <OpenAssistantsChat
            api={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}/v1alpha/assistants/hooli/chat`}
            name="Example Assistant"
            starterPrompts={[
              {
                title: 'Show recent purchases',
                prompt: 'Show recent purchases',
              },
              {
                title: 'Show spend per product',
                prompt: 'Show spend per product',
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
