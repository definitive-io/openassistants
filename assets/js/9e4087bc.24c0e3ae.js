"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[28],{6140:(e,s,r)=>{r.r(s),r.d(s,{default:()=>o});r(1504);var t=r(6016),a=r(4357),i=r(5756),c=r(9012),n=r(6448),l=r(7624);function d(e){let{year:s,posts:r}=e;return(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(n.c,{as:"h3",id:s,children:s}),(0,l.jsx)("ul",{children:r.map((e=>(0,l.jsx)("li",{children:(0,l.jsxs)(t.c,{to:e.metadata.permalink,children:[e.metadata.formattedDate," - ",e.metadata.title]})},e.metadata.date)))})]})}function h(e){let{years:s}=e;return(0,l.jsx)("section",{className:"margin-vert--lg",children:(0,l.jsx)("div",{className:"container",children:(0,l.jsx)("div",{className:"row",children:s.map(((e,s)=>(0,l.jsx)("div",{className:"col col--4 margin-vert--lg",children:(0,l.jsx)(d,{...e})},s)))})})})}function o(e){let{archive:s}=e;const r=(0,a.G)({id:"theme.blog.archive.title",message:"Archive",description:"The page & hero title of the blog archive page"}),t=(0,a.G)({id:"theme.blog.archive.description",message:"Archive",description:"The page & hero description of the blog archive page"}),d=function(e){const s=e.reduce(((e,s)=>{const r=s.metadata.date.split("-")[0],t=e.get(r)??[];return e.set(r,[s,...t])}),new Map);return Array.from(s,(e=>{let[s,r]=e;return{year:s,posts:r}}))}(s.blogPosts);return(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(i.U7,{title:r,description:t}),(0,l.jsxs)(c.c,{children:[(0,l.jsx)("header",{className:"hero hero--primary",children:(0,l.jsxs)("div",{className:"container",children:[(0,l.jsx)(n.c,{as:"h1",className:"hero__title",children:r}),(0,l.jsx)("p",{className:"hero__subtitle",children:t})]})}),(0,l.jsx)("main",{children:d.length>0&&(0,l.jsx)(h,{years:d})})]})]})}}}]);