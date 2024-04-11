
import os
import sys
import json
import torch
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt, QMetaObject, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QPixmap, QImage, QFont
from diffusers import StableDiffusionXLPipeline
from PyQt6.uic import loadUiType
from kits import read_config_paths

# 加载UI的头文件（仅加载一次）
Ui_MainWindow, _ = loadUiType('sdxlWebui.ui')

device = "cuda" if torch.cuda.is_available() else "cpu"
config_file = './config.ini'
_, checkpointPath = read_config_paths(config_file)

class InferenceService:
    def __init__(self, pipe):
        self.pipe = pipe

    def infer(self, text_prompt, parent):
        task = InferenceTask(text_prompt, parent)
        thread = QThread()
        task.moveToThread(thread)
        thread.started.connect(task.run)
        task.finished.connect(thread.quit)
        task.error_occurred.connect(parent.show_error_message)
        task.image_generated.connect(parent.update_image_label)
        thread.start()
    # def is_running(self):
    #     return self.task.is_running if self.task else False
class InferenceTask(QObject):
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    image_generated = pyqtSignal(QPixmap)
    def __init__(self, text_prompt, parent):
        super().__init__(parent)
        self.text_prompt = text_prompt
        self.parent = parent
        self.is_running = False
    def run(self):
        self.is_running = True
        # g = torch.Generator(device="cuda")
        try:
            outputs = self.parent.pipe(
                prompt=self.text_prompt,
                negative_prompt="worst quality, low quality, normal quality",
                seed=42,
                width=1024,
                height=1024,
                num_inference_steps=20,  # 迭代步数，默认值为50。
                guidance_scale=7.5,  # 指导比例，控制生成图像的细节与清晰度，默认值为7.5
                eta=0.0,
                output_type="pil",
                # generator=g, # 随机数生成
                # output_type="latent",
            )
            img = outputs.images[0].resize((1024, 1024))
            img.save("temp.png")
            image = QImage("temp.png")
            self.image_generated.emit(image)
        except Exception as e:
            self.error_occurred.emit(f"模型推理过程中发生错误：{str(e)}")
        finally:
            self.is_running = False
            self.finished.emit()
class mainWindow(QMainWindow, Ui_MainWindow):
    inference_start = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.text_prompt = ""
        self.setWindowTitle("手把手教你制作, 添加微信: artfulcode")
        self.ui.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 设置字体
        font = QFont("Times New Roman", 14)
        self.ui.plainTextEdit.setFont(font)
        self.pipe = None  # 初始化模型引用为空
        self.prompt_content_comboBox = "korea girl,looking at viewer,alleyway,collared_shirt,pale_skin,long hair,real world"
        self.ui.pushButton_2.setCheckable(True)
        self.ui.pushButton_2.clicked.connect(self.on_pushButton_2_clicked)
        self.ui.pushButton_3.setCheckable(True)
        self.ui.pushButton_3.clicked.connect(self.on_pushButton_3_clicked)
        self.ui.comboBox.currentTextChanged.connect(self.on_comboBox_currentTextChanged)
        self.load_model()
        self.setup_inference_service()
        self.is_generating = False  # 标记是否正在生成

    def load_model(self):
        try:
            model_path = checkpointPath
            self.pipe = StableDiffusionXLPipeline.from_single_file(model_path, torch_dtype=torch.float16).to(device)
        except Exception as e:
            self.show_error_message(f"无法加载模型：{str(e)}")

    def show_error_message(self, message):
        QMessageBox.critical(self, "错误", message)

    def update_image_label(self, image):
        pixmap = QPixmap.fromImage(image)
        self.ui.image_label.setPixmap(pixmap)
        QTimer.singleShot(0, lambda: os.remove("temp.png"))  # 删除临时文件

    def setup_inference_service(self):
        self.inference_service = InferenceService(self.pipe)
        self.inference_start.connect(self.run_inference)

    def run_inference(self):
        # if self.pipe is not None and not self.inference_service.is_running:
        if self.pipe is not None:
            print("开始推理")
            self.is_generating = True
            text_content = self.ui.plainTextEdit.toPlainText() or "1dog,"
            self.text_prompt = text_content + self.prompt_content_comboBox
            self.inference_service.infer(self.text_prompt, self)

    def on_comboBox_currentTextChanged(self, text):
        data = self.read_json("sdxl_styles/sdxl_styles.json")
        self.prompt_content_comboBox = self.get_prompt_for_name(text, data)

    def get_prompt_for_name(self, name, data):
        for item in data:
            if item["name"] == name:
                return item.get('prompt')
        return ""

    def on_pushButton_3_clicked(self):
        self.is_generating = False
        self.ui.image_label.clear()
        print("清除图片显示")

    def on_pushButton_2_clicked(self):
        if not self.is_generating:
            self.inference_start.emit()
        else:
            print("已经在生成中，请勿重复点击")

    def read_json(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.show_error_message(f"无法读取或解析JSON文件：{str(e)}")
            return {}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec())
