delete from sys_menu
where name in (
    'AddAIBuddyGroup',
    'EditAIBuddyGroup',
    'DeleteAIBuddyGroup',
    'AIBuddyGroupManage'
);

drop table if exists ai_buddy_group_user;
drop table if exists ai_buddy_group_resource;
drop table if exists ai_buddy_group;
