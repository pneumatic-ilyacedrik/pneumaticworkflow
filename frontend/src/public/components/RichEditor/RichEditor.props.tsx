import { ComponentProps, ReactNode } from 'react';
import { EditorProps } from 'draft-js';
import Editor from '@draft-js-plugins/editor';
import { TOutputChecklist } from '../../types/template';
import { TForegroundColor } from '../UI/Fields/common/types';

export enum EEditorKeyCommand {
  Enter = 'enter',
}
export interface IRichEditorState {
  isLoading: boolean;
  shouldSubmitAfterFileLoaded: boolean;
  editorState: EditorState;
  suggestions: TMentionData[];
  areSuggestionsOpened: boolean;
}

export type TMentionData = {
  id?: number;
  name: string;
  link?: string;
};

export interface IPositionSuggestionsParams {
  decoratorRect: { x: number; y: number } & DOMRect;
  popover: HTMLElement;
  props: {
    open: boolean;
    suggestions: TMentionData[];
  };
  // tslint:disable-next-line: no-any
  state: any;
}

export interface IRichEditorProps {
  isModal?: boolean;
  accountId: number;
  mentions: TMentionData[];
  placeholder: EditorProps['placeholder'];
  className?: string;
  defaultValue?: string;
  initialState?: EditorState;
  withMentions?: boolean;
  withToolbar?: boolean;
  withChecklists?: boolean;
  multiline?: boolean;
  children?: ReactNode;
  title?: string;
  decorators?: ComponentProps<typeof Editor>['decorators'];
  foregroundColor?: TForegroundColor;
  stripPastedFormatting?: boolean;
  submitIcon?: ReactNode;
  cancelIcon?: ReactNode;
  isInTaskDescriptionEditor?: boolean;
  handleChange(value: string): Promise<string>;
  handleChangeChecklists?(checklists: TOutputChecklist[]): void;
  onSubmit?(): void;
  onCancel?(): void;
}
