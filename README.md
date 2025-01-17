## 它可以做什么

此脚本可通过 danbooru API 获取图片列表并以多线程的方式批量下载图片、动图和视频，可选择根据`页面ID`/`图片ID`区间下载两种下载模式，脚本预设了 danbooru/gelbooru/yande.re/konachan/rule34/sankakucomplex 等常见的基于 danbooru 和 gelbooru 程序搭建的图库的网站爬虫模板，另支持自定义设置`下载模板`、`搜索/排除标签`、`线程数`、`自定义保存路径`、`http代理`、`下载查重`、`校验文件完整性`、`保存元数据`等强大功能。

---

## 使用方法

### 运行方式

使用**shell**运行，仅测试了在`Windows 11 + PowerShell + Python 3.9.1 64-bit`环境下可以正常运行。

### 运行参数

|     长参数名     | 短参数名 | 类型 |         默认         |                                                                                      描述                                                                                       |
| :--------------: | :------: | :--: | :------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|       mode       |    m     | 必选 |          无          | 指定运行模式，取值范围：`["id", "page", "file", "copyright"]`，`id`：通过 ID 下载 / `page`：通过页码下载 / `file`：使用`json`格式的配置文件运行，同时需要指定`file-config-path` |
|     template     |    t     | 可选 |    (str)"yandere"    |                                                                                    运行模板                                                                                     |
|      start       |    s     | 可选 |        (int)1        |                                                                                     起始 ID                                                                                     |
|       end        |    e     | 可选 |        (int)1        |                                                                结束 ID，`-1` 表示下载到最新一张图/下载到最后一页                                                                |
|       tags       |    t     | 可选 |       (str)""        |                                                         搜索(`tagname`)/排除(`-tagname`)指定 tags，使用`+`连接多个 tag                                                          |
|       path       |    p     | 可选 |     (str)"./img"     |                                                                                  文件保存路径                                                                                   |
|      proxy       |    P     | 可选 |       (str)""        |                                                              http 代理地址，格式：`http://[用户名:密码@]IP[:端口]`                                                              |
|      thread      |    T     | 可选 |        (int)5        |                                                            线程数，建议设置为 `5` 或更低，过高可能造成 HTTP429 错误                                                             |
| file-config-path |   _无_   | 可选 | (str)"./config.json" |                                                                    配置文件路径，只在运行模式为`file`时生效                                                                     |
|    retry-max     |   _无_   | 可选 |        (int)5        |                                                                 最大网络请求重试次数，`-1`表示重试直到下载成功                                                                  |
|    log-level     |   _无_   | 可选 |     (str)"Info"      |                                   更改日志记录等级，取值范围：`["Debug", "Info", "Warn", "Error", "None"]`，日志等级依次升高，信息量依次减少                                    |
|  deduplication   |   _无_   | 可选 |    (str)"strict"     |                                   去重模式，取值范围：`strict`：严格模式，通过 ID+MD5 验证 / `sloppy`：宽松模式，通过 ID 验证 / `none`：不验证                                   |
|     chksums      |   _无_   | 可选 |    (boolean)True     |                                                                     下载后进行文件完整性校验（标志性参数）                                                                      |
|  with-metadata   |   _无_   | 可选 |    (boolean)False    |                                                                       保存每个图片的元数据（标志性参数）                                                                        |
|   make-config    |   _无_   | 可选 |    (boolean)False    |                                               生成一个空白的配置文件，此时`file-config-path`将视为配置文件生成路径（标志性参数）                                                |
|   no-print-log   |   _无_   | 可选 |    (boolean)False    |                                                                      不打印日志到标准输出流（标志性参数）                                                                       |

### 运行示例

#### `id`模式

**danbooru 的 post id 会递增：post id 越大，图片上传时间越晚，最新图片的 post id 永远大于其他 post id。**

##### 示例一

```shell
python3 main.py -m id -s 301 -e 301
```

含义：根据`图片ID`下载，从`301`下载到`301`（仅下载 ID 为`301`的图片）。

##### 示例二

```shell
python3 main.py -m id -s 123456 -e 654321
```

含义：根据`图片ID`下载，从`123456`下载到`654321`（下载 ID 在`[123456,654321]`区间中的图片，实际下载时会倒序下载，即从 654321 开始下载）。

##### 示例三

```shell
python3 main.py -m id -s 123456 -e -1
```

含义：根据`图片ID`下载，从`123456`下载到`最新一张图`（下载 ID 大于等于`123456`的图片，实际下载时会倒序下载，即从最新一张图开始下载）。

##### 示例四

```shell
python3 main.py -m id -s 1 -e -1
```

含义：根据`图片ID`下载，从`1`下载到`最新一张图`（下载 ID 大于等于`1`的图片，即`全部下载`，实际下载时会倒序下载，即从最新一张图开始下载）。

#### `page`模式

**danbooru 的 page id 会动态更新：page id 越大，图片上传时间越早，最新图片所在的 page id 永远为 1。**

##### 示例五

```shell
python3 main.py -m page -s 301 -e 301
```

含义：根据`页面ID`下载，从`301`下载到`301`（仅下载第`301`页的图片）。

##### 示例六

```shell
python3 main.py -m page -s 123 -e 456
```

含义：根据`页面ID`下载，从`123`下载到`456`（下载所在位置在`[123,456]`区间页中的图片）。

##### 示例七

```shell
python3 main.py -m page -s 123 -e -1
```

含义：根据`页面ID`下载，从`123`下载到`最后一页`（下载所在位置大于等于第`123`页中的图片）。

##### 示例八

```shell
python3 main.py -m page -s 1 -e -1
```

含义：根据`页面ID`下载，从`1`下载到`最后一页`（下载所在位置大于等于第`1`页的图片，即`全部下载`）。

#### `file`模式

**配置文件的`键`（`key`）均需使用`长命令`，且`-`应被替换为`_`。当指定为`file`模式时，配置文件的优先级最高。当配置文件内未提供参数的值或值为空字符串时，使用命令行传入的参数的值，如果命令行仍未指定，使用默认值。**

##### 示例九

```shell
python3 main.py -m file "--file-config-path" "./config.json"
```

与此同时，`./config.json`的内容：

```text
{
	"args": {
		"mode": "page",
		"template": "yandere",
		"start": 1,
		"end": 5,
		"tags": "angel+-tagme+tail+-ass",
		"path": "./downloader",
		"proxy": "http://username:password@127.0.0.1:8080",
		"thread": 5,
		"file_config_path": "",
		"retry_max": "20",
		"log_level": "Info",
		"deduplication": "strict",
		"chksums": true,
		"with_metadata": false,
		"make_config": false,
		"no_print_log": false
	}
}
```

含义：以配置文件中的配置运行。

配置文件含义：根据`页面ID`下载，使用`yandere`模板，下载所在位置大于等于第`1`页且小于等于第`5`页的图片，只获取标签中包含`["angel", "tail"]`且不包含`["tagme", "ass"]`的图片，下载到当前目录下名为`downloader`的目录（如不存在则自动创建），使用 HTTP 代理：`http://username:password@127.0.0.1:8080`，`5`线程下载，超时重试`20`次，日志级别`Info`，严格去重，下载后校验文件完整性，不包含元数据，输出日志到屏幕。

##### 示例十

```shell
python3 main.py -m file "--file-config-path" "./config.json" -p "./yande" -e 100
```

与此同时，`./config.json`的内容：

```text
{
	"args": {
		"mode": "page",
		"start": 1,
		"end": 5,
		"tags": "angel+-tagme+tail+-ass",
		"thread": 5,
		"proxy": "http://username:password@127.0.0.1:8080"
	}
}
```

含义：以配置文件中的配置运行，下载到到当前目录下名为`yande`的目录（如不存在则自动创建），**但指定的`结束ID`将不会生效**。

配置文件含义：根据`页面ID`下载，下载所在位置大于等于第`1`页且小于等于第`5`页的图片，只获取标签中包含`["angel", "tail"]`且不包含`["tagme", "ass"]`的图片，`5`线程下载，使用 HTTP 代理：`http://username:password@127.0.0.1:8080`，其余未设置的均为默认值。

### 模板参数

```text
{
	"mode": {
		"page": {
			"api": "",
			"header": {},
			"method": "",
			"data": "",
			"download": {
				"metadata": "",
				"filename": "",
				"metadata_filename": "",
				"header": {}
			}
		},
		"id": {
			"api": "",
			"header": {},
			"method": "",
			"data": "",
			"download": {
				"metadata": "",
				"filename": "",
				"metadata_filename": "",
				"header": {}
			},
			"op_symbol": {
				"id": "",
				"id_range": "",
				"eq": "",
				"lt": "",
				"gt": ""
			}
		}
	},
	"advanced": {
		"positioner": {
			"#root": "",
			"#id": "",
			"#md5": "",
			"#file_url": ""
		},
		"constant": {},
		"variable": {}
	}
}
```

网站模板是此程序的核心模块，尽管预设模板已经满足了大多数情况下的用户需求，用户通常没有必要理解模板内容的含义，但如果想使用本程序的高级功能，理解并能自行撰写网站模板是很有必要的。上方是一个空白模板，接下来将会将其分解并一一说明其用法与细节。

程序在运行时，会以`_base`模板为基础，将自定义模板与基底模板合并，随后检查模板内容是否合法，尽管大部分错误都可以在这一阶段找出，但错误的模板仍然可能导致一些预料之外的结果。

#### 模式（`mode`）

两种模式：`page` 和 `id`，需要在此处分别配置。

##### `page`模式

用于按页面下载。

- `api`：API 地址
- `header`：调用此 API 时的请求头信息
- `method`：调用此 API 时的 HTTP 请求方法（如 GET、POST）
- `data`：调用此 API 时的请求数据（针对 POST 等方法）
- `download`：下载图片时的配置
  - `metadata`：指定图片的元数据的具体内容
  - `filename`：指定图片文件名
  - `metadata_filename`：指定图片的元数据的文件名
  - `header`：下载时的请求头信息

##### `id`模式

用于按 ID 下载。

- `api`：API 地址
- `header`：调用此 API 时的请求头信息
- `method`：调用此 API 时的 HTTP 请求方法（如 GET、POST）
- `data`：调用此 API 时的请求数据（针对 POST 等方法）
- `download`：下载图片时的配置
  - `metadata`：指定图片的元数据的具体内容
  - `filename`：指定图片文件名
  - `metadata_filename`：指定图片的元数据的文件名
  - `header`：下载时的请求头信息
- `op_symbol`：查询时的操作符号配置
  - `id`：定义 ID 字段
  - `id_range`：定义 ID 范围字段
  - `eq`：定义等于操作符
  - `lt`：定义小于操作符
  - `gt`：定义大于操作符

#### 高级设置（`advanced`）

高级设置是网站模板能够灵活扩展的关键，该字段包含`positioner`、`constant`和`variable`。此字段下每个字段都有其独有的分隔符（delimiter）用以在引用时区分，引用方法为`分隔符+{+名称+}`，但在定义时应为`分隔符+名称`，名称仅应包含英文字母、数字和下划线且首字符不能为数字，这实际上类似于模板字符串。

高级设置下定义的内容可以在大部分字段中自由引用，这同样包含嵌套引用，甚至可以在部分字段的字段名中引用，高级设置的优先级从高至低分别为：`preset`->`positioner`->`constant`->`variable`，这代表了如果在嵌套引用时，`preset`会最先被解析，而`variable`将被最后解析，所有被引用内容在解析后都会保留其本来的数据类型。

**关于转义：如果模板字段内的静态字符串恰巧与高级设置内的引用格式相冲突，此时可以使用转义，例如需要表达"11${abc}22"，但字符串片段"${abc}"与引用预设变量的格式冲突，可以在其前面加上一个与对应的分隔符相同的字符以将其转义，即"$${abc}"，完整字符串为"11$${abc}22"**。

##### `preset`

预设变量，分隔符为`$`。尽管在自定义模板中并没有也不应该包含此字段，但实际上该字段是必不可少的，在运行时由程序自动添加和控制，无法被手动添加、删除和修改。

- `$tags`：运行参数`tags`
- `$page`：页面 ID，初始为 1，每次请求 API 后自增 1
- `$proxy`：运行参数`proxy`
- `$index`：数组下标，用于遍历从 API 获取到的图片 JSON 数组

##### `positioner`

定位器，分隔符为`#`。定义如何从获取到的数据中提取信息，其中`#root`、`#id`、`#md5`和`#file_url`是必要的。

- `#root`：根节点，用于指示数组的根路径
- `#id`：提取 ID 的路径
- `#md5`：提取 MD5 值的路径
- `#file_url`：提取文件 URL 的路径

##### `constant`

静态常量，分隔符为`@`。可以在此处定义 Cookie、用户名和密码等内容。**常量无法引用任何内容，只能为静态字符串。**

##### `variable`

动态变量，分隔符为`!`。动态变量实际上是 Python 代码片段，需要返回（return）的内容需要被赋值给名为`exec_result`的变量，而不是使用`return`关键字。

---

## 常见问题

### ModuleNotFoundError: No module named 'xxxxxx'

使用`pip install`命令下载对应的库即可。

### 使用 sankakucomplex 与 konachan 模板下载时报错

需要在模板文件中完善 Cookie 或用户名密码。

### 使用 danbooru 模板下载时提示已跳过一个未提供下载链接的文件

danbooru 部分图片需要 Danbooru Gold 才可查看，请参考[Upgrade Account](https://danbooru.donmai.us/upgrade)。

### 使用 rule34 模板时下载文件会一直校验失败

rule34 的 api 返回的 hash 有可能与实际文件 hash 不一致，建议在下载 rule34 的图片时将`chksums`置于`False`，此时程序仅会根据`Content-Length`响应头校验文件是否完整。

---

## 更新日志

### V2.0.3

1. 修复了 pyinstaller 打包后获取运行路径有误的问题。

### V2.0.2

1. 更新了网站模板。
2. 完善了文件完整性校验逻辑。
3. 完善了运行时的状态信息。

### V2.0.1

1. 删除了 update 模式。
2. 修复了下载时可能无法正常阻塞线程的 bug。
3. 完善了运行时的状态信息。

### V2.0.0

1. 项目名修改为 danbooru_downloader，现在支持 danbooru 和基于 danbooru 修改的大部分图库。
2. 添加了自定义网站模板功能。
3. 添加了更改日志记录级别功能。
4. 完善了去重功能并添加自定义选择去重模式功能，不再依靠文件名去重。
5. 添加了记录图片元数据功能。
6. 添加了不打印日志功能。
7. 添加了一些预设模板。
8. 完善了运行时的状态信息。
9. 优化了代码逻辑。

### V1.5.2

1. 修复了部分场景下最大失败重试次数不生效的 bug。

### V1.5.1

1. 代码规范性改进。
2. 添加了生成空白配置文件功能。
3. 添加了自定义最大失败重试次数功能。
4. 修改了参数格式及帮助信息。

### V1.4.1

1. 添加了使用配置文件进行下载功能。
2. 添加了校验文件完整性功能。
3. 修改了命令行参数格式及帮助信息。

### V1.3.4

1. 代码规范性改进。
2. 调整了目录结构。
3. 完善了运行时的状态信息。

### V1.3.1

1. 重写了日志模块（修复了日志记录可能不完整的 bug、添加了根据日志类型在控制台输出日志颜色）。

### V1.2.5

1. 美化代码，更换更新接口。

### V1.2.0

1. 修改了通过图片 ID 区间下载时获取图片列表的方法，不再使用估算值。

### V1.1.1

1. 修改了代码逻辑：将图片链接添加到下载列表前判断 file_url 键是否存在。

### V1.1.0

1. 添加了在线更新功能。
2. 修改了帮助信息。

### V1.0.3

1. 添加了错误处理。
2. 修改了下载器判断下载任务完成的逻辑，减少卡死几率。

### V1.0.1

1. 添加了版权信息。

### V1.0.0

1. 正式版上线。
