# SmallBlueFish-Model

Lossless history of superseded model-engineering experiments. These archived snapshots are development history, not the current approved or final character model.

## 来源与使用范围 / Attribution and use

- 网格起点是项目所有者提供的 Tripo 生成头部、身体、尾部模型；本项目加入了修复、材质、头饰和表情工程修改。
- 人设参考：B站「这个刀子真甜」（UID 23315338），[原帖](https://www.bilibili.com/opus/1234477753856688168)。
- 根据项目于 2026-10-28 保存的来源核验记录：在该帖评论中，用户“被咸死の鱼”于 2026-08-28 07:00 询问三创，作者于 07:21 回复“不商用随便做”。这记录的是非商用三创表态，不是完整权利链保证或商用许可；本仓库不额外授予商用权利，也不添加 MIT 等开放授权。
- 同一来源记录还注明原版形象来源 @ZipZipPipe 与 @上善无形。此项目不是官方 DeepSeek 角色发布。
- 未纳入 my-neuro / Charakuru 示例模型、原帖参考图文件、登录截图、账号信息、聊天或代理运行日志。仅存本项目模型快照及恢复所需文件。
- 旧导出物里的保守 VRM 权限字段属于当时的项目设置，不应被误称为原作者的独立禁令；公开存储本身也不扩展第三方授予的权利。

## Batch 1: superseded head-frill diagnostics

The 16 `.blend` models in `MANIFEST.json` are earlier, rejected or superseded head-frill diagnostic experiments. The complete v18 model is included as eight ordered byte-concatenation parts in `base/`, so recovery does not depend on files remaining on the original computer. The parts are a transport detail, not different model versions; `restore.py` automatically joins them in temporary storage and verifies the original base SHA-256. Each archived model is a Zstandard patch from that exact base. Base, patch, and restored original SHA-256 checksums are recorded.

Original source ZIP/materials, current master model, frozen increment assets, VRM deliveries, scripts, diagnostic images, and active experiments are not removed by this archive. The complete v18 base is also retained locally. Historical scripts may reference original model paths; restore the relevant archive into the original project root before re-running those scripts.

## Verify without writing large files

Install Python 3.10+ and the `zstd` command-line program (tested with Zstandard 1.5.7), then run:

```sh
python3 restore.py --verify-only
```

Allow about 68 MB of temporary disk space to reassemble the base. This decodes each archived model into a SHA-256 stream and checks the exact original byte count and hash. It does not write full restored models.

## Restore all archived originals

```sh
python3 restore.py --destination /path/to/whale-model-prep
```

Allow at least the `original_bytes` amount from `MANIFEST.json` as free disk space. Files are restored at their original relative paths. Matching existing files are left in place; different existing files are never overwritten. The script uses a temporary file in each target directory, verifies it, and then publishes it atomically without replacing existing data.

For one file manually:

```sh
cat base/shallow-fold-v18-PREVIEW.blend.part-????-of-0008 > /safe/new/path/base.blend
# Verify this base against the base SHA-256 in MANIFEST.json before decoding.
zstd -d --patch-from=/safe/new/path/base.blend deltas/NAME.blend.zst -o /safe/new/path/NAME.blend
sha256sum /safe/new/path/NAME.blend
```

Compare the output SHA-256 and byte count with `MANIFEST.json` before use.

## Storage and privacy

Only explicitly selected old model experiments and recovery metadata belong here. Do not add credentials, authentication screenshots, conversation/agent logs, unrelated projects, or raw whole-workspace backups. This archive uses normal Git objects, not Git LFS, and does not enable or purchase paid storage. Future batches should remain bounded and deduplicated; do not push tens of GB of raw `.blend` snapshots.
