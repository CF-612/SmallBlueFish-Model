# 大面积阴影实验旧版归档

本批保存 14 个被替代的制作实验，不代表当前最终模型。原工程合计 927,874,063 字节，含完整恢复基准的归档合计 167,620,766 字节。

在本目录运行：

```sh
sha256sum -c SHA256SUMS
python3 restore.py --verify-only --temp-dir /path/to/disk-temp
python3 restore.py --destination /path/to/whale-model-prep --temp-dir /path/to/disk-temp
```

需要 Python 3.10+ 与 zstd。分片会自动拼接，恢复后校验原始 SHA-256；不会覆盖内容不同的既有文件。完整恢复应留足原工程总字节空间，临时拼接还需要基准和最大差分的空间。

来源与非商用使用范围见[项目说明](../../README.md)。
