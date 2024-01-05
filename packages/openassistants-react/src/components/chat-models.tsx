import { z } from 'zod';

const BaseMessageZod = z.object({
  role: z.union([
    z.literal('user'),
    z.literal('assistant'),
    z.literal('function'),
  ]),
});

const FunctionCallArgumentZod = z.object({
  name: z.string(),
  arguments: z.record(z.any()),
});

const InputRequestArgumentZod = FunctionCallArgumentZod.extend({
  json_schema: z.any(), // this is a json schema. Will be compile to a zod object at runtime
});

const UserMessageZod = BaseMessageZod.extend({
  role: z.literal('user'),
  content: z.union([
    z.string(),
    z.array(z.object({}).passthrough()),
  ]).optional(),
  input_response: FunctionCallArgumentZod.optional(),
});

const AssistantMessageZod = BaseMessageZod.extend({
  role: z.literal('assistant'),
  content: z.string().optional(),
  input_request: InputRequestArgumentZod.optional(),
  function_call: FunctionCallArgumentZod.optional(),
  stage: z.union([z.literal('confirmed'), z.literal('unconfirmed')]).optional(),
});

const DataframeZod = z.object({
  rows: z.array(z.array(z.string())),
  cols: z.array(z.string()),
});
const ExamplePromptZod = z.object({
  title: z.string(),
  prompt: z.string(),
});

const FunctionMessageZod = BaseMessageZod.extend({
  role: z.literal('function'),
  stage: z.union([z.literal('confirmed'), z.literal('unconfirmed')]),
  outputs: z.array(
    z.union([
      z.object({
        type: z.literal('dataframe'),
        dataframe: DataframeZod,
        title: z.string().optional(),
      }),
      z.object({ type: z.literal('visualization'), visualization: z.any() }),
      z.object({ type: z.literal('text'), text: z.string() }),
      z.object({
        type: z.literal('follow_ups'),
        follow_ups: z.array(ExamplePromptZod),
      }),
    ])
  ),
});

const MessageZod = z.union([
  UserMessageZod,
  AssistantMessageZod,
  FunctionMessageZod,
]);

export type BaseMessage = z.infer<typeof BaseMessageZod>;
export type UserMessage = z.infer<typeof UserMessageZod>;
export type AssistantMessage = z.infer<typeof AssistantMessageZod>;
export type FunctionMessage = z.infer<typeof FunctionMessageZod>;
export type Message = z.infer<typeof MessageZod>;
export type FunctionCallArgument = z.infer<typeof FunctionCallArgumentZod>;
export type InputRequestArgument = z.infer<typeof InputRequestArgumentZod>;
export type Dataframe = z.infer<typeof DataframeZod>;

export interface ExamplePrompt {
  title: string;
  prompt: string;
}
