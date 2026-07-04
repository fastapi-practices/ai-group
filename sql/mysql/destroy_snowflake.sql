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
