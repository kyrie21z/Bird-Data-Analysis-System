# “智巡千羽”品牌同步设计

## 目标

将当前项目的页面品牌与 `C:\Users\kyrie\Desktop\bird-detector` 保持一致。所有六个 HTML 页面使用参考项目的图标和“智巡千羽”名称，同时保持现有页面布局、功能和非品牌文字样式不变。

## 资源与结构

- 将参考项目根目录的 `icon.png` 原样复制到 `frontend/assets/images/icon.png`。
- 将 `AaMeiRenZhuan-JianFan-Web.woff2` 原样复制到 `frontend/assets/fonts/`。
- 新建 `frontend/css/branding.css`，集中声明 `@font-face`、品牌图标尺寸和品牌标题字体。
- 六个页面均引用共享样式，避免重复的字体和图标规则。

Flask 已将 `frontend/` 配置为根静态目录，因此页面通过 `/assets/images/icon.png` 和 `/assets/fonts/AaMeiRenZhuan-JianFan-Web.woff2` 访问资源，无需新增后端路由。

## 页面变更

每个页面的 `<head>` 添加 PNG favicon 和共享品牌样式。首页浏览器标题改为“智巡千羽”；子页面保留功能前缀，例如“数据管理 - 智巡千羽”和“观测趋势分析 - 智巡千羽”。

导航栏原有 Font Awesome 鸟图标与“鸟类数据分析系统 V1.0”替换为参考 PNG 图标及包裹在 `.brand-title` 中的“智巡千羽”。只有 `.brand-title` 使用美人篆；导航链接、正文、卡片标题、页面标题及其他文字继续使用当前字体。浏览器标签标题无法指定字体，因此该限制仅适用于页面内可见品牌标题。

## 回退与兼容

字体声明使用 `font-display: swap`，并配置中文无衬线回退字体。若字体加载失败，标题仍保持可读。图标使用明确尺寸和 `object-fit: contain`，避免原始大尺寸 PNG 改变导航栏高度。

## 验收

- 六个页面的浏览器标题均不再包含“鸟类数据分析系统”。
- 六个页面均声明相同 favicon，并显示相同导航栏图标和“智巡千羽”。
- 美人篆的 CSS 选择器只命中 `.brand-title`。
- 所有本地静态资源可由 Flask 返回，页面不产生图标、字体或样式 404。
- 运行 `python -m compileall backend`，并对六个页面执行静态检查或浏览器烟雾测试。
