"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[840],{468:(e,t,s)=>{s.r(t),s.d(t,{assets:()=>d,contentTitle:()=>r,default:()=>l,frontMatter:()=>a,metadata:()=>o,toc:()=>p});var n=s(7624),i=s(2172);const a={sidebar_position:1},r="Getting started",o={id:"getting-started",title:"Getting started",description:"Let's discover OpenAssistants in less than 5 minutes.",source:"@site/docs/getting-started.md",sourceDirName:".",slug:"/getting-started",permalink:"/openassistants/docs/getting-started",draft:!1,unlisted:!1,editUrl:"https://github.com/definitive-io/openassistants/docs/getting-started.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1},sidebar:"tutorialSidebar",next:{title:"Live demo",permalink:"/openassistants/docs/live-demo"}},d={},p=[{value:"Step 1: A simple FastAPI server based on OpenAssistants",id:"step-1-a-simple-fastapi-server-based-on-openassistants",level:2},{value:"Step 2: Defining the library and Assistant",id:"step-2-defining-the-library-and-assistant",level:2},{value:"Step 3: Using it through the UI",id:"step-3-using-it-through-the-ui",level:2}];function c(e){const t={a:"a",code:"code",h1:"h1",h2:"h2",img:"img",p:"p",pre:"pre",strong:"strong",...(0,i.M)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(t.h1,{id:"getting-started",children:"Getting started"}),"\n",(0,n.jsxs)(t.p,{children:["Let's discover ",(0,n.jsx)(t.strong,{children:"OpenAssistants in less than 5 minutes"}),"."]}),"\n",(0,n.jsx)(t.h2,{id:"step-1-a-simple-fastapi-server-based-on-openassistants",children:"Step 1: A simple FastAPI server based on OpenAssistants"}),"\n",(0,n.jsxs)(t.p,{children:["See ",(0,n.jsx)(t.a,{href:"https://github.com/definitive-io/openassistants/blob/main/examples/fast-api-server/fast_api_server/main.py",children:"code example"})]}),"\n",(0,n.jsx)(t.pre,{children:(0,n.jsx)(t.code,{className:"language-python",children:'from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom openassistants.core.assistant import Assistant\nfrom openassistants_fastapi.routes import RouteAssistants, create_router\n\napp = FastAPI()\n\nroute_assistants = RouteAssistants(\n    assistants={"hooli": Assistant(libraries=["piedpiper"])}\n)\n\n# <Some CORS stuff left out for simplicity, see full code example on GitHub>\n\napi_router = create_router(route_assistants)\n\napp.include_router(api_router)\n'})}),"\n",(0,n.jsxs)(t.p,{children:["Note, by convention, libraries can be placed in the working directory of the Python app in ",(0,n.jsx)(t.code,{children:"library/<name-of-library>"}),"."]}),"\n",(0,n.jsx)(t.p,{children:"A FastAPI server can define multiple assistants, which one is used can be specified by the client by calling the right REST route."}),"\n",(0,n.jsx)(t.h2,{id:"step-2-defining-the-library-and-assistant",children:"Step 2: Defining the library and Assistant"}),"\n",(0,n.jsx)(t.p,{children:'Functions are defined as YAML files in a folder (this is what we refer to as a "library" of functions). An assistant can consume multiple libraries to be able to use all functions defined across them.'}),"\n",(0,n.jsxs)(t.p,{children:["A single function inside ",(0,n.jsx)(t.code,{children:"library/piedpiper"}),":"]}),"\n",(0,n.jsx)(t.pre,{children:(0,n.jsx)(t.code,{className:"language-yaml",children:'name: send_purchase_inquiry_email\ndisplay_name: Send purchase inquiry email\ndescription: |\n  send an inquiry email about a recent purchase to an employee\nsample_questions:\n  - send purchase inquiry email\nparameters:\n  json_schema:\n    type: object\n    properties:\n      to:\n        type: string\n        format: email\n        description: email address to send to\n    required:\n      - to\ntype: PythonEvalFunction\npython_code: |\n  async def main(args: dict):\n    import asyncio\n    yield [{"type": "text", "text": "Sending email..."}]\n    await asyncio.sleep(2)\n    yield [{"type": "text", "text": f"Inquiry email about recent purchase sent to: {args.get(\'to\')}"}]\n'})}),"\n",(0,n.jsx)(t.h2,{id:"step-3-using-it-through-the-ui",children:"Step 3: Using it through the UI"}),"\n",(0,n.jsx)(t.p,{children:"Once the functions have been defined we can connect to the REST API using the default UI client."}),"\n",(0,n.jsxs)(t.p,{children:["First, navigate to ",(0,n.jsx)(t.code,{children:"examples/fast-api-server"})," to start the example backend:"]}),"\n",(0,n.jsx)(t.pre,{children:(0,n.jsx)(t.code,{className:"language-bash",children:"poetry install\npoetry shell\nexport OPENAI_API_KEY=sk-my-key\n./run/sh\n"})}),"\n",(0,n.jsx)(t.p,{children:"Then, simply start the Next.js app that points to the REST endpoint:"}),"\n",(0,n.jsx)(t.pre,{children:(0,n.jsx)(t.code,{className:"language-bash",children:"cd examples/next\nyarn run dev\n"})}),"\n",(0,n.jsx)(t.p,{children:(0,n.jsx)(t.img,{alt:"UI",src:s(1552).c+"",width:"841",height:"683"})})]})}function l(e={}){const{wrapper:t}={...(0,i.M)(),...e.components};return t?(0,n.jsx)(t,{...e,children:(0,n.jsx)(c,{...e})}):c(e)}},1552:(e,t,s)=>{s.d(t,{c:()=>n});const n=s.p+"assets/images/openassistants-16feeb0a171a4fa49bae23435f235089.png"},2172:(e,t,s)=>{s.d(t,{I:()=>o,M:()=>r});var n=s(1504);const i={},a=n.createContext(i);function r(e){const t=n.useContext(a);return n.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function o(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:r(e.components),n.createElement(a.Provider,{value:t},e.children)}}}]);