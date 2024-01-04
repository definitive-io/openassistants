'use client';

import { OpenAssistantsChat } from '@definitive-io/openassistants-react';

export default function Home() {
  return (
    <main className="flex h-full flex-col items-center justify-between">
      <div className="relative flex w-full h-full overflow-hidden">
        <div className="group w-full pl-0 animate-in duration-300 ease-in-out peer-[[data-state=open]]:lg:pl-[250px] peer-[[data-state=open]]:xl:pl-[300px]">
          <OpenAssistantsChat
            api={`${
              process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            }/v1alpha/assistants/hooli/chat`}
            name="NBA Recap Writing Assistant"
            starterPrompts={[
              {
                title: 'Recap the Knicks game',
                prompt: 'Recap the Knicks game',
              },
              {
                title: 'Recap the Pacers game',
                prompt: 'Recap the Pacers game',
              },
              {
                title: 'Recap the Kings game',
                prompt: 'Recap the Kings game',
              },
            ]}
            welcomeMessage="Stay updated with last night's NBA games! This application offers concise recaps, focusing on team statistics and key player performances to summarize the game's results."
            getToken={() => Promise.resolve('token')}
          ></OpenAssistantsChat>
        </div>
      </div>
    </main>
  );
}
