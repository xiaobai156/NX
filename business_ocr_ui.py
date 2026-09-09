from __future__ import annotations

import json
import tempfile
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QThread, Signal, QTimer, QEventLoop
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QPlainTextEdit,
    QSpinBox, QVBoxLayout, QWidget,
)


class ScanThread(QThread):
    done = Signal(dict)

    def __init__(self, image_root: str, truth_root: str, issue: int):
        super().__init__(); self.image_root, self.truth_root, self.issue = image_root, truth_root, issue

    def run(self):
        exts = {".jpg", ".jpeg", ".png", ".webp"}
        images = sum(1 for p in Path(self.image_root).rglob("*") if p.is_file() and p.suffix.lower() in exts)
        truths = sum(1 for p in Path(self.truth_root).glob(f"*_{self.issue}期.txt") if p.is_file()) if self.truth_root else 0
        self.done.emit({"images": images, "truths": truths, "issue": self.issue})


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("专用 OCR 训练软件 0.1.3（界面预览版）"); self.resize(860, 620)
        self.image = QLineEdit(); self.image.setText(r"C:\Users\Administrator\Desktop\每天工具\飞机抓图\结果")
        self.truth = QLineEdit(); self.issue = QSpinBox(); self.issue.setRange(1, 99999); self.issue.setValue(251)
        self.gpu = QLabel("未检查"); self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        root = QVBoxLayout(); paths = QGroupBox("数据批次"); form = QFormLayout()
        form.addRow("图片目录", self._path_row(self.image)); form.addRow("答案目录", self._path_row(self.truth)); form.addRow("目标期数", self.issue)
        paths.setLayout(form); root.addWidget(paths)
        bar = QHBoxLayout()
        for text, slot in [("检查环境", self.doctor), ("扫描数据", self.scan), ("生成样本", self.placeholder), ("开始训练", self.placeholder), ("测试模型", self.placeholder), ("导出模型", self.placeholder)]:
            b = QPushButton(text); b.clicked.connect(slot); bar.addWidget(b)
        root.addLayout(bar); root.addWidget(QLabel("GPU状态：")); root.addWidget(self.gpu); root.addWidget(QLabel("日志")); root.addWidget(self.log)
        w = QWidget(); w.setLayout(root); self.setCentralWidget(w)

    def _path_row(self, edit):
        row = QWidget(); lay = QHBoxLayout(row); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(edit)
        b = QPushButton("选择"); b.clicked.connect(lambda: self.choose(edit)); lay.addWidget(b); return row

    def choose(self, edit):
        p = QFileDialog.getExistingDirectory(self, "选择目录")
        if p: edit.setText(p)

    def doctor(self):
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], capture_output=True, text=True, timeout=8, creationflags=subprocess.CREATE_NO_WINDOW)
            if out.returncode: raise RuntimeError(out.stderr.strip() or "nvidia-smi 失败")
            self.gpu.setText("显卡可见：" + out.stdout.strip()); self.log.appendPlainText("显卡查询完成（OCR CUDA 链路尚未验证）。")
        except Exception as e:
            self.gpu.setText("不可用"); self.log.appendPlainText(f"环境检查失败：{e}")

    def scan(self):
        if hasattr(self, 'scan_worker') and self.scan_worker.isRunning(): return
        if not self.image.text().strip() or not Path(self.image.text()).is_dir(): return QMessageBox.warning(self, "无法扫描", "图片目录不存在。")
        if not self.truth.text().strip() or not Path(self.truth.text()).is_dir(): return QMessageBox.warning(self, "无法扫描", "请先选择真实答案目录。")
        self.log.appendPlainText("开始只读扫描……"); self.scan_worker = ScanThread(self.image.text(), self.truth.text(), self.issue.value()); self.scan_worker.done.connect(self.scan_done); self.scan_worker.start()

    def scan_done(self, result):
        self.log.appendPlainText(json.dumps(result, ensure_ascii=False)); self.log.appendPlainText("扫描完成。当前版本尚未解析 TXT 或生成训练样本。")

    def placeholder(self):
        QMessageBox.information(self, "第一版", "此按钮已预留；TXT 解析、GPU定位、训练和导出将在通过真实数据核对后实现。")

    def closeEvent(self, event):
        if hasattr(self, 'scan_worker') and self.scan_worker.isRunning():
            event.ignore()
            self.log.appendPlainText("请等待扫描完成再关闭。")
        else:
            event.accept()


def self_check(app, win, destination):
    """Exercise the packaged application's real widgets using isolated fixtures."""
    import traceback
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    try:
        assert win.isVisible() and win.windowHandle().isExposed(), 'Main window not exposed'
        buttons = {b.text(): b for b in win.findChildren(QPushButton)}
        buttons['检查环境'].click()
        assert win.gpu.text() != '未检查'
        with tempfile.TemporaryDirectory(prefix='ocr_ui_check_') as folder:
            base = Path(folder)
            (base / 'sample.JPG').write_bytes(b'file-count-only-fixture')
            (base / '群_251期.txt').write_text('3头 齐天大圣（已分流）', encoding='utf-8')
            (base / '群_1251期.txt').write_text('', encoding='utf-8')
            win.image.setText(folder); win.truth.setText(folder); win.issue.setValue(251)
            buttons['扫描数据'].click()
            assert win.scan_worker.wait(10000), 'Scan timed out'
            loop = QEventLoop(); QTimer.singleShot(200, loop.quit); loop.exec()
            counts = [json.loads(line) for line in win.log.toPlainText().splitlines() if line.startswith('{')]
            assert counts == [{'images': 1, 'truths': 1, 'issue': 251}], win.log.toPlainText()
            dialogs = []
            def close_dialog():
                for widget in app.topLevelWidgets():
                    if isinstance(widget, QMessageBox) and widget.isVisible():
                        dialogs.append(widget.text()); widget.accept()
            win.truth.clear()
            QTimer.singleShot(100, close_dialog); buttons['扫描数据'].click()
            assert dialogs[-1] == '请先选择真实答案目录。'
            QTimer.singleShot(100, close_dialog); buttons['开始训练'].click()
            assert '此按钮已预留' in dialogs[-1]
            win.truth.setText(folder)
            loop = QEventLoop(); QTimer.singleShot(200, loop.quit); loop.exec()
            assert win.grab().save(str(target / 'ui-check.png'))
        (target / 'ui-check.json').write_text(json.dumps({'status':'passed', 'executable':sys.executable, 'checks':['main window exposed', 'GPU query button', 'isolated scan: 1 image, 1 matching TXT', 'empty truth directory rejected', 'training placeholder dialog'], 'gpu':win.gpu.text()}, ensure_ascii=False, indent=2), encoding='utf-8')
        app.exit(0)
    except Exception:
        (target / 'ui-check.json').write_text(traceback.format_exc(), encoding='utf-8')
        app.exit(1)


if __name__ == "__main__":
    app = QApplication(sys.argv); win = MainWindow(); win.show()
    if len(sys.argv) == 3 and sys.argv[1] == '--self-check':
        QTimer.singleShot(1000, lambda: self_check(app, win, sys.argv[2]))
    sys.exit(app.exec())


