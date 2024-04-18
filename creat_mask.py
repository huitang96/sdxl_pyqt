from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRect

import cv2
import numpy as np
class SaveImage():
    def __init__(self):
        self.image = None
        self.mask = None
    def read_image_from_pixmap(self, pixmap):
        # 将QPixmap格式的图片转换为OPenCV格式
        image = pixmap.toImage()
        width = image.width()
        height = image.height()
        bytes_per_line = image.bytesPerLine()
        data = image.bits().asarray(height * bytes_per_line)
        image = np.array(data).reshape((height, width, 4))
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        return image

    def saveImage(self, mask_aera, imagePixmap, Pixmap=False):
        mask_aera_xx, mask_aera_xy, mask_aera_yx, mask_aera_yy = mask_aera
        # 读取图片
        # imagePixmap = QPixmap("./image/img_2.png")  # 初始化图像
        imageCV = cv2.imread("./image/img_2.png")
        image = imageCV
        if Pixmap: # 将pixmap格式转换为cv2格式
            image = self.read_image_from_pixmap(imagePixmap)
        # 获取图片的尺寸
        height, width, _ = image.shape
        # 创建一个与原始图片相同大小的全黑图片
        temp = np.zeros((height, width), dtype=np.uint8)
        origin = image.copy()
        temp[mask_aera_xx:mask_aera_xy, mask_aera_yx:mask_aera_yy] = 1 # 将temp中指定区域与原图做与运算
        # 保存修改后的temp
        mask = cv2.bitwise_and(image, image, mask=temp) # 将temp和原始图片进行位运算
        # 将原始图片和掩码图片保存下来
        cv2.imwrite("./image/img_2_temp.png", origin)
        cv2.imwrite("./image/img_2_mask.png", mask)
        print("已保存掩码坐标")

# 测试函数
# if __name__ == "__main__":
#     app = QApplication([])
#     save_image = SaveImage()
#     mask_aera = (0, 500, 0, 500)
#     save_image.saveImage(mask_aera, Pixmap=True)

class DrawWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawWidget, self).__init__(parent)
        self.image = QPixmap("./image/img_2.png")  # 初始化图像
        self.is_drawing_rect = False
        self.start_point = None
        self.end_point = None
        self.pen_color = QColor(255, 255, 255, 125)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)
        # 打印self.image的尺寸
        print(self.image.size())
        if self.end_point is not None and self.start_point is not None:
            pen = QPen(self.pen_color, 25, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            # 使用 fillRect() 方法填充矩形区域
            brush = QBrush(self.pen_color)
            painter.setBrush(brush)
            rect_to_draw = QRect(self.start_point, self.end_point).normalized()
            painter.fillRect(rect_to_draw, brush)
            # 打印矩形区域的尺寸
            print("Rectangle size:", rect_to_draw.size())
            # 分解为横坐标的起始，纵坐标的起始值
            print("Rectangle start point:", self.end_point.x(), self.start_point.y())
            print("Rectangle end point:", self.end_point.x(), self.end_point.y())

            save_image = SaveImage()
            mask_aera = (self.start_point.x(), self.end_point.x(), self.start_point.y(), self.end_point.y())
            save_image.saveImage(mask_aera, self.image, Pixmap=True)


    def mousePressEvent(self, event):
        self.is_drawing_rect = True
        self.start_point = event.pos()

    def mouseReleaseEvent(self, event):
        self.is_drawing_rect = False
        self.end_point = event.pos()
        self.update()
    def mouseMoveEvent(self, event):
        pass  # 不需要处理鼠标移动事件，因为我们只在鼠标按下和松开时绘制矩形

if __name__ == "__main__":
    app = QApplication([])
    label = QLabel() # 整个画布
    draw_area = DrawWidget()  # 创建自定义绘图区域
    layout = QVBoxLayout()
    layout.addWidget(draw_area)  # 将绘图区域添加到布局中
    label.setLayout(layout)
    # 显示窗口
    label.show()
    app.exec()