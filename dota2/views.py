from django.urls import reverse
from django.shortcuts import render, redirect
from django.db import connections


def index(request):
    new_url = reverse('dota2:patch') + '?patch_name=latest_version'
    return redirect(new_url)


def patch(request):
    patch_name = request.GET.get('patch_name')
    conn = connections['default']
    cursor = conn.cursor()
    result = {}

    # 获取所有版本信息
    patch_names = []
    sql = 'select patch_name from dota2_patches'
    cursor.execute(sql)
    required_records = cursor.fetchall()
    for row in reversed(required_records):
        if patch_name == 'latest_version':
            patch_name = row[0]
        patch_names.append({
            'patch_name': row[0],
        })
    result['patch_names'] = patch_names

    # 提取版本基础信息
    sql = 'select * from dota2_patches where patch_name = %s'
    cursor.execute(sql, [patch_name])
    required_records = cursor.fetchall()
    for row in required_records:
        result['patch_name'] = row[0]
        result['patch_number'] = row[1]
        result['patch_timestamp'] = int(row[2].strftime("%Y%m%d%H"))

    # 提取综合改动
    generic = []
    sql = 'select indent_level, note, info from dota2_curpatch where patch_name_id = %s and cur_type1 = %s'
    cursor.execute(sql, [patch_name, 'generic'])
    required_records = cursor.fetchall()
    for row in required_records:
        row_dic = {
            'indent_level': row[0],
            'note': row[1]
        }
        if row[2] is not None:
            row_dic['info'] = row[2]
        generic.append(row_dic)
    result['generic'] = generic

    # 提取物品改动
    items = []
    sql = 'select ability_id from dota2_curpatch where patch_name_id = %s and cur_type1 = %s group by ability_id'
    cursor.execute(sql, [patch_name, 'items'])
    required_records = cursor.fetchall()
    sql = 'select indent_level, note from dota2_curpatch where patch_name_id = %s and ability_id = %s'
    for row in required_records:
        item_dic = {}
        cursor.execute('select name_loc, name from dota2_itemabilities where id = %s', [row[0]])
        r = cursor.fetchone()
        item_dic['name_loc'] = r[0]
        item_dic['url'] = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/' + r[1][5:] + '.png'
        # print(item_dic['url'])
        notes = []
        cursor.execute(sql, [patch_name, row[0]])
        required_records_notes = cursor.fetchall()
        for row_notes in required_records_notes:
            notes.append({
                'indent_level': row_notes[0],
                'note': row_notes[1]
            })
        item_dic['notes'] = notes
        items.append(item_dic)
    result['items'] = items

    # 提取中立物品
    neutral_items = []
    sql = 'select ability_id from dota2_curpatch where patch_name_id = %s and cur_type1 = %s group by ability_id'
    cursor.execute(sql, [patch_name, 'neutral_items'])
    required_records = cursor.fetchall()
    sql = 'select indent_level, note from dota2_curpatch where patch_name_id = %s and ability_id = %s'
    for row in required_records:
        neutral_items_dic = {}
        cursor.execute('select name_loc, name from dota2_itemabilities where id = %s', [row[0]])
        r = cursor.fetchone()
        neutral_items_dic['name_loc'] = r[0]
        neutral_items_dic['url'] = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/items/' + r[1][5:] + '.png'
        cursor.execute(sql, [patch_name, row[0]])
        required_records_notes = cursor.fetchall()
        notes = []
        for row_notes in required_records_notes:
            notes.append({
                'indent_level': row_notes[0],
                'note': row_notes[1],
            })
        neutral_items_dic['notes'] = notes
        neutral_items.append(neutral_items_dic)
    result['neutral_items'] = neutral_items

    # 获取英雄改动
    heroes = []
    sql = 'select hero_id from dota2_curpatch where patch_name_id = %s and cur_type1 = %s group by hero_id'
    cursor.execute(sql, [patch_name, 'heroes'])
    required_records = cursor.fetchall()
    sql = 'select indent_level, note from dota2_curpatch where patch_name_id = %s and hero_id = %s and cur_type2 = %s'
    for row in required_records:
        hero_dic = {}
        cursor.execute('select name_loc, name from dota2_heroes where id = %s', [row[0]])
        r = cursor.fetchone()
        hero_dic['name_loc'] = r[0]
        hero_dic['url'] = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/' + r[1][14:] + ".png"
        # print(hero_dic['url'])
        cursor.execute(sql, [patch_name, row[0], 'hero_note'])
        required_records_hero_note = cursor.fetchall()
        hero_notes = []
        for row_hero_note in required_records_hero_note:
            hero_notes.append({
                'indent_level': row_hero_note[0],
                'note': row_hero_note[1],
            })
        hero_dic['hero_notes'] = hero_notes
        cursor.execute(sql, [patch_name, row[0], 'talent_note'])
        required_records_talent_note = cursor.fetchall()
        talent_notes = []
        for row_talent_note in required_records_talent_note:
            talent_notes.append({
                'indent_level': row_talent_note[0],
                'note': row_talent_note[1],
            })
        hero_dic['talent_notes'] = talent_notes
        abilities = []
        cursor.execute('select ability_id from dota2_curpatch where patch_name_id = %s and hero_id = %s and cur_type2 '
                       '= %s group by ability_id', [patch_name, row[0], 'ability_note'])
        required_records_ability = cursor.fetchall()
        for row_ability in required_records_ability:
            hero_ability_dic = {}
            cursor.execute('select name_loc, name from dota2_itemabilities where id = %s', [row_ability[0]])
            r = cursor.fetchone()
            hero_ability_dic['name_loc'] = r[0]
            hero_ability_dic['url'] = 'https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/abilities/' + r[1] + '.png'
            cursor.execute('select indent_level, note from dota2_curpatch where patch_name_id = %s and hero_id = %s '
                           'and ability_id = %s', [patch_name, row[0], row_ability[0]])
            required_records_ability_notes = cursor.fetchall()
            ability_notes = []
            for row_ability_note in required_records_ability_notes:
                ability_notes.append({
                    'indent_level': row_ability_note[0],
                    'note': row_ability_note[1],
                })
            hero_ability_dic['ability_notes'] = ability_notes
            abilities.append(hero_ability_dic)
        hero_dic['abilities'] = abilities
        heroes.append(hero_dic)
    result['heroes'] = heroes

    # print(result['generic'])
    # data = json.dumps(result, ensure_ascii=False)
    return render(request, 'dota2/patch.html', result)
