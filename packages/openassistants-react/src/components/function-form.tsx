import { AssistantMessage } from './chat-models';
import React from 'react';
import validator from '@rjsf/validator-ajv8';
import { FieldTemplateProps, WidgetProps } from '@rjsf/utils';
import Form from '@rjsf/core';
import { Button, IconCheck, Input, Label } from './ui';
import { Combobox } from './ui/combobox';
import { cn } from '../lib/utils';

interface FuncionFormProps extends React.ComponentProps<'div'> {
  message: AssistantMessage;
  onSubmit: (values: any) => void;
}

const InputWidget = function (props: WidgetProps) {
  return (
    <Input
      className={'py-2'}
      type="text"
      value={props.value || ''}
      required={props.required}
      autoFocus={props.autofocus || true}
      onChange={(event) => props.onChange(event.target.value)}
    />
  );
};

const SelectWidget = (props: WidgetProps) => {
  if (!props.options.enumOptions) {
    return (
      <Label className="px-8 text-destructive">
        Could not determine options
      </Label>
    );
  }
  return (
    <Combobox
      data={props.options.enumOptions}
      value={props.value}
      onSelect={(v) => {
        props.onChange(v);
      }}
    ></Combobox>
  );
};

export function FunctionForm({ message, onSubmit }: FuncionFormProps) {
  const [submitted, setSubmitted] = React.useState(false);
  const json_schema = message?.input_request?.json_schema;
  const uiSchema = {};
  // expand with more widgets
  const widgets = {
    TextWidget: InputWidget,
    EmailWidget: InputWidget,
    SelectWidget: SelectWidget,
  };

  const properCase = (str: string): string => {
    return str
      .replace(/\s+/g, ' ')
      .split('_')
      .map(
        (word) =>
          `${word.charAt(0).toUpperCase()}${word.slice(1).toLowerCase()}`
      )
      .join(' ');
  };

  const CustomFieldTemplate = (props: FieldTemplateProps) => {
    const {
      id,
      classNames,
      style,
      label,
      help,
      required,
      description,
      errors,
      children,
    } = props;
    return (
      <div className={classNames} style={style}>
        {id === 'root' ? (
          <p className="mb-2 font-semibold text-base text-primary">
            {properCase(label)}
          </p>
        ) : (
          <p className={cn('py-2 font-semibold text-sm')}>
            {properCase(label)}
            {required && '*'}
          </p>
        )}
        {children}
        <p className={cn('mt-1 text-sm text-muted-foreground opacity-80')}>
          {description}
        </p>
        <p className="text-destructive">{errors}</p>
        {help}
      </div>
    );
  };

  const SubmitButton = () => (
    <Button className="my-4" type="submit">
      Confirm
    </Button>
  );
  return (
    <div>
      {!submitted && (
        <Form
          schema={json_schema}
          widgets={widgets}
          uiSchema={uiSchema}
          templates={{
            FieldTemplate: CustomFieldTemplate,
            ButtonTemplates: { SubmitButton },
          }}
          formData={message.input_request?.arguments}
          validator={validator}
          onSubmit={(form) => {
            onSubmit(form.formData);
            setSubmitted(true);
          }}
          onError={() => console.log('errors')}
        />
      )}
      {submitted && (
        <div className="flex">
          <IconCheck></IconCheck>
          <Label className="px-2">Form Submitted</Label>
        </div>
      )}
    </div>
  );
}
