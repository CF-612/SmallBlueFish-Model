> 2026-10-30 交接记录。工程与脚本附件正在准备上传；本文不表示新 VRM 已导出或发布。已发布可运行原型仍为 alpha.2。

# DOT 增量迁移交接（非整源替换）

## 边界与现状

本机负责睫毛、眼睑、耳根、发根、真实口腔、袖形修复。以本机缺图恢复及后续修复源为主；**不得用本包 alpha3 候选整源覆盖本机 recovered 源**。本目录仅供定向迁移，未执行本机合并，也不证明目标宿主验收。不要把本机未完成口腔或未批准袖形、尾巴混进 DOT 已批准增量。

DOT 辅助脚本验证基线 SHA256：`3cce2c0e36497c7ba659c5541382f94c7f2f04fd50e05fcb18f43f410a34666f`。此哈希仅定义旧基线，不要求本机回退；目标发生拓扑、键名、UV、材质变化时必须重新建立对应，不能绕过 assert 强行套用。

所有脚本均为手动导入函数，不提供一键批处理。使用 Blender 的 bpy、mathutils、VRM 插件数据；部分依赖 numpy。先存本机独立候选，记录目标哈希及对象/键/绑定清单，再只运行选定 helper。脚本内 guard 不等同于完整迁移安全检查。

## 已批准外观增量（仍须目标兼容检查）

| helper / 函数 | 对象、键、材质与表达式影响 | 前置与冲突 guard |
|---|---|---|
| `install_post_alpha2_star.py` / `install_post_alpha2_star()` | 新建两侧 `ReferenceStarIris_*`（旧基线各579顶点），新增白色 MToon 材质与两侧蓝底材质；复制 `TrueEyeSurface_*` 全部非Basis键。创建/接通 `eyeStar`、`starEyes`、`starEnterSmall`、`starPulseExpand`、`starPulseContract`，跟随原虹膜形变；保留 watery/sparkling 绑定。停用旧 `ApprovedSpecial_starEyes_*` 并移除其 morph binds。 | `WhaleHumanoid`、两侧 `TrueEyeSurface_*`、head骨骼、原虹膜网格及UV须对应；脚本硬编码原虹膜前8181顶点范围和空间尺寸，改拓扑/变换后必须重建映射。检查无同名新对象/材质冲突。已有 `post_alpha2_star_v1` 返回；旧 `reference_star_iris_v1` 会拒绝。检查原生中性态压缩烘焙也涵盖新增对象，不能只复制可见网格。 |
| `suppress_confirmed_pink_fragments.py` / `suppress_confirmed_pink_fragments()` | 仅 `donor_tripo_part_37/38` 全壳各30面分配复制的 `*_ConfirmedPinkFragmentAlphaZero` MToon BLEND/alpha0、关闭透明Z写入；不删网格，不改形态键、UV、纹理像素，不触碰白虹膜高光。 | 对象必须仍是已确认粉片；源贴图名及UV中心粉色多数采样 guard 必须通过。本机若重建/合并此壳，先人工重新确认归属。已有 `confirmed_pink_fragment_suppressed_v1` 跳过。目标宿主须验证透明材质导出。 |
| `remove_confirmed_wrong_donor41.py` / `remove_confirmed_wrong_donor41()` | 删除独立灰片 `donor_tripo_part_41` 及所有指向它的 morph binds；旧基线为24顶点28面、39绑定。不改其他虹膜/眼白/高光。 | 脚本检查mesh及 `tripo_part_41_material*` 材质身份；迁移前额外核对24顶点28面和空间位置，不可因同名直接删本机新部件。对象已不存在返回。必须对删除前后导出绑定作差分。 |

推荐先37/38、后41，再在虹膜接口确认后迁新星；新星与粉片清理彼此独立。不迁入任何旧96顶点rim helper。

## 嘴部：仅历史效果对比，禁止自动迁入本机新口腔

以下 helper 已附带，但**不是新口腔迁移方案**。全部限定旧基线完整脸/口腔结构，尤其 MouthRim 为384顶点。即使顶点数相同，也必须匹配原索引和空间；本机真实开口/口缘/牙列重建后默认视为冲突。

| helper / 函数 | 精确影响 | 前置、顺序与冲突 |
|---|---|---|
| `polish_feisty_upper_occlusion.py` / `polish_feisty_upper_occlusion()` | 为 `SharedDentalArches` 新增 `postAlpha2FeistyRootOcclusion`；在 `feisty`、`mouthFeisty` 所用 `dental_oral_feisty` 绑定旁新增修正。旧牙网格3328顶点：上牙根/牙龈1628顶点后退3mm、下移6mm，并将犬齿冠上沿贴原口腔顶；不改旧键、MouthRim、TrueOralBag、舌、下牙弓。无新材质。 | 必须旧3328牙列、384 MouthRim、TrueOralBag末96顶点及roof索引完全一致。函数不幂等；已有修正键或绑定即停，禁止重复运行。不可用来掩盖新口腔连接问题。 |
| `sync_cancelled_and_smile_aliases.py` / `sync_cancelled_and_smile_aliases()` | 只改 `angry/happy/relaxed` 口部 morph/material/texture binds；angry取消旧05嘴并恢复overrideMouth=none；happy复制12闭笑，relaxed闭笑强度保留0.35；眼眉绑定保留。几何键不改。 | 要求旧 `mouthSmile` 含 `closedSmileArc`，已取消 mouthFrown/mouthOpenSpiral。ORAL对象集合硬编码；新口腔对象可能不在集合内，绝不可直接执行。旧结构对比时先运行它，再运行下一项。 |
| `install_shared_closed_smile_branch.py` / `install_shared_closed_smile_branch()` | 新建 `SharedClosedSmileBranch`（384顶点192四边面），仅Basis/ClosedSmileBranch；为旧MouthRim新增 `postAlpha2ClosedSmileRimRetreat`，替换 `mouthSmile/happy/relaxed` 的 closedSmileArc消费者。原rim Basis/旧键不改，复用旧材质；闭笑终点取旧12，归零细带位于旧脸皮后20µm。 | assert旧rim384及无已有分支；需要旧 `donor_tripo_part_1` 表面射线投射。真实口洞或脸拓扑变化将破坏零态遮挡，不可照搬。须验证0/.25/.35/.5/.75/1、正反/reset、正侧面、原生导出，不以384数量代替对应验证。 |

## 眼白过渡：仅可选候选，不在默认 alpha3 模型中

文件另见 `../optional-eye-transition/`，不与上述安全清理混为一项。v10外观已获认可，但最终兼容性仍有边界；v11几何与v10一致，仅为六个gaze/shadow表达式增加原生alpha退隐。

两版 `add_sclera_skin_feather(width=.0025,bands=4)` 新建两侧 `ScleraSkinFeather_*`、八个渐变MToon材质，复制脸部边界相关形态键和绑定；不改原脸/虹膜顶点。依赖旧 `donor_tripo_part_1`、`TrueLidSkin_*` 材质/UV边界、`TrueEyeSurface_*` 与 `CompleteOriginalIrisRim_*`。本机眼睑重建后边界对应必须重做，已有同名对象应先核对，不能凭跳过逻辑认为已升级。

v11在 blink/符号退隐之外，对 lookLeft/Right/Up/Down、shadowLarge/Small 额外绑定8材质alpha0。已有subset原生测试验证52组单控、正反、联合与归零符合three-vrm加法语义；**多控叠加会得到负opacity，不是clamp0**，未完成WebGL/目标宿主联合视觉验收。因此默认不安装，不能声称眼白迁移已全部合格。

## 目标验收与留存

1. 本机独立候选上逐helper操作，保存实际diff和哈希；任何身份guard不符立即停，不改assert。
2. 新星：中性隐藏、进入/呼吸极值、眨眼、四向gaze、压缩与reset；保留原watery/sparkling能力。
3. 粉片/灰片：正常、半闭、全闭、惊讶、缩瞳、左右gaze及reset；白高光必须仍在。
4. 导出后检查真实MToon/材质alpha及所有原生表达式绑定，核对metadata、骨架物理、原有动画接口未丢。CPU数值测试不等于Unity画面验收。
5. 本机负责的口腔、睫毛、耳根、发根、袖形保持独立验收记录；DOT不替代这些完成状态。

`helper-manifest.json` 给出逐文件SHA256，helper为原件复制，无自动保存/导出/发布动作。本交接未包含原始路线文档、私有会话标识或机器绝对路径。
