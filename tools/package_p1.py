"""Package an already validated P1 Windows build; never silently package stale sources."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile
ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'build/windows'
receipt_path = out / 'build-receipt.json'
receipt = json.loads(receipt_path.read_text())
sources = sorted(p for folder in ['scripts', 'scenes', 'data', 'assets'] for p in (ROOT / 'game' / folder).rglob('*') if p.is_file() and p.suffix not in ['.import', '.uid']) + [ROOT / 'game/project.godot', ROOT / 'game/export_presets.cfg']
if any(p.stat().st_mtime > receipt_path.stat().st_mtime for p in sources):
    raise SystemExit('Source newer than build receipt; rebuild before packaging')
for name, digest in receipt['sha256'].items():
    if hashlib.sha256((out / name).read_bytes()).hexdigest() != digest:
        raise SystemExit(f'Build hash mismatch: {name}')
receipt['runtime_revision'] = 2
receipt['source_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
shutil.copyfile(ROOT / 'game/assets/fonts/OFL.txt', out / 'OFL.txt')
shutil.copyfile(ROOT / 'docs/p1-expanded-validation.txt', out / 'validation.txt')
(out / 'README.txt').write_text('''夜潮事务所 — P1视觉版
解压后保持exe和pck同目录，双击night-tide.exe。离线运行，无需Godot/Python。
M01→结算→营地→保存读取→M02；当前标准难度、首发三人。
先选队员，再选基础行动或专长、目标，预览后确认。右侧内容可滚动。
专长显示剩余次数；许舟抛索点击落点，林岚移动急救先选伤员再选落点。
双人协作先选下拉框搭档；双方成本都会在预览列出。
“撤销上一组战术行动”恢复动作前状态；结束回合/任务结算/新承诺后不能跨边界撤销。
撤退承诺为明确选择，不选择不会因失败自动增加人际违约；营地认责与后续实际守约分别处理。
顶部“设置与存档”内保存/读取为手动槽；每个有效动作含撤销都会自动保存。
新版槽：user://saves/p1_expanded/。基础版p1_v1槽保留，此版不会补造旧档缺少的关系/专长历史。
本包请从新周目验证。Windows用户目录位于Godot app_userdata/夜潮事务所/。
阅读validation.txt了解测试范围。Windows实机/DPI/性能仍待用户验证，不以macOS导出替代。
Noto Sans CJK SC字体许可见OFL.txt。本包集成首发三人的立绘、棋子、场景及营地插画；不包含全游戏后续人物美术。
''', encoding='utf-8')
shutil.copyfile(ROOT / 'docs/ui-localization-plan.txt', out / 'ui-localization.txt')
shutil.copyfile(ROOT / 'docs/p1-visual-validation.txt', out / 'visual-validation.txt')
shutil.copyfile(ROOT / 'docs/p1-visual-assets.json', out / 'visual-assets.json')
package = ROOT / 'build/night-tide-windows-p1-visual.zip'
with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
    for name in ['night-tide.exe', 'night-tide.pck', 'build-receipt.json', 'README.txt', 'OFL.txt', 'validation.txt', 'ui-localization.txt', 'visual-validation.txt', 'visual-assets.json']:
        z.write(out / name, name)
with zipfile.ZipFile(package) as z:
    for name, digest in receipt['sha256'].items():
        assert hashlib.sha256(z.read(name)).hexdigest() == digest
report = {'date': '2026-11-05', 'scope': 'P1 integrated portrait/sprite/environment art and visual feedback with existing complete gameplay regression',
          'checks': {'reference': 1172, 'foundation': 33, 'content': 10, 'loop': 166, 'systems': 179, 'ui_localization': 286, 'visual': 544},
          'windows_native': 'pending_user_device_test', 'build': receipt,
          'package': str(package.relative_to(ROOT)), 'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
          'gui_external_screen': {'screen': 1, 'primary': 0, 'total': 2}}
(ROOT / 'docs/p1-visual-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(f'P1_PACKAGE_OK: {package} ({package.stat().st_size} bytes)')
