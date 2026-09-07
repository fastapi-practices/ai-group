insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values (2147098509659213900, 'ai-buddy-group.menu', 'AIBuddyGroupManage', '/plugins/ai-buddy/group', 9, 'material-symbols:group-outline', 1, '/plugins/ai-buddy-group/views/index', null, 1, 1, 1, '', null, (select id from sys_menu where name = 'PluginAIBuddy'), now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2147098509659213901, '新增分组', 'AddAIBuddyGroup', null, 0, null, 2, null, 'ai:group:add', 1, 0, 1, '', null, 2147098509659213900, now(), null),
(2147098509659213902, '修改分组', 'EditAIBuddyGroup', null, 0, null, 2, null, 'ai:group:edit', 1, 0, 1, '', null, 2147098509659213900, now(), null),
(2147098509659213903, '删除分组', 'DeleteAIBuddyGroup', null, 0, null, 2, null, 'ai:group:del', 1, 0, 1, '', null, 2147098509659213900, now(), null);
