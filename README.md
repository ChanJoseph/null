# 一键 P 图

上传照片，说「P一下」或「好看就行」。技能会按主观审美直接出图，不用先选参数。

在这个仓库里，Agent 会读 `.cursor/skills/one-click-retouch/`。聊天框输入 `/one-click-retouch` 也可以手动挂上。

想在别的项目里用，把 `one-click-retouch` 文件夹复制到本机 `~/.cursor/skills/`。云端 Agent 要用这份个人技能时，在 Cursor 的 Settings → Agents 里打开 Sync Skills for Cloud Agents。

默认会参考原图重做一版更好看的成片，人和场景保留。说「别重画」或「只调色」时，只做轻度曝光、白平衡和锐化。证件、合同和必须保留文字的截图不会处理。
