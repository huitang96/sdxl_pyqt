from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QPixmap, QPen, QColor
from PyQt6 import QtCore


class DrawWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawWidget, self).__init__(parent)
        self.image = QPixmap("test.png")  # 初始化图像
        self.is_painting = False
        self.pen_color = QColor(255, 255, 255, 125)
        self.line_points = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

        if self.is_painting and self.line_points:
            pen = QPen(self.pen_color, 25, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            for i in range(len(self.line_points) - 1):
                start_point = self.line_points[i]
                end_point = self.line_points[i + 1]
                painter.drawLine(start_point, end_point)

    def mousePressEvent(self, event):
        self.is_painting = True
        self.line_points.append(event.pos())

    def mouseMoveEvent(self, event):
        if self.is_painting:
            self.line_points.append(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        # self.is_painting = False
        self.line_points.append(event.pos())  # 添加释放点，以完成最后一段线
        self.update()

if __name__ == "__main__":
    app = QApplication([])

    label = QLabel()
    draw_area = DrawWidget()  # 创建自定义绘图区域
    layout = QVBoxLayout()
    layout.addWidget(draw_area)  # 将绘图区域添加到布局中
    label.setLayout(layout)

    # 显示窗口
    label.show()

    app.exec()