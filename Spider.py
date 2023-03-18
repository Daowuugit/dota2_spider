# -- coding: utf-8 --

from fake_useragent import UserAgent
from datetime import datetime
import time
import requests
import json
import psycopg2
import random


class DotaSpider(object):
    # 初始化
    def __init__(self):
        self.url = 'https://www.dota2.com'
        self.conn = psycopg2.connect(database="dota2_db", user='postgres', password="123456", host='127.0.0.1', port='5432')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    # 获取英雄信息
    def get_herolist(self):
        url = self.url + '/datafeed/herolist'
        headers = {'User-Agent': UserAgent().firefox}
        params = {'language': 'schinese'}
        response = requests.get(url, headers=headers, params=params)
        html = json.loads(response.text)
        for dic in html['result']['data']['heroes']:
            id = dic['id']
            name = dic['name']
            name_loc = dic['name_loc']
            name_english_loc = dic['name_english_loc']
            primary_attr = dic['primary_attr']
            complexity = dic['complexity']
            sql = "insert into dota2_heroes (id, name, name_loc, name_english_loc, primary_attr, complexity) " \
                  "values (%s, %s, %s, %s, %s, %s)" \
                  "on conflict(id)" \
                  "do update set (name, name_loc, name_english_loc, primary_attr, complexity) = (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql, [id, name, name_loc, name_english_loc, primary_attr, complexity,
                                          name, name_loc, name_english_loc, primary_attr, complexity])

    # 获取物品信息
    def get_itemlist(self):
        url = self.url + '/datafeed/itemlist'
        headers = {'User-Agent': UserAgent().firefox}
        params = {'language': 'schinese'}
        response = requests.get(url, headers=headers, params=params)
        html = json.loads(response.text)
        for dic in html['result']['data']['itemabilities']:
            id = dic['id']
            name = dic['name']
            name_loc = dic['name_loc']
            name_english_loc = dic['name_english_loc']
            is_item = True
            neutral_item_tier = dic['neutral_item_tier']
            sql ="insert into dota2_itemabilities (id, name, name_loc, name_english_loc, is_item, neutral_item_tier) " \
                 "values (%s, %s, %s, %s, %s, %s)" \
                 "on conflict(id)" \
                 "do update set (name, name_loc, name_english_loc, is_item, neutral_item_tier) = (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql, [id, name, name_loc, name_english_loc, is_item, neutral_item_tier,
                                          name, name_loc, name_english_loc, is_item, neutral_item_tier])

    def get_ability(self):
        url = self.url + '/datafeed/abilitylist'
        headers = {'User-Agent': UserAgent().firefox}
        params = {'language': 'schinese'}
        response = requests.get(url, headers=headers, params=params)
        html = json.loads(response.text)
        for dic in html['result']['data']['itemabilities']:
            id = dic['id']
            name = dic['name']
            name_loc = dic['name_loc']
            name_english_loc = dic['name_english_loc']
            is_item = False
            neutral_item_tier = dic['neutral_item_tier']
            sql = "insert into dota2_itemabilities (id, name, name_loc, name_english_loc, is_item, neutral_item_tier) "\
                  "values (%s, %s, %s, %s, %s, %s)" \
                  "on conflict(id)" \
                  "do update set (name, name_loc, name_english_loc, is_item, neutral_item_tier) = (%s, %s, %s, %s, %s)"
            self.cursor.execute(sql, [id, name, name_loc, name_english_loc, is_item, neutral_item_tier,
                                          name, name_loc, name_english_loc, is_item, neutral_item_tier])

    #  获取所有版本信息
    def get_patches(self):
        url = self.url + '/datafeed/patchnoteslist'
        headers = {'User-Agent': UserAgent().firefox}
        params = {'language': 'schinese'}
        response = requests.get(url, headers=headers, params=params)
        html = json.loads(response.text)
        for dic in html['patches']:
            patch_name = dic['patch_name']
            patch_number = dic['patch_number']
            patch_timestamp = datetime.fromtimestamp(dic['patch_timestamp'])
            sql = "insert into dota2_patches (patch_name, patch_number, patch_timestamp) " \
                  "values (%s, %s, %s) " \
                  "on conflict(patch_name) " \
                  "do update set (patch_number, patch_timestamp) = (%s, %s)"
            self.cursor.execute(sql, [patch_name, patch_number, patch_timestamp,
                                                  patch_number, patch_timestamp])
            self.get_note(patch_name)

    # 获取指定版本信息
    def get_note(self, patch_name_id):
        url = self.url + '/datafeed/patchnotes'
        headers = {'User-Agent': UserAgent().firefox}
        params = {'language': 'schinese', 'version': patch_name_id}
        response = requests.get(url, headers=headers, params=params)
        html = json.loads(response.text)

        if 'generic' in html.keys():
            cur_type1 = 'generic'
            generic_note_count = 0  # 记录当前模块公告条数
            for dic in html['generic']:
                generic_note_count += 1
                indent_level = dic['indent_level']
                note = dic['note']
                name_id = patch_name_id + cur_type1 + str(generic_note_count)
                if 'info' in dic.keys():
                    info = dic['info']
                    sql = 'insert into dota2_curPatch(name_id, indent_level, note, info, patch_name_id, cur_type1) ' \
                          'values(%s, %s, %s, %s, %s, %s)' \
                          'on conflict(name_id)' \
                          'do update set(indent_level, note, info, patch_name_id, cur_type1) = (%s, %s, %s, %s, %s)'
                    self.cursor.execute(sql, [name_id, indent_level, note, info, patch_name_id, cur_type1,
                                                       indent_level, note, info, patch_name_id, cur_type1])
                else:
                    sql = 'insert into dota2_curPatch(name_id, indent_level, note, patch_name_id, cur_type1) ' \
                          'values(%s, %s, %s, %s, %s)' \
                          'on conflict(name_id)' \
                          'do update set(indent_level, note, patch_name_id, cur_type1) = (%s, %s, %s, %s)'
                    self.cursor.execute(sql, [name_id, indent_level, note, patch_name_id, cur_type1,
                                                       indent_level, note, patch_name_id, cur_type1])

        if 'items' in html.keys():
            cur_type1 = 'items'
            item_note_count = 0
            for dic in html['items']:
                ability_id = dic['ability_id']
                for djc in dic['ability_notes']:
                    item_note_count += 1
                    name_id = patch_name_id + cur_type1 + str(item_note_count)
                    indent_level = djc['indent_level']
                    note = djc['note']
                    sql = 'insert into dota2_curPatch(name_id, indent_level, note, patch_name_id, cur_type1, ability_id)' \
                          ' values(%s, %s, %s, %s, %s, %s)' \
                          'on conflict(name_id)' \
                          'do update set(indent_level, note, patch_name_id, cur_type1, ability_id) = (%s, %s, %s, %s, %s)'
                    self.cursor.execute(sql, [name_id, indent_level, note, patch_name_id, cur_type1, ability_id,
                                                       indent_level, note, patch_name_id, cur_type1, ability_id])

        if 'neutral_items' in html.keys():
            cur_type1 = 'neutral_items'
            neutral_items_count = 0
            for dic in html['neutral_items']:
                ability_id = dic['ability_id']
                for djc in dic['ability_notes']:
                    indent_level = djc['indent_level']
                    note = djc['note']
                    neutral_items_count += 1
                    name_id = patch_name_id + cur_type1 + str(neutral_items_count)
                    sql = 'insert into dota2_curPatch (name_id, indent_level, note, patch_name_id, cur_type1, ability_id) ' \
                          'values(%s, %s, %s, %s, %s, %s)' \
                          'on conflict (name_id)' \
                          'do update set(indent_level, note, patch_name_id, cur_type1, ability_id) = (%s, %s, %s, %s, %s)'
                    self.cursor.execute(sql, [name_id, indent_level, note, patch_name_id, cur_type1, ability_id,
                                              indent_level, note, patch_name_id, cur_type1, ability_id])

        if 'heroes' in html.keys():
            cur_type1 = 'heroes'
            heroes_count = 0
            for dic in html['heroes']:
                hero_id = dic['hero_id']
                if 'hero_notes' in dic.keys():
                    cur_type2 = 'hero_note'
                    for djc in dic['hero_notes']:
                        indent_level = djc['indent_level']
                        note = djc['note']
                        heroes_count += 1
                        name_id = patch_name_id + cur_type1 + str(heroes_count)
                        sql = 'insert into dota2_curPatch(name_id, indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id) ' \
                              'values(%s, %s, %s, %s, %s, %s, %s)' \
                              'on conflict (name_id)' \
                              'do update set (indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id) = (%s, %s, %s, %s, %s, %s)'
                        self.cursor.execute(sql, [name_id, indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id,
                                                  indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id])

                if 'talent_notes' in dic.keys():
                    cur_type2 = 'talent_note'
                    for djc in dic['talent_notes']:
                        indent_level = djc['indent_level']
                        note = djc['note']
                        heroes_count += 1
                        name_id = patch_name_id + cur_type1 + str(heroes_count)
                        sql = 'insert into dota2_curPatch(name_id, indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id) ' \
                              'values(%s, %s, %s, %s, %s, %s, %s)' \
                              'on conflict (name_id)' \
                              'do update set (indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id) = (%s, %s, %s, %s, %s, %s)'
                        self.cursor.execute(sql, [name_id, indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id,
                                                           indent_level, note, patch_name_id, cur_type1, cur_type2, hero_id])

                if 'abilities' in dic.keys():
                    cur_type2 = 'ability_note'
                    for djc in dic['abilities']:
                        ability_id = djc['ability_id']
                        for dkc in djc['ability_notes']:
                            indent_level = dkc['indent_level']
                            note = dkc['note']
                            heroes_count += 1
                            name_id = patch_name_id + cur_type1 + str(heroes_count)
                            sql = 'insert into dota2_curPatch(name_id, indent_level, note, patch_name_id, cur_type1, cur_type2, ability_id, hero_id) ' \
                                  'values(%s, %s, %s, %s, %s, %s, %s, %s)' \
                                  'on conflict (name_id)' \
                                  'do update set (indent_level, note, patch_name_id, cur_type1, cur_type2, ability_id, hero_id) = (%s, %s, %s, %s, %s, %s, %s)'
                            self.cursor.execute(sql, [name_id, indent_level, note, patch_name_id, cur_type1, cur_type2, ability_id, hero_id,
                                                      indent_level, note, patch_name_id, cur_type1, cur_type2, ability_id, hero_id])

    # 开始运行
    def run(self):
        self.get_herolist()
        self.get_itemlist()
        self.get_ability()
        self.get_patches()


if __name__ == '__main__':
    start = time.time()
    spider = DotaSpider()
    spider.run()
    end = time.time()
    print('执行时间：%.2f' % (end - start))
