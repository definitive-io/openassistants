import Image from 'next/image';
import { Chat } from './chat';
import { handler } from './action';

export const runtime = 'edge';

export default function Page() {
  return <Chat handler={handler} />;
}
