'use client';

import { OpenAssistantsChat } from '@definitive-io/openassistants-react';

export default function Home() {
  return (
    <main className="flex h-full flex-col items-center justify-between">
      <div className="relative flex w-full h-full overflow-hidden">
        <div className="group w-full pl-0 animate-in duration-300 ease-in-out peer-[[data-state=open]]:lg:pl-[250px] peer-[[data-state=open]]:xl:pl-[300px]">
          <OpenAssistantsChat
            api={`https://openassistants-fast-api-server-pr-92.onrender.com/v1alpha/assistants/hooli/chat`}
            name="NBA Recap Writing Assistant"
            starterPrompts={[
              {
                title: 'Recap the Warriors game',
                prompt: 'Recap the Warriors game',
              },
              {
                title: 'Recap the Bucks game',
                prompt: 'Recap the Bucks game',
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
