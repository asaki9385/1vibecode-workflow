---
description: 启动/继续 VibeCode 产品视频工作流
---

请读取并严格遵循 .claude/skills/vibecode-agent.md 中定义的工作流：

1. 首先读取 state/workflow.json（如不存在则视为INIT阶段）
2. 根据当前stage，按vibecode-agent.md的对应阶段说明继续执行
3. 如涉及网页构建阶段（BUILD_PROJECT），同时读取
   .claude/skills/hero-shot-builder.md 获取详细指导

如果当前是新workflow（INIT阶段），先检测 input/ 目录是否有图片，
按skill说明进行后续操作。