insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values (2147098509659213900, '分组管理', 'AIGroupManage', '/plugins/ai/group', 7, 'material-symbols:group-outline', 1, '/plugins/ai-group/views/index', null, 1, 1, 1, '', null, (select id from sys_menu where name = 'PluginAI'), now(), null);

insert into sys_menu (id, title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
(2147098509659213901, '新增分组', 'AddAIGroup', null, 0, null, 2, null, 'ai:group:add', 1, 0, 1, '', null, 2147098509659213900, now(), null),
(2147098509659213902, '修改分组', 'EditAIGroup', null, 0, null, 2, null, 'ai:group:edit', 1, 0, 1, '', null, 2147098509659213900, now(), null),
(2147098509659213903, '删除分组', 'DeleteAIGroup', null, 0, null, 2, null, 'ai:group:del', 1, 0, 1, '', null, 2147098509659213900, now(), null);
