# 接口分析
1. /datafeed/patchnoteslist?language=schinese
  返回所有的版本信息
2. /datafeed/itemlist?language=schinese
  返回所有的物品信息
3. /datafeed/herolist?language=schinese
  返回所有的英雄信息
4. /datafeed/abilitylist?language=schinese
  返回所有的技能信息
5. /datafeed/patchnotes?version=7.23d&language=schinese
返回当前版本的公告信息
6. 图片
  https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/
  物品：items/ + name[5:] + '.png'
  英雄：hroes/ + name[14:] + '.png'
  技能：abilities/ + name + '.png'

# 数据库使用
    

拉取镜像：`docker pull postgres`

创建一个新的容器：`docker run -d --name dota2_db -p 5432:5432 -e POSTGRES_PASSWORD=123456 postgres`

进入容器：`docker exec -it dota2_db psql -U postgres`
```psql
    # 创建数据库
    create database dota2_db;

    # 退出
    \q
```

再次进入容器：`docker exec -it dota2_db psql -U postgres dota2_db`


```sql
-- 英雄表格
create table dota2_heroes(
    id int primary key not null,    -- id
    name varchar not null,         -- 名字
    name_loc varchar(200),         -- 中文名字
    name_english_loc varchar(200), -- 英文名字
    primary_attr int,               --
    complexity int
);

-- 物品能力表格
create table dota2_itemabilities(
    id int primary key not null,        -- id
    name varchar(200) not null,         -- 名字
    name_loc varchar(200) not null,     -- 中文名字
    name_english_loc varchar(200),      -- 英文名字
    is_item bool not null,              -- 是物品或技能
    neutral_item_tier int not null      -- 中立物品
);

-- 所有版本表格
create table dota2_patches(
    patch_name varchar(200) primary key not null, -- 版本名字
    patch_number varchar(200) not null,           -- 版本号
    patch_timestamp timestamp not null            -- 日期和时间
);

-- 当前版本信息表格
create type type1 as enum('generic', 'items', 'neutral_items', 'heroes', 'neutral_creeps'); -- 综合，物品，中立，英雄    
create type type2 as enum('hero_note', 'ability_note', 'talent_note'); -- 英雄、技能、天赋
create table dota2_curPatch(
    name_id varchar(200) primary key not null, -- patch_name_id + cur_type1 + 序号
    indent_level int not null,     -- 
    note text not null,            -- 公告
    info text,
    patch_name_id varchar(200) references dota2_patches(patch_name),      -- 版本名，外键
    cur_type1 type1 not null,      -- 改动类型
    cur_type2 type2,               -- 改动类型2
    ability_id int,           -- 物品或技能id
    hero_id int                    -- 英雄id
);
```