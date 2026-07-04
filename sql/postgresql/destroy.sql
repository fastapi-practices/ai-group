delete from sys_menu
where name in (
    'AddAIGroup',
    'EditAIGroup',
    'DeleteAIGroup',
    'AIGroupManage'
);

drop table if exists ai_group_user;
drop table if exists ai_group_resource;
drop table if exists ai_group;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
