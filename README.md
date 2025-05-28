# Time_Sync

TimeSync 是一款智能群体时间协调系统，专为解决多人日程匹配痛点而设计。系统通过算法自动化+大模型辅助实现用户便捷上传非空闲时间和群体时间交集计算，可帮助活动组织者在指定日期范围内快速定位最优时间段，从而极大的提高组织管理的效率。

本系统采用前沿的智能算法和大语言模型技术，能够智能解析各类日程文本，自动提取时间信息，并通过高效的群体时间匹配算法，为组织者提供最优的时间安排建议。系统支持多种数据导入方式，提供直观的可视化界面，让时间协调变得简单高效。无论是学术会议、社团活动还是课程安排，TimeSync 都能帮助您轻松找到最适合的时间段，让组织管理工作事半功倍。

> 注：稳定版代码在main分支，其他分支为测试分支

## RayNovate团队成员

| 姓名   | 学号      | 专业             | 书院     |
| ------ | --------- | ---------------- | -------- |
| 王浩宸 | 241220128 | 计算机科学与技术 | 开甲书院 |
| 陈新   | 241502026 | 信息与计算科学   | 开甲书院 |
| 胡恩齐 | 241880252 | 技术科学试验班   | 健雄书院 |
| 罗伟亮 | 241880396 | 技术科学试验班   | 健雄书院 |

> 按学号顺序排序

## 后端使用方法

> 见[backend](https://github.com/SweetGargamel/time_sync_frontend)

1. 克隆仓库到本地

2. 运行一下代码安装依赖（建议先新建一个虚拟环境）

   ```bash
   pip install -r requirements.txt
   ```

3. 在`/time_sync`目录下新增一个配置文件`config.py`，内容见下方的文件内容（在线仓库我们没有上传 ）。

4. 安装PostgreSQL数据库，并创建一个数据库`time_sync`。你也可以用其他数据库如MySQL。（目前我们的配置是直接连接到我们服务器上的数据库，如果您不想本地配置数据库的话可以直接套用我们的Config文件连接在线数据库）

### 后端的项目结构

```plaintext
后端 (timesync_backend/):
├── config.py                   # 配置文件,包含数据库配置和API密钥等
├── run.py                     # 应用程序入口文件
├── upload/                    # 文件上传目录
└── utils/                     # 工具函数目录
    ├── ai_chat.py            # AI对话相关功能
    ├── course_converter.py   # 课程数据转换器
    ├── Crawler.py            # 教务网爬虫
    ├── models.py             # 数据库模型定义
    ├── Prompt.py            # AI提示词模板
    ├── routes.py            # 路由处理函数
    │
    ├── add_person/          # 人员管理模块
    │   ├── add_person_main.py         # 人员添加主要逻辑
    │   ├── Identify_columns.py        # 表格列识别
    │   └── Identify_nonrepeat_group.py # 去重组识别
    │
    ├── llm_change_events/   # 日程修改模块
    │   └── llm_change_events_main.py  # 日程修改主要逻辑
    │
    ├── llm_file_events/     # 文件处理模块
    │   ├── AddFile.py              # 添加文件
    │   ├── ApplyFileUploadLease.py # 文件上传租约
    │   ├── Describefile.py         # 文件描述
    │   ├── llm_file_events_main.py # 文件事件主逻辑
    │   └── UploadTempFile.py       # 临时文件上传
    │
    ├── llm_operate_groups/  # 组操作模块
    │   └── llm_operate_groups.py   # 组操作主要逻辑
    │
    └── src/                 # 基础功能模块
        ├── getcourse.py     # 获取课程信息
        └── login.py         # 登录相关功能
```

## 前端使用方法

> 见[frontend](https://github.com/SweetGargamel/time_sync_frontend)

1. 在本地安装node.js环境

2. `npm install`安装所有依赖

3. `npm run dev`启动本地服务器

4. 启动后端服务器

5. 最后打开 http://localhost:5173/ 即可本地查看页面

### 前端的项目结构

```plaintext
前端 (time_sync/):
├── index.html              # 入口HTML文件
├── package.json           # 项目依赖配置
├── vite.config.js        # Vite构建工具配置
│
└── src/
    ├── App.vue           # 根组件
    ├── main.js           # 应用入口文件
    │
    ├── hooks/            # 自定义钩子函数
    │   ├── AI_Insert_Person.js  # AI辅助添加人员
    │   ├── file_uploader.js     # 文件上传处理
    │   ├── LLM_form_group.js    # AI智能分组
    │   └── nju_crawler.js       # 南大教务网爬虫
    │
    ├── stores/           # 状态管理
    │   ├── change_event.js    # 日程修改状态
    │   ├── events.js          # 日程管理状态
    │   ├── persongroup.js     # 人员和组管理状态
    │   ├── query.js           # 查询相关状态
    │   └── url.js             # API接口URL配置
    │
    └── views/            # 页面组件
        ├── ChangeEvents.vue    # 日程修改页面
        ├── HomeView.vue        # 首页
        ├── QueryView.vue       # 查询页面
        ├── UpdatePersonView.vue # 人员管理页面
        └── UpLoadEventsView.vue # 日程上传页面
```

## 网站部署

您可以访问 http://47.122.85.137 来查看我们的已经部署好的网站。由于我们暂时只是测试阶段，允许所有人有修改人员和组信息，您可以做少量的删改的测试，但是请您不要把所有的人员信息都删除。

由于阿里云的限制，我们的服务器暂时不允许绑定域名。同时我们购买的阿里云配置有限，可能会出现大量访问时出现卡顿的情况。

由于我们的所有AI功能全部是依赖大模型实现的，可能会存在反应时间长的问题，请您耐心等待。

## 时光织梦：代码里的温度韵脚

_算法是理性的诗行，而温度是它的韵脚：_

_当系统为熬夜科研的同学避开早八，那是代码在说"你值得休息"；_

_当界面为忙碌的教师自动推荐最佳时段，那是程序在道"你的时间很珍贵"；_

_当学长学姐的经验分享突破时间壁垒，是它在说 "传承的火花不应熄灭"；_

_当志愿服务的温暖如期抵达，是它在道 "善意值得最顺畅的旅程"；_

_当学术灵感在预定的时空畅快碰撞，是它在轻吟 "智慧的交响需要精准的节拍"；_

_当日历上亮起代表共识的绿色区块，那是技术在轻语"看，我们找到了相聚的答案"。_
<br />

_从教室到实验室，从行政楼到社团活动室，我们愿做无声的守护者——_

_不让任何一个人的声音因时间而沉默，_

_不让任何一次协作因繁琐而降温。_

_我们让错过的遗憾化作重逢的惊喜，_

_将零散的日程编织成紧密的联结。_
<br />

_最好的技术，_

_从来不是冰冷的01二进制，_

_而是能读懂你匆忙脚步下的期待，_

_能守护你珍贵时光里的每一度温暖。_

> ——By RayNovate Team
