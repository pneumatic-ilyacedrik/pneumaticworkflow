import pytest
from django.contrib.auth import get_user_model

from pneumatic_backend.processes.tests.fixtures import (
    create_test_user,
    create_test_template,
    create_test_workflow,
    create_test_account,
)
from pneumatic_backend.processes.enums import (
    FieldType,
)
from pneumatic_backend.processes.models import (
    FieldTemplate,
    TaskField,
    FieldTemplateSelection,
    FieldSelection,
    FileAttachment,
)
from pneumatic_backend.processes.api_v2.services.task.selection import (
    SelectionService
)
from pneumatic_backend.processes.api_v2.services import (
    WorkflowEventService
)
from pneumatic_backend.processes.api_v2.services.task.field import (
    TaskFieldService
)
from pneumatic_backend.processes.api_v2.services.task.exceptions import (
    TaskFieldException
)
from pneumatic_backend.processes.messages import workflow as messages


UserModel = get_user_model()
pytestmark = pytest.mark.django_db


def test_create_instance__task_field__ok(mocker):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    field_template = FieldTemplate.objects.create(
        type=FieldType.FILE,
        name='Some file',
        description='Some description',
        api_name='some-api-name',
        order=11,
        task=template.tasks.get(number=1),
        template=template,
        is_required=True,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    value = 'https://john.cena/john.cena'
    markdown_value = '[john.cena](https://john.cena/john.cena)'
    get_valid_value_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._get_valid_value',
        return_value=(value, markdown_value)
    )
    clear_value = 'https://clear-john.cena/john.cena'
    clear_markdown_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'MarkdownService.clear',
        return_value=clear_value
    )
    raw_value = ['555']
    service = TaskFieldService(
        user=user
    )

    # act
    service._create_instance(
        instance_template=field_template,
        value=raw_value,
        task_id=task.id,
        workflow_id=workflow.id,
    )

    # assert
    get_valid_value_mock.assert_called_once_with(
        raw_value=raw_value,
        selections=None
    )
    clear_markdown_mock.assert_called_once_with(value)
    task_field = service.instance
    assert task_field.kickoff is None
    assert task_field.task == task
    assert task_field.type == field_template.type
    assert task_field.is_required == field_template.is_required
    assert task_field.name == field_template.name
    assert task_field.description == field_template.description
    assert task_field.api_name == field_template.api_name
    assert task_field.order == field_template.order
    assert task_field.value == value
    assert task_field.markdown_value == markdown_value
    assert task_field.clear_value == clear_value
    assert task_field.user_id is None


def test_create_instance__kickoff_field__ok(mocker):

    # arrange
    user = create_test_user()
    template = create_test_template(user, tasks_count=1)
    field_template = FieldTemplate.objects.create(
        type=FieldType.TEXT,
        name='Some text',
        kickoff=template.kickoff_instance,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    value = 'https://john.cena/john.cena'
    markdown_value = '[john.cena](https://john.cena/john.cena)'
    get_valid_value_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._get_valid_value',
        return_value=(value, markdown_value)
    )
    clear_value = 'https://clear-john.cena/john.cena'
    clear_markdown_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'MarkdownService.clear',
        return_value=clear_value
    )
    raw_value = ['555']
    service = TaskFieldService(
        user=user
    )

    # act
    service._create_instance(
        instance_template=field_template,
        value=raw_value,
        kickoff_id=workflow.kickoff_instance.id,
        workflow_id=workflow.id,
    )

    # assert
    get_valid_value_mock.assert_called_once_with(
        raw_value=raw_value,
        selections=None
    )
    clear_markdown_mock.assert_called_once_with(value)
    task_field = service.instance
    assert task_field.task is None
    assert task_field.kickoff_id == workflow.kickoff_instance.id
    assert task_field.user_id is None


def test_create_instance__type_user__ok(mocker):

    # arrange
    user = create_test_user()
    template = create_test_template(user, tasks_count=1)
    field_template = FieldTemplate.objects.create(
        type=FieldType.USER,
        name='Some user',
        task=template.tasks.get(number=1),
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    value = 'https://john.cena/john.cena'
    markdown_value = '[john.cena](https://john.cena/john.cena)'
    get_valid_value_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._get_valid_value',
        return_value=(value, markdown_value)
    )
    clear_value = 'https://clear-john.cena/john.cena'
    clear_markdown_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'MarkdownService.clear',
        return_value=clear_value
    )
    raw_value = '555'
    service = TaskFieldService(
        user=user
    )

    # act
    service._create_instance(
        instance_template=field_template,
        value=raw_value,
        task_id=task.id,
        workflow_id=workflow.id,
    )

    # assert
    get_valid_value_mock.assert_called_once_with(
        raw_value=raw_value,
        selections=None
    )
    clear_markdown_mock.assert_called_once_with(value)
    task_field = service.instance
    assert task_field.user_id == 555


def test_create_instance__skip_value__ok(mocker):

    # arrange
    user = create_test_user()
    template = create_test_template(user, tasks_count=1)
    field_template = FieldTemplate.objects.create(
        type=FieldType.USER,
        name='Some user',
        kickoff=template.kickoff_instance,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    value = 'https://john.cena/john.cena'
    markdown_value = '[john.cena](https://john.cena/john.cena)'
    get_valid_value_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._get_valid_value',
        return_value=(value, markdown_value)
    )
    clear_value = 'https://clear-john.cena/john.cena'
    clear_markdown_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'MarkdownService.clear',
        return_value=clear_value
    )
    service = TaskFieldService(
        user=user
    )

    # act
    service._create_instance(
        instance_template=field_template,
        task_id=task.id,
        workflow_id=workflow.id,
        skip_value=True
    )

    # assert
    get_valid_value_mock.assert_not_called()
    clear_markdown_mock.assert_not_called()
    task_field = service.instance
    assert task_field.value == ''
    assert task_field.clear_value is None
    assert task_field.markdown_value is None
    assert task_field.user_id is None


@pytest.mark.parametrize('field_type', FieldType.TYPES_WITH_SELECTION)
def test_create_selections_with_value__radio_dropdown__not_value__ok(
    field_type,
    mocker
):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=field_type,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=field_type,
        workflow=workflow
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    create_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.create'
    )

    # act
    service._create_selections_with_value(
        raw_value=None,
        instance_template=field_template
    )

    # assert
    create_selection_mock.assert_called_once_with(
        instance_template=selection_template,
        field_id=task_field.id,
        is_selected=False
    )


def test_create_selections_with_value__checkbox__not_value__ok(
    mocker
):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.CHECKBOX,
        workflow=workflow
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    create_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.create'
    )

    # act
    service._create_selections_with_value(
        raw_value=None,
        instance_template=field_template
    )

    # assert
    create_selection_mock.assert_called_once_with(
        instance_template=selection_template,
        field_id=task_field.id,
        is_selected=False
    )


def test_create_selections_with_value__checkbox_id__ok(
    mocker
):
    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    create_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.create'
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.CHECKBOX,
        workflow=workflow
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = [str(selection_template_1.id)]

    # act
    service._create_selections_with_value(
        raw_value=raw_value,
        instance_template=field_template
    )

    # assert
    create_selection_mock.call_count = 2
    create_selection_mock.assert_has_calls([
        mocker.call(
            instance_template=selection_template_1,
            field_id=task_field.id,
            is_selected=True
        ),
        mocker.call(
            instance_template=selection_template_2,
            field_id=task_field.id,
            is_selected=False
        )
    ])


def test_create_selections_with_value__checkbox_api_name__ok(
    mocker
):

    # arrange
    create_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.create'
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.CHECKBOX,
        workflow=workflow
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = [selection_template_1.api_name]

    # act
    service._create_selections_with_value(
        raw_value=raw_value,
        instance_template=field_template
    )

    # assert
    create_selection_mock.call_count = 2
    create_selection_mock.assert_has_calls([
        mocker.call(
            instance_template=selection_template_1,
            field_id=task_field.id,
            is_selected=True
        ),
        mocker.call(
            instance_template=selection_template_2,
            field_id=task_field.id,
            is_selected=False
        )
    ])


@pytest.mark.parametrize('field_type', FieldType.TYPES_WITH_SELECTION)
def test_create_selections_with_value__radio_dropdown_id__ok(
    field_type,
    mocker
):
    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    create_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.create'
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=field_type,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=field_type,
        workflow=workflow
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = str(selection_template_1.id)

    # act
    service._create_selections_with_value(
        raw_value=raw_value,
        instance_template=field_template
    )

    # assert
    create_selection_mock.call_count = 2
    create_selection_mock.assert_has_calls([
        mocker.call(
            instance_template=selection_template_1,
            field_id=task_field.id,
            is_selected=True
        ),
        mocker.call(
            instance_template=selection_template_2,
            field_id=task_field.id,
            is_selected=False
        )
    ])


@pytest.mark.parametrize('field_type', FieldType.TYPES_WITH_SELECTION)
def test_create_selections_with_value__radio_dropdown_api_name__ok(
    field_type,
    mocker
):

    # arrange
    create_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.create'
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=field_type,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=field_type,
        workflow=workflow
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = selection_template_1.api_name

    # act
    service._create_selections_with_value(
        raw_value=raw_value,
        instance_template=field_template
    )

    # assert
    create_selection_mock.call_count = 2
    create_selection_mock.assert_has_calls([
        mocker.call(
            instance_template=selection_template_1,
            field_id=task_field.id,
            is_selected=True
        ),
        mocker.call(
            instance_template=selection_template_2,
            field_id=task_field.id,
            is_selected=False
        )
    ])


def test_link_new_attachments__not_attached__ok():

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user, tasks_count=1)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.FILE,
        workflow=workflow
    )
    attachment = FileAttachment.objects.create(
        name='john.cena',
        url='https://john.cena/john.cena',
        size=1488,
        account_id=user.account_id
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )

    # act
    service._link_new_attachments(
        attachments_ids=[attachment.id]
    )

    # assert
    attachment.refresh_from_db()
    assert attachment.output_id == task_field.id
    assert attachment.workflow_id == workflow.id


def test_link_new_attachments__update_attached__ok():

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user, tasks_count=1)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.FILE,
        workflow=workflow
    )
    attachment = FileAttachment.objects.create(
        output_id=task_field.id,
        name='john.cena',
        url='https://john.cena/john.cena',
        size=1488,
        account_id=user.account_id,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )

    # act
    service._link_new_attachments(
        attachments_ids=[attachment.id]
    )

    # assert
    attachment.refresh_from_db()
    assert attachment.output_id == task_field.id
    assert attachment.workflow_id == workflow.id


def test_link_new_attachments__event_attachment__not_link():

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user, tasks_count=1)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.FILE,
        workflow=workflow
    )
    attachment = FileAttachment.objects.create(
        name='john.cena',
        url='https://john.cena/john.cena',
        size=1488,
        account_id=user.account_id,
    )

    event = WorkflowEventService.comment_created_event(
        user=user,
        attachments=[attachment.id],
        workflow=workflow,
        text=None,
        after_create_actions=False
    )
    attachment.event = event
    attachment.save()

    service = TaskFieldService(
        instance=task_field,
        user=user
    )

    # act
    service._link_new_attachments(
        attachments_ids=[attachment.id]
    )

    # assert
    attachment.refresh_from_db()
    assert attachment.output_id is None
    assert attachment.workflow_id is None


def test_link_new_attachments__another_account_attachment__not_update():

    # arrange
    another_account = create_test_account()
    user = create_test_user()
    workflow = create_test_workflow(user=user, tasks_count=1)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.FILE,
        workflow=workflow
    )
    attachment = FileAttachment.objects.create(
        name='john.cena',
        url='https://john.cena/john.cena',
        size=1488,
        account_id=another_account.id,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )

    # act
    service._link_new_attachments(
        attachments_ids=[attachment.id]
    )

    # assert
    attachment.refresh_from_db()
    assert attachment.output_id is None
    assert attachment.workflow_id is None


def test_link_new_attachments__not_value__not_attached():

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user, tasks_count=1)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.FILE,
        workflow=workflow
    )
    attachment = FileAttachment.objects.create(
        name='john.cena',
        url='https://john.cena/john.cena',
        size=1488,
        account_id=user.account_id
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )

    # act
    service._link_new_attachments(
        attachments_ids=[]
    )

    # assert
    attachment.refresh_from_db()
    assert attachment.output_id is None
    assert attachment.workflow_id is None


@pytest.mark.parametrize('field_type', FieldType.TYPES_WITH_SELECTION)
def test_update_selections__radio_dropdown__not_value__ok(
    field_type,
    mocker
):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=field_type,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=field_type,
        workflow=workflow
    )
    selection = FieldSelection.objects.create(
        field=task_field,
        value=selection_template.value,
        api_name=selection_template.api_name,
        is_selected=False,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    update_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.partial_update'
    )
    selection_service_init_mock = mocker.patch.object(
        SelectionService,
        attribute='__init__',
        return_value=None
    )

    # act
    service._update_selections(raw_value=None)

    # assert
    selection_service_init_mock.assert_called_once_with(
        instance=selection,
        user=user
    )
    update_selection_mock.assert_called_once_with(
        is_selected=False,
        force_save=True
    )


def test_update_selections__checkbox__not_value__ok(
    mocker
):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.CHECKBOX,
        workflow=workflow
    )
    selection = FieldSelection.objects.create(
        field=task_field,
        value=selection_template.value,
        api_name=selection_template.api_name,
        is_selected=False,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    update_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.partial_update'
    )
    selection_service_init_mock = mocker.patch.object(
        SelectionService,
        attribute='__init__',
        return_value=None
    )

    # act
    service._update_selections(raw_value=None)

    # assert
    selection_service_init_mock.assert_called_once_with(
        instance=selection,
        user=user
    )
    update_selection_mock.assert_called_once_with(
        is_selected=False,
        force_save=True
    )


def test_update_selections__checkbox_id__ok(
    mocker
):
    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    update_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.partial_update'
    )
    selection_service_init_mock = mocker.patch.object(
        SelectionService,
        attribute='__init__',
        return_value=None
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.CHECKBOX,
        workflow=workflow
    )
    selection_1 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_1.value,
        api_name=selection_template_1.api_name,
        is_selected=True,
    )
    selection_2 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_2.value,
        api_name=selection_template_2.api_name,
        is_selected=True,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = [str(selection_1.id)]

    # act
    service._update_selections(raw_value=raw_value)

    # assert
    selection_service_init_mock.call_count = 2
    selection_service_init_mock.assert_has_calls([
        mocker.call(instance=selection_1, user=user),
        mocker.call(instance=selection_2, user=user),
    ])
    update_selection_mock.call_count = 2
    update_selection_mock.assert_has_calls([
        mocker.call(
            is_selected=True,
            force_save=True
        ),
        mocker.call(
            is_selected=False,
            force_save=True
        )
    ])


def test_update_selections__checkbox_api_name__ok(
    mocker
):

    # arrange
    update_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.partial_update'
    )
    selection_service_init_mock = mocker.patch.object(
        SelectionService,
        attribute='__init__',
        return_value=None
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.CHECKBOX,
        workflow=workflow
    )
    selection_1 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_1.value,
        api_name=selection_template_1.api_name,
        is_selected=True,
    )
    selection_2 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_2.value,
        api_name=selection_template_2.api_name,
        is_selected=True,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = [selection_1.api_name]

    # act
    service._update_selections(raw_value=raw_value)

    # assert
    selection_service_init_mock.call_count = 2
    selection_service_init_mock.assert_has_calls([
        mocker.call(instance=selection_1, user=user),
        mocker.call(instance=selection_2, user=user),
    ])
    update_selection_mock.call_count = 2
    update_selection_mock.assert_has_calls([
        mocker.call(
            is_selected=True,
            force_save=True
        ),
        mocker.call(
            is_selected=False,
            force_save=True
        )
    ])


@pytest.mark.parametrize('field_type', FieldType.TYPES_WITH_SELECTION)
def test_update_selections__radio_dropdown_id__ok(
    field_type,
    mocker
):
    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    update_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.partial_update'
    )
    selection_service_init_mock = mocker.patch.object(
        SelectionService,
        attribute='__init__',
        return_value=None
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=field_type,
        name='field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=field_type,
        workflow=workflow
    )
    selection_1 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_1.value,
        api_name=selection_template_1.api_name,
        is_selected=False,
    )
    selection_2 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_2.value,
        api_name=selection_template_2.api_name,
        is_selected=True,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = str(selection_1.id)

    # act
    service._update_selections(raw_value=raw_value)

    # assert
    selection_service_init_mock.call_count = 2
    selection_service_init_mock.assert_has_calls([
        mocker.call(instance=selection_1, user=user),
        mocker.call(instance=selection_2, user=user),
    ])
    update_selection_mock.call_count = 2
    update_selection_mock.assert_has_calls([
        mocker.call(
            is_selected=True,
            force_save=True
        ),
        mocker.call(
            is_selected=False,
            force_save=True
        )
    ])


@pytest.mark.parametrize('field_type', FieldType.TYPES_WITH_SELECTION)
def test_update_selections__radio_dropdown_api_name__ok(
    field_type,
    mocker
):

    # arrange
    update_selection_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field'
        '.SelectionService.partial_update'
    )
    selection_service_init_mock = mocker.patch.object(
        SelectionService,
        attribute='__init__',
        return_value=None
    )
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=field_type,
        name='field',
        template=template,
        api_name='api-name-1',
    )
    selection_template_1 = FieldTemplateSelection.objects.create(
        value='first',
        field_template=field_template,
        template=template,
    )
    selection_template_2 = FieldTemplateSelection.objects.create(
        value='second',
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=field_type,
        workflow=workflow
    )
    selection_1 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_1.value,
        api_name=selection_template_1.api_name,
        is_selected=False,
    )
    selection_2 = FieldSelection.objects.create(
        field=task_field,
        value=selection_template_2.value,
        api_name=selection_template_2.api_name,
        is_selected=True,
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = selection_1.api_name

    # act
    service._update_selections(raw_value=raw_value)

    # assert
    selection_service_init_mock.call_count = 2
    selection_service_init_mock.assert_has_calls([
        mocker.call(instance=selection_1, user=user),
        mocker.call(instance=selection_2, user=user),
    ])
    update_selection_mock.call_count = 2
    update_selection_mock.assert_has_calls([
        mocker.call(
            is_selected=True,
            force_save=True
        ),
        mocker.call(
            is_selected=False,
            force_save=True
        )
    ])


def test_partial_update__type_file__ok(mocker):

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.FILE,
        workflow=workflow
    )
    deleted_attachment = FileAttachment.objects.create(
        name='test',
        url='https://test.test',
        size=1488,
        account_id=user.account_id,
        output=task_field
    )
    value = 'https://john.cena/john.cena'
    markdown_value = '[john.cena](https://john.cena/john.cena)'
    attachment = FileAttachment.objects.create(
        name='john.cena',
        url=value,
        size=1488,
        account_id=user.account_id,
        output=task_field
    )
    get_valid_value_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._get_valid_value',
        return_value=(value, markdown_value)
    )
    clear_value = 'https://clear-john.cena/john.cena'
    clear_markdown_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'MarkdownService.clear',
        return_value=clear_value
    )
    link_new_attachments_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._link_new_attachments'
    )
    update_selections_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._update_selections'
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = [str(attachment.id)]

    # act
    service.partial_update(value=raw_value)

    # assert
    get_valid_value_mock.assert_called_once_with(
        raw_value=raw_value,
        selections=None
    )
    clear_markdown_mock.assert_called_once_with(value)
    assert not FileAttachment.objects.filter(id=deleted_attachment.id).exists()
    link_new_attachments_mock.assert_called_once_with(raw_value)
    update_selections_mock.assert_not_called()
    task_field.refresh_from_db()
    assert task_field.value == value
    assert task_field.markdown_value == markdown_value
    assert task_field.clear_value == clear_value
    assert task_field.user_id is None


def test_partial_update__type_file_null_value__ok(mocker):

    # arrange
    value = ''
    markdown_value = ''
    user = create_test_user()
    workflow = create_test_workflow(user=user)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        is_required=True,
        type=FieldType.FILE,
        workflow=workflow
    )
    deleted_attachment = FileAttachment.objects.create(
        name='test',
        url='https://test.test',
        size=1488,
        account_id=user.account_id,
        output=task_field
    )
    service = TaskFieldService(
        instance=task_field,
        user=user
    )
    raw_value = None

    get_valid_value_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._get_valid_value',
        return_value=(value, value)
    )
    clear_value = ''
    clear_markdown_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'MarkdownService.clear',
        return_value=clear_value
    )
    link_new_attachments_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._link_new_attachments'
    )
    update_selections_mock = mocker.patch(
        'pneumatic_backend.processes.api_v2.services.task.field.'
        'TaskFieldService._update_selections'
    )

    # act
    service.partial_update(value=raw_value)

    # assert
    get_valid_value_mock.assert_called_once_with(
        raw_value=raw_value,
        selections=None
    )
    clear_markdown_mock.assert_called_once_with(value)
    assert not FileAttachment.objects.filter(id=deleted_attachment.id).exists()
    link_new_attachments_mock.assert_called_once_with(raw_value)
    update_selections_mock.assert_not_called()
    task_field.refresh_from_db()
    assert task_field.value == value
    assert task_field.markdown_value == markdown_value
    assert task_field.clear_value == clear_value
    assert task_field.user_id is None


def test_get_valid_radio_value__id__ok():

    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.RADIO,
        name='Radio field',
        template=template,
        api_name='api-name-1',
    )
    value = 'first option'
    FieldTemplateSelection.objects.create(
        value='Another value',
        field_template=field_template,
        template=template,
    )
    selection_template = FieldTemplateSelection.objects.create(
        value=value,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    selection = FieldSelection.objects.create(
        field=task_field,
        value=selection_template.value,
        api_name=selection_template.api_name,
        is_selected=True,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = str(selection_template.id)

    # act
    result = service._get_valid_radio_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (selection.value, selection.value)


def test_get_valid_radio_value__api_name__ok():

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.RADIO,
        name='Radio field',
        template=template,
        api_name='api-name-1',
    )
    value = 'first option'
    selection_template = FieldTemplateSelection.objects.create(
        value=value,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    selection = FieldSelection.objects.create(
        field=task_field,
        value=selection_template.value,
        api_name=selection_template.api_name,
        is_selected=True,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = selection.api_name

    # act
    result = service._get_valid_radio_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (selection.value, selection.value)


def test_get_valid_radio_value__first_create_selection__ok():

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.RADIO,
        name='Radio field',
        template=template,
        api_name='api-name-1',
    )
    value = 'first option'
    selection_template = FieldTemplateSelection.objects.create(
        value=value,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = selection_template.api_name

    # act
    result = service._get_valid_radio_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (selection_template.value, selection_template.value)


@pytest.mark.parametrize('raw_value', ('abc', None))
def test_get_valid_radio_value__not_string__raise_exception(raw_value):

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.RADIO,
        workflow=workflow,
    )
    service = TaskFieldService(instance=task_field)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_radio_value(
            raw_value=raw_value,
            selections=task_field.selections.all()
        )

    # assert
    assert ex.value.message == messages.MSG_PW_0028
    assert ex.value.api_name == task_field.api_name


def test_get_valid_radio_value__not_exists_selection__raise_exception():

    # arrange
    user = create_test_user()
    workflow = create_test_workflow(user=user)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name='api-name-1',
        type=FieldType.RADIO,
        workflow=workflow,
    )
    service = TaskFieldService(instance=task_field)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_radio_value(
            raw_value='12352',
            selections=task_field.selections.all()
        )
    # assert
    assert ex.value.message == messages.MSG_PW_0028
    assert ex.value.api_name == task_field.api_name


def test_get_valid_checkbox_value__one_id__ok():

    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    value = 'first option'
    FieldTemplateSelection.objects.create(
        value='Another value',
        field_template=field_template,
        template=template,
    )
    selection_template = FieldTemplateSelection.objects.create(
        value=value,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    selection = FieldSelection.objects.create(
        field=task_field,
        value=selection_template.value,
        api_name=selection_template.api_name,
        is_selected=True,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = [str(selection_template.id)]

    # act
    result = service._get_valid_checkbox_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (selection.value, selection.value)


def test_get_valid_checkbox_value__many_ids__ok():

    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    value_1 = 'first option'
    selection_template_1 = FieldTemplateSelection.objects.create(
        value=value_1,
        field_template=field_template,
        template=template,
    )
    value_2 = 'second option'
    selection_template_2 = FieldTemplateSelection.objects.create(
        value=value_2,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    FieldSelection.objects.create(
        field=task_field,
        value=selection_template_1.value,
        api_name=selection_template_1.api_name,
    )
    FieldSelection.objects.create(
        field=task_field,
        value=selection_template_2.value,
        api_name=selection_template_2.api_name,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = [str(selection_template_1.id), str(selection_template_2.id)]

    # act
    result = service._get_valid_checkbox_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (
        f'{value_1}, {value_2}',
        f'{value_1}, {value_2}'
    )


def test_get_valid_checkbox_value__one_api_name__ok():

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    value = 'first option'
    FieldTemplateSelection.objects.create(
        value='Another value',
        field_template=field_template,
        template=template,
    )
    selection_template = FieldTemplateSelection.objects.create(
        value=value,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    selection = FieldSelection.objects.create(
        field=task_field,
        value=selection_template.value,
        api_name=selection_template.api_name,
        is_selected=True,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = [selection_template.api_name]

    # act
    result = service._get_valid_checkbox_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (selection.value, selection.value)


def test_get_valid_checkbox_value__many_api_names__ok():

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    value_1 = 'first option'
    selection_template_1 = FieldTemplateSelection.objects.create(
        value=value_1,
        field_template=field_template,
        template=template,
    )
    value_2 = 'second option'
    selection_template_2 = FieldTemplateSelection.objects.create(
        value=value_2,
        field_template=field_template,
        template=template,
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    FieldSelection.objects.create(
        field=task_field,
        value=selection_template_1.value,
        api_name=selection_template_1.api_name,
    )
    FieldSelection.objects.create(
        field=task_field,
        value=selection_template_2.value,
        api_name=selection_template_2.api_name,
    )
    service = TaskFieldService(instance=task_field)
    raw_value = [selection_template_1.api_name, selection_template_2.api_name]

    # act
    result = service._get_valid_checkbox_value(
        raw_value=raw_value,
        selections=field_template.selections.all()
    )

    # assert
    assert result == (
        f'{value_1}, {value_2}',
        f'{value_1}, {value_2}'
    )


@pytest.mark.parametrize('raw_value', ('abc', None))
def test_get_valid_checkbox_value__not_list__raise_exception(raw_value):

    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    service = TaskFieldService(instance=task_field)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_checkbox_value(
            raw_value=raw_value,
            selections=field_template.selections.all()
        )

    # assert
    assert ex.value.message == messages.MSG_PW_0029
    assert ex.value.api_name == task_field.api_name


@pytest.mark.parametrize('raw_value', ('abc', None, 8942))
def test_get_valid_checkbox_value__wrong_api_name_type__raise_exception(
    raw_value
):

    # TODO Remove in https://my.pneumatic.app/workflows/34311/

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.CHECKBOX,
        name='Checkbox field',
        template=template,
        api_name='api-name-1',
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    service = TaskFieldService(instance=task_field)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_checkbox_value(
            raw_value=[raw_value],
            selections=field_template.selections.all()
        )

    # assert
    assert ex.value.message == messages.MSG_PW_0030
    assert ex.value.api_name == task_field.api_name


# def test_get_valid_checkbox_value__not_found_api_name__raise_exception():
#
#     # TODO Uncomment in https://my.pneumatic.app/workflows/34311/
#
#     # arrange
#     user = create_test_user()
#     template = create_test_template(user=user, tasks_count=1)
#     template_task = template.tasks.first()
#     field_template = FieldTemplate.objects.create(
#         task=template_task,
#         type=FieldType.CHECKBOX,
#         name='Checkbox field',
#         template=template,
#         api_name='api-name-1',
#     )
#     value = 'first option'
#     FieldTemplateSelection.objects.create(
#         value='Another value',
#         field_template=field_template,
#         template=template,
#     )
#     selection_template = FieldTemplateSelection.objects.create(
#         value=value,
#         field_template=field_template,
#         template=template,
#     )
#     workflow = create_test_workflow(user=user, template=template)
#     task = workflow.current_task_instance
#     task_field = TaskField.objects.create(
#         task=task,
#         api_name=field_template.api_name,
#         is_required=field_template.is_required,
#         type=field_template.type,
#         workflow=workflow,
#     )
#     selection = FieldSelection.objects.create(
#         field=task_field,
#         value=selection_template.value,
#         template_id=selection_template.id,
#         api_name=selection_template.api_name,
#         is_selected=True,
#     )
#     service = TaskFieldService(instance=task_field)
#
#     # act
#     with pytest.raises(TaskFieldException) as ex:
#         service._get_valid_checkbox_value(
#             raw_value=[selection.api_name, 'bad-api-name'],
#             selections=field_template.selections.all()
#         )
#
#     # assert
#     assert ex.value.message == messages.MSG_PW_0031
#     assert ex.value.api_name == task_field.api_name


@pytest.mark.parametrize('raw_value', (176516132, 176516132.00))
def test_get_valid_date_value__valid_value__ok(raw_value):

    # arrange
    user = create_test_user()
    service = TaskFieldService(user=user)

    # act
    result = service._get_valid_date_value(raw_value=raw_value)

    # assert
    assert result == (
        str(raw_value),
        'Aug 06, 1975, 12:15AM'
    )


@pytest.mark.parametrize('raw_value', ('176516132', '176516132.00', ' '))
def test_get_valid_date_value__invalid_value__ok(raw_value):
    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.DATE,
        name='Date field',
        template=template,
        api_name='api-name-1',
    )
    workflow = create_test_workflow(user=user, template=template)
    task = workflow.current_task_instance
    task_field = TaskField.objects.create(
        task=task,
        api_name=field_template.api_name,
        is_required=field_template.is_required,
        type=field_template.type,
        workflow=workflow,
    )
    service = TaskFieldService(instance=task_field)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_date_value(raw_value=raw_value)

    # assert
    assert ex.value.api_name == task_field.api_name
    assert ex.value.message == messages.MSG_PW_0032


@pytest.mark.parametrize('raw_value', (5165, True))
def test_get_valid_url_value__not_string__raise_exception(raw_value):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.URL,
        name='URL field',
        template=template,
        api_name='api-name-1',
    )
    service = TaskFieldService(user=user, instance=field_template)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_url_value(raw_value=raw_value)

    # assert
    assert ex.value.message == messages.MSG_PW_0034
    assert ex.value.api_name == field_template.api_name


@pytest.mark.parametrize(
    'raw_value',
    ('ssh://my.pneumatic.app', 'relative/path')
)
def test_get_valid_url_value__invalid_url__raise_exception(raw_value):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.URL,
        name='URL field',
        template=template,
        api_name='api-name-1',
    )
    service = TaskFieldService(user=user, instance=field_template)

    # act
    with pytest.raises(TaskFieldException) as ex:
        service._get_valid_url_value(raw_value=raw_value)

    # assert
    assert ex.value.message == messages.MSG_PW_0035
    assert ex.value.api_name == field_template.api_name


@pytest.mark.parametrize(
    'raw_value',
    ('https://my.pneumatic.app', 'https://192.168.0.1')
)
def test_get_valid_url_value__valid_value__ok(raw_value):

    # arrange
    user = create_test_user()
    template = create_test_template(user=user, tasks_count=1)
    template_task = template.tasks.first()
    field_template = FieldTemplate.objects.create(
        task=template_task,
        type=FieldType.URL,
        name='URL field',
        template=template,
        api_name='api-name-1',
    )
    service = TaskFieldService(user=user, instance=field_template)

    # act
    raw_value_result, markdown_value_result = (
        service._get_valid_url_value(raw_value=raw_value)
    )

    # assert
    assert raw_value_result == raw_value
    assert markdown_value_result == f'[URL field]({raw_value})'
