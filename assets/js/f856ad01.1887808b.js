"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[809],{4669:(e,s,t)=>{t.r(s),t.d(s,{assets:()=>l,contentTitle:()=>o,default:()=>u,frontMatter:()=>i,metadata:()=>r,toc:()=>c});var n=t(5893),a=t(1151);const i={slug:"assistants-not-agents",title:"Assistants not Agents",authors:["rick","dan"],tags:["facebook","hello","docusaurus"]},o=void 0,r={permalink:"/openassistants/blog/assistants-not-agents",editUrl:"https://github.com/definitive-io/openassistants/blog/2023-12-8-assistants-not-agents/index.md",source:"@site/blog/2023-12-8-assistants-not-agents/index.md",title:"Assistants not Agents",description:"In the fast-evolving world of AI systems, the distinction between building AI assistants and autonomous agents has become crucial. Recent insights from Dharmesh Shah highlight the inherent challenges with AI agents and why a more focused approach is preferable.",date:"2023-12-08T00:00:00.000Z",formattedDate:"December 8, 2023",tags:[{label:"facebook",permalink:"/openassistants/blog/tags/facebook"},{label:"hello",permalink:"/openassistants/blog/tags/hello"},{label:"docusaurus",permalink:"/openassistants/blog/tags/docusaurus"}],readingTime:3.43,hasTruncateMarker:!1,authors:[{name:"Rick Lamers",title:"Core contributor of OpenAssistants",url:"https://github.com/ricklamers",imageURL:"https://avatars.githubusercontent.com/u/1309307?v=4",key:"rick"},{name:"Dan Loman",title:"Core contributor of OpenAssistants",url:"https://github.com/dloman118",imageURL:"https://avatars.githubusercontent.com/u/99347459?v=4",key:"dan"}],frontMatter:{slug:"assistants-not-agents",title:"Assistants not Agents",authors:["rick","dan"],tags:["facebook","hello","docusaurus"]},unlisted:!1},l={authorsImageUrls:[void 0,void 0]},c=[{value:"The Pitfall of Autonomous Agents",id:"the-pitfall-of-autonomous-agents",level:4},{value:"The Advantage of AI Assistants",id:"the-advantage-of-ai-assistants",level:4},{value:"Launching <code>OpenAssistants</code>",id:"launching-openassistants",level:4},{value:"Conclusion",id:"conclusion",level:4}];function h(e){const s={a:"a",code:"code",em:"em",h4:"h4",img:"img",li:"li",ol:"ol",p:"p",strong:"strong",ul:"ul",...(0,a.a)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsxs)(s.p,{children:["In the fast-evolving world of AI systems, the distinction between building AI assistants and autonomous agents has become crucial. Recent insights from ",(0,n.jsx)(s.a,{href:"https://agent.ai/p/why-most-agent-ais-dont-work-yet",children:"Dharmesh Shah"})," highlight the inherent challenges with AI agents and why a more focused approach is preferable."]}),"\n",(0,n.jsx)(s.h4,{id:"the-pitfall-of-autonomous-agents",children:"The Pitfall of Autonomous Agents"}),"\n",(0,n.jsx)(s.p,{children:"AI agents, like those in projects such as AutoGPT and BabyAGI, are designed to function autonomously, handling a series of tasks without human intervention. This sounds ideal, but there's a catch. These agents rely on imperfect Large Language Models (LLMs) like GPT to interpret goals and execute tasks. While LLMs are incredibly advanced, they're not infallible. They have an inherent error rate, which might seem negligible at a glance but can significantly impact an agent's performance."}),"\n",(0,n.jsx)(s.p,{children:"For instance, if an LLM has a 95% success rate for each task, the cumulative success rate drops alarmingly with each additional task an agent undertakes. The mathematics behind this shows that even with a high individual task success rate, the overall reliability of an agent can diminish rapidly, reducing its effectiveness to a mere coin toss in complex scenarios. This is particularly problematic for general-purpose agents trying to cater to diverse functions."}),"\n",(0,n.jsxs)("blockquote",{class:"twitter-tweet",children:[(0,n.jsx)("p",{lang:"en",dir:"ltr",children:"AI agents like that are also prone to all kinds of disastrous security holes that aren't nearly as harmful to copilots - I think that's a major reason we haven't seen a breakout application of that form of agent yet, whereas copilots are being used successfully on a daily basis"}),"\u2014 Simon Willison (@simonw) ",(0,n.jsx)("a",{href:"https://twitter.com/simonw/status/1733916061928686040?ref_src=twsrc%5Etfw",children:"December 10, 2023"})]}),"\n",(0,n.jsx)(s.h4,{id:"the-advantage-of-ai-assistants",children:"The Advantage of AI Assistants"}),"\n",(0,n.jsx)(s.p,{children:"This is where AI assistants come into the limelight. Unlike their autonomous counterparts, AI assistants are designed to perform specific tasks, one at a time, with human interaction playing a central role. This approach has several advantages:"}),"\n",(0,n.jsxs)(s.ol,{children:["\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:[(0,n.jsx)(s.strong,{children:"Reduced Error Rate"}),": By focusing on specific tasks, AI assistants can minimize the cumulative error rate. A narrower scope means less room for errors to compound."]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:[(0,n.jsx)(s.strong,{children:"Human Oversight"}),": AI assistants can work in tandem with humans, allowing for real-time feedback and corrections. This not only ensures more accurate outcomes but also helps in refining the AI's learning process."]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:[(0,n.jsx)(s.strong,{children:"Specialized Functionality"}),": Tailoring an AI assistant to specific use-cases means it can be optimized for those tasks, resulting in a more efficient and effective performance."]}),"\n"]}),"\n",(0,n.jsxs)(s.li,{children:["\n",(0,n.jsxs)(s.p,{children:[(0,n.jsx)(s.strong,{children:"Flexibility and Control"}),": With AI assistants, users maintain control, dictating the pace and direction of the task. This leads to a more user-friendly experience, as the assistant can adapt to the user's needs and preferences."]}),"\n"]}),"\n"]}),"\n",(0,n.jsxs)(s.h4,{id:"launching-openassistants",children:["Launching ",(0,n.jsx)(s.code,{children:"OpenAssistants"})]}),"\n",(0,n.jsxs)(s.p,{children:["That's where ",(0,n.jsx)(s.code,{children:"openassistants"})," comes in. We aim to make it easier to develop robust assistants that rely on function calling for performing actions and retrieving information into a conversational context. With a human in the loop these systems can be ",(0,n.jsx)(s.em,{children:"useful"})," and ",(0,n.jsx)(s.em,{children:"reliable"}),". Our goal is to make the process of building robust assistants as easy as possible by putting as much boilerplate and common components into a set of extensible and composible libraries."]}),"\n",(0,n.jsx)(s.p,{children:"We're launching with three packages:"}),"\n",(0,n.jsxs)(s.ul,{children:["\n",(0,n.jsxs)(s.li,{children:[(0,n.jsx)(s.code,{children:"openassistants"})," the core library responsible for the main function calling / message generating runtime"]}),"\n",(0,n.jsxs)(s.li,{children:[(0,n.jsx)(s.code,{children:"openassistants-fastapi"})," a set of FastAPI routes used for interacting with the core runtime loop through a REST API"]}),"\n",(0,n.jsxs)(s.li,{children:[(0,n.jsx)(s.code,{children:"openassistants-ui"})," an example chat client that supports rich streaming outputs like tables, plots, form inputs and text."]}),"\n"]}),"\n",(0,n.jsx)(s.p,{children:"The project is built on top of LangChain and we will soon support more sophisticated RAG features based on LlamaIndex. Our goal is to be the open alternative to the AssistantsAPI that can operate against any LLM: both Open Source LLMs like fine-tuned Llama's focused on function calling and proprietary models with e.g. native support for function calling."}),"\n",(0,n.jsx)(s.p,{children:(0,n.jsx)(s.img,{src:t(7731).Z+"",width:"841",height:"683"})}),"\n",(0,n.jsx)(s.h4,{id:"conclusion",children:"Conclusion"}),"\n",(0,n.jsx)(s.p,{children:"In conclusion, while the allure of fully autonomous AI agents is undeniable, the current state of technology suggests a more measured approach. Building AI assistants that excel in specific tasks and work in harmony with human users is not just practical but also more aligned with our current technological capabilities. This approach promises a more reliable AI experience that leads to experiences that we can actually deploy with confidence in production today."})]})}function u(e={}){const{wrapper:s}={...(0,a.a)(),...e.components};return s?(0,n.jsx)(s,{...e,children:(0,n.jsx)(h,{...e})}):h(e)}},7731:(e,s,t)=>{t.d(s,{Z:()=>n});const n=t.p+"assets/images/openassistants-16feeb0a171a4fa49bae23435f235089.png"},1151:(e,s,t)=>{t.d(s,{Z:()=>r,a:()=>o});var n=t(7294);const a={},i=n.createContext(a);function o(e){const s=n.useContext(i);return n.useMemo((function(){return"function"==typeof e?e(s):{...s,...e}}),[s,e])}function r(e){let s;return s=e.disableParentContext?"function"==typeof e.components?e.components(a):e.components||a:o(e.components),n.createElement(i.Provider,{value:s},e.children)}}}]);