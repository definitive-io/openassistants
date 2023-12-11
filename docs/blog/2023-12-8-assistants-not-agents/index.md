---
slug: assistants-not-agents
title: Assistants not Agents
authors: [rick, dan]
tags: [facebook, hello, docusaurus]
---

In the fast-evolving world of AI systems, the distinction between building AI assistants and autonomous agents has become crucial. Recent insights from [Dharmesh Shah](https://agent.ai/p/why-most-agent-ais-dont-work-yet) highlight the inherent challenges with AI agents and why a more focused approach is preferable.

#### The Pitfall of Autonomous Agents

AI agents, like those in projects such as AutoGPT and BabyAGI, are designed to function autonomously, handling a series of tasks without human intervention. This sounds ideal, but there's a catch. These agents rely on imperfect Large Language Models (LLMs) like GPT to interpret goals and execute tasks. While LLMs are incredibly advanced, they're not infallible. They have an inherent error rate, which might seem negligible at a glance but can significantly impact an agent's performance.

For instance, if an LLM has a 95% success rate for each task, the cumulative success rate drops alarmingly with each additional task an agent undertakes. The mathematics behind this shows that even with a high individual task success rate, the overall reliability of an agent can diminish rapidly, reducing its effectiveness to a mere coin toss in complex scenarios. This is particularly problematic for general-purpose agents trying to cater to diverse functions.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">AI agents like that are also prone to all kinds of disastrous security holes that aren&#39;t nearly as harmful to copilots - I think that&#39;s a major reason we haven&#39;t seen a breakout application of that form of agent yet, whereas copilots are being used successfully on a daily basis</p>&mdash; Simon Willison (@simonw) <a href="https://twitter.com/simonw/status/1733916061928686040?ref_src=twsrc%5Etfw">December 10, 2023</a></blockquote>

#### The Advantage of AI Assistants

This is where AI assistants come into the limelight. Unlike their autonomous counterparts, AI assistants are designed to perform specific tasks, one at a time, with human interaction playing a central role. This approach has several advantages:

1. **Reduced Error Rate**: By focusing on specific tasks, AI assistants can minimize the cumulative error rate. A narrower scope means less room for errors to compound.

2. **Human Oversight**: AI assistants can work in tandem with humans, allowing for real-time feedback and corrections. This not only ensures more accurate outcomes but also helps in refining the AI's learning process.

3. **Specialized Functionality**: Tailoring an AI assistant to specific use-cases means it can be optimized for those tasks, resulting in a more efficient and effective performance.

4. **Flexibility and Control**: With AI assistants, users maintain control, dictating the pace and direction of the task. This leads to a more user-friendly experience, as the assistant can adapt to the user's needs and preferences.

#### Launching `OpenAssistants`

That's where `openassistants` comes in. We aim to make it easier to develop robust assistants that rely on function calling for performing actions and retrieving information into a conversational context. With a human in the loop these systems can be _useful_ and _reliable_. Our goal is to make the process of building robust assistants as easy as possible by putting as much boilerplate and common components into a set of extensible and composible libraries.

We're launching with three packages:

- `openassistants` the core library responsible for the main function calling / message generating runtime
- `openassistants-fastapi` a set of FastAPI routes used for interacting with the core runtime loop through a REST API
- `openassistants-ui` an example chat client that supports rich streaming outputs like tables, plots, form inputs and text.

The project is built on top of LangChain and we will soon support more sophisticated RAG features based on LlamaIndex. Our goal is to be the open alternative to the AssistantsAPI that can operate against any LLM: both Open Source LLMs like fine-tuned Llama's focused on function calling and proprietary models with e.g. native support for function calling.

![](https://github.com/definitive-io/openassistants/assets/1309307/3e7821f4-62d8-42c0-80c7-94be8b3f2e2c)

#### Conclusion

In conclusion, while the allure of fully autonomous AI agents is undeniable, the current state of technology suggests a more measured approach. Building AI assistants that excel in specific tasks and work in harmony with human users is not just practical but also more aligned with our current technological capabilities. This approach promises a more reliable AI experience that leads to experiences that we can actually deploy with confidence in production today.
