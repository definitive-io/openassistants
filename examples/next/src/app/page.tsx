'use client';

import { OpenAssistantsChat } from '@definitive-io/openassistants-ui';

export default function Home() {
  return (
    <main className="flex h-full flex-col items-center justify-between">
      <div className="relative flex w-full h-full overflow-hidden">
        <div className="group w-full pl-0 animate-in duration-300 ease-in-out peer-[[data-state=open]]:lg:pl-[250px] peer-[[data-state=open]]:xl:pl-[300px]">
          <OpenAssistantsChat
<<<<<<< Updated upstream
            api={`${
              process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            }/v1alpha/assistants/hooli/chat`}
            name="Chevrolet of Watsonville Chat Team"
=======
            api={`https://openassistants-fast-api-server-pr-56.onrender.com/v1alpha/assistants/hooli/chat`}
            name="Example Assistant"
>>>>>>> Stashed changes
            starterPrompts={[
              {
                title: 'Display store hours',
                prompt: 'Display store hours',
              },
              {
                title: 'See Inventory',
                prompt: 'See Inventory',
              },
              {
                title: 'Contact us',
                prompt: 'Contact us',
              },
            ]}
            welcomeMessage="Good afternoon! Welcome to Chevrolet of Watsonville. How can I assist you today in your vehicle search?"
            getToken={() => Promise.resolve('token')}
          ></OpenAssistantsChat>
        </div>
      </div>
    </main>
  );
}
