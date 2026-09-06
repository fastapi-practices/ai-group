do $$
declare
    ai_group_menu_id bigint;
begin
    insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
    values ('ai-buddy-group.menu', 'AIGroupManage', '/plugins/ai-buddy/group', 7, 'material-symbols:group-outline', 1, '/plugins/ai-buddy-group/views/index', null, 1, 1, 1, '', null, (select id from sys_menu where name = 'PluginAIBuddy'), now(), null)
    returning id into ai_group_menu_id;

    insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
    values
    ('新增分组', 'AddAIGroup', null, 0, null, 2, null, 'ai:group:add', 1, 0, 1, '', null, ai_group_menu_id, now(), null),
    ('修改分组', 'EditAIGroup', null, 0, null, 2, null, 'ai:group:edit', 1, 0, 1, '', null, ai_group_menu_id, now(), null),
    ('删除分组', 'DeleteAIGroup', null, 0, null, 2, null, 'ai:group:del', 1, 0, 1, '', null, ai_group_menu_id, now(), null);
end $$;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
