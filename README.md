# SmallBlueFish-Model

小肥鱼模型的制作、修复与版本归档。项目仍在制作中，这里的旧版工程不是最终发布模型。

## 原型下载

当前试验版：[v0.1.0-alpha.2 发布页](https://github.com/CF-612/SmallBlueFish-Model/releases/tag/v0.1.0-alpha.2)。

- [下载完整原型包（ZIP，约 199 MiB）](https://github.com/CF-612/SmallBlueFish-Model/releases/download/v0.1.0-alpha.2/SmallBlueFish-v0.1.0-alpha.2-prototype.zip)
- 解压后使用 `model/SmallBlueFish-v0.1.0-alpha.2.vrm`，格式为 VRM 1.0。使用说明和已知限制见包内文档。
- 请下载上述命名原型包；GitHub 自动生成的 Source code ZIP 是仓库快照。
- 此版本用于原型测试，仍有待修细节；后续修改不会自动更新已下载文件。

原型 ZIP 的 SHA-256：

```text
0c481fc0d57bc8a1634138c6b260603dd6f91511139391ced9fc78e2aab4663c
```

## 当前进度

已归档 **75 个旧版实验工程**：原文件合计约 **4.12 GB**，含完整恢复基准的无损归档约 **652 MB**。每批都已从 GitHub 独立下载，恢复后逐一核对原始 SHA-256。

| 批次 | 旧版数量 | 清单与恢复入口 |
| --- | ---: | --- |
| 头饰诊断 | 16 | [根目录清单](MANIFEST.json) |
| 大面积阴影 | 14 | [阴影归档](archive/shadow-20261029/) |
| 口腔制作 | 11 | [口腔归档](archive/oral-20261029/) |
| 早期眼睑与视线 | 23 | [眼睑归档](archive/old-lids-20261029/) |
| 早期视线分层 | 11 | [视线分层归档](archive/early-gaze-20261029/) |

当前模型仍在调整，本仓库的归档不代表最新制作状态。

## 恢复旧版

需要 Python 3.10+ 和 `zstd` 命令行工具（已用 Zstandard 1.5.7 测试）。下载仓库后，进入需要恢复的批次目录；头饰诊断使用仓库根目录。

```sh
sha256sum -c SHA256SUMS
python3 restore.py --verify-only
python3 restore.py --destination /path/to/whale-model-prep
```

每批均可独立恢复，不依赖原电脑上的文件。脚本会自动拼接基准与差分分片，核对原始 SHA-256，并拒绝覆盖内容不同的既有文件。请按该批 `MANIFEST.json` 的 `original_bytes` 留足恢复空间，另留约 100 MB 临时空间；恢复全部批次约需 4.2 GB。

这些工程使用 Blender 5.2.3 保存，贴图已内嵌。

## 来源与使用范围

模型起点是项目所有者提供的 Tripo 生成头部、身体和尾部，之后进行了网格、材质、头饰与表情修复。

人设参考来自 B站「这个刀子真甜」（UID 23315338）的[原帖](https://www.bilibili.com/opus/1234477753856688168)。根据 2026-10-28 的来源核验记录，作者在 2026-08-28 的三创询问下回复 **“不商用随便做”**。本项目保留这一非商用要求，不额外授予商用权利，也未添加独立开源许可证。

来源记录另注明原版形象来自 @ZipZipPipe 与 @上善无形。本项目并非官方 DeepSeek 角色发布。
