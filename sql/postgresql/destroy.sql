delete from sys_menu
where name in (
    'AddAIBuddyGroup',
    'EditAIBuddyGroup',
    'DeleteAIBuddyGroup',
    'AIBuddyGroupManage'
);

drop table if exists ai_buddy_user;
drop table if exists ai_buddy_resource;
drop table if exists ai_buddy_group;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
