import { commonRequest } from './commonRequest';
import { getBrowserConfigEnv } from '../utils/getConfig';
import { IKickoff, ITemplateTask } from '../types/template';

export type TGetTemplateFieldsResponse = {
  tasks: Pick<ITemplateTask, 'id' | 'fields' | 'name' | 'apiName'>[];
  kickoff: Pick<IKickoff, 'fields'>;
};

export function getTemplateFields(id: string) {
  const {
    api: { urls },
  } = getBrowserConfigEnv();

  const url = urls.templateFields.replace(':id', String(id));

  return commonRequest<TGetTemplateFieldsResponse>(url);
}
