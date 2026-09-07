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
