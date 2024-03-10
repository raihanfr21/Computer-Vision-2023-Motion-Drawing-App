import cv2
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
from handTracker import *

class ColorRect():
    def __init__(self, x, y, w, h, color, text='', alpha=0.5):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.alpha = alpha

    def draw_rect(self, img, text_color=(255, 255, 255), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        alpha = self.alpha
        bg_rec = img[self.y: self.y + self.h, self.x: self.x + self.w]
        white_rect = np.ones(bg_rec.shape, dtype=np.uint8)
        white_rect[:] = self.color
        res = cv2.addWeighted(bg_rec, alpha, white_rect, 1 - alpha, 1.0)
        img[self.y: self.y + self.h, self.x: self.x + self.w] = res

        text_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)
        text_pos = (int(self.x + self.w / 2 - text_size[0][0] / 2), int(self.y + self.h / 2 + text_size[0][1] / 2))
        cv2.putText(img, self.text, text_pos, fontFace, fontScale, text_color, thickness)

    def is_over(self, x, y):
        if (self.x + self.w > x > self.x) and (self.y + self.h > y > self.y):
            return True
        return False

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Motion Drawing")
        self.root.configure(bg="#F0F0F0")  

        app_name_label = tk.Label(root, text="Motion Drawing", font=("Comic Sans MS", 28, "bold"), bg="#F0F0F0", fg="#3B3B3A")
        app_name_label.pack(pady=50)
    
        start_icon = Image.open("C:\\Users\\Administrator\\Downloads\\virtual_painter-main\\virtual_painter-main\\images\\start-button_5261298.png")
        quit_icon = Image.open("C:\\Users\\Administrator\\Downloads\\virtual_painter-main\\virtual_painter-main\\images\\exit-door_3989443.png")

        start_icon = start_icon.resize((110, 110), Image.ANTIALIAS)
        quit_icon = quit_icon.resize((100, 100), Image.ANTIALIAS)

        start_icon_tk = ImageTk.PhotoImage(start_icon)
        quit_icon_tk = ImageTk.PhotoImage(quit_icon)

        start_button = tk.Button(root, image=start_icon_tk, command=self.start_application, bd=0)
        start_button.image = start_icon_tk  
        start_button.pack(pady=25)

        quit_button = tk.Button(root, image=quit_icon_tk, command=root.destroy, bd=0)
        quit_button.image = quit_icon_tk  
        quit_button.pack(pady=25)

    def start_application(self):
        self.root.destroy()  
        main()


def main():
    root = tk.Tk()
    root.title("Motion Drawig")

    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    canvas = np.zeros((720, 1280, 3), np.uint8)
    detector = HandTracker(detection_confidence=0.8)

    px, py = 0, 0
    color = (255, 0, 0)
    brush_size = 5
    eraser_size = 20

    colors_btn = ColorRect(200, 0, 100, 100, (120, 255, 0), 'Warna')
    colors = [ColorRect(300, 0, 100, 100, (255, 0, 0)),
              ColorRect(400, 0, 100, 100, (0, 0, 255)),
              ColorRect(500, 0, 100, 100, (0, 255, 0)),
              ColorRect(600, 0, 100, 100, (255, 0, 0)),
              ColorRect(700, 0, 100, 100, (0, 255, 255)),
              ColorRect(800, 0, 100, 100, (0, 0, 0),)]
    clear_btn = ColorRect(900, 0, 100, 100, (100, 100, 100), "Hapus")

    pens = [ColorRect(1100, 50 + 100 * i, 100, 100, (50, 50, 50), str(pen_size)) for i, pen_size in enumerate(range(5, 25, 5))]
    pen_btn = ColorRect(1100, 0, 100, 50, color, 'Pena')

    board_btn = ColorRect(50, 0, 100, 100, (255, 255, 0), 'Kanvas')
    white_board = ColorRect(50, 120, 1020, 580, (255, 255, 255), alpha=0.6)

    selected_menu = None

    cooling_counter = 20
    hide_board = True
    hide_colors = True
    hide_pen_sizes = True

    def on_mouse_click(event):
        nonlocal selected_menu, hide_board, hide_colors, hide_pen_sizes, cooling_counter, color, brush_size, canvas, px, py

        x, y = event.x, event.y

        if selected_menu is not None:
            if selected_menu == 'Pena':
                for pen in pens:
                    if pen.is_over(x, y):
                        brush_size = int(pen.text)
                        pen.alpha = 0
                    else:
                        pen.alpha = 0.5

            elif selected_menu == 'Warna':
                for cb in colors:
                    if cb.is_over(x, y):
                        color = cb.color
                        cb.alpha = 0
                    else:
                        cb.alpha = 0.5

                if clear_btn.is_over(x, y):
                    clear_btn.alpha = 0
                    canvas[:] = 0
                    px, py = 0, 0  
                else:
                    clear_btn.alpha = 0.5

        if colors_btn.is_over(x, y) and not cooling_counter:
            cooling_counter = 10
            hide_colors = not hide_colors
            colors_btn.text = 'Warna' if hide_colors else 'Tutup'
            selected_menu = 'Warna' if not hide_colors else None
        elif pen_btn.is_over(x, y) and not cooling_counter:
            cooling_counter = 10
            hide_pen_sizes = not hide_pen_sizes
            pen_btn.text = 'Pena' if hide_pen_sizes else 'Tutup'
            selected_menu = 'Pena' if not hide_pen_sizes else None
        elif board_btn.is_over(x, y) and not cooling_counter:
            cooling_counter = 10
            hide_board = not hide_board
            board_btn.text = 'Kanvas' if hide_board else 'Tutup'
            selected_menu = 'Kanvas' if not hide_board else None
        else:
            selected_menu = None

    def update_gui():
        nonlocal px, py, color, brush_size, canvas, selected_menu, cooling_counter, hide_colors, hide_board, hide_pen_sizes

        if cooling_counter:
            cooling_counter -= 1

        ret, frame = cap.read()
        if not ret:
            return

        frame = cv2.resize(frame, (1280, 720))
        frame = cv2.flip(frame, 1)

        detector.findHands(frame)
        positions = detector.getPostion(frame, draw=False)
        up_fingers = detector.getUpFingers(frame)

        if up_fingers:
            x, y = positions[8][1], positions[8][2]

            if selected_menu == 'Pen':
                if not hide_pen_sizes:
                    for pen in pens:
                        if pen.is_over(x, y):
                            brush_size = int(pen.text)
                            pen.alpha = 0
                        else:
                            pen.alpha = 0.5

            elif selected_menu == 'Colors':
                if not hide_colors:
                    for cb in colors:
                        if cb.is_over(x, y):
                            color = cb.color
                            cb.alpha = 0
                        else:
                            cb.alpha = 0.5

                    if clear_btn.is_over(x, y):
                        clear_btn.alpha = 0
                        canvas[:] = 0
                        px, py = 0, 0  
                    else:
                        clear_btn.alpha = 0.5

            if px != 0 and py != 0:
                cv2.circle(frame, (px, py), brush_size, color, -1)

            if white_board.is_over(x, y) and not hide_board:
                cv2.circle(frame, (x, y), brush_size, color, -1)
                if px == 0 and py == 0:
                    px, py = x, y
                if color == (0, 0, 0):
                    cv2.line(canvas, (px, py), (x, y), color, eraser_size)
                else:
                    cv2.line(canvas, (px, py), (x, y), color, brush_size)
                px, py = x, y
        else:
            px, py = 0, 0  

        colors_btn.draw_rect(frame)
        cv2.rectangle(frame, (colors_btn.x, colors_btn.y), (colors_btn.x + colors_btn.w, colors_btn.y + colors_btn.h),
                      (255, 255, 255), 2)

        board_btn.draw_rect(frame)
        cv2.rectangle(frame, (board_btn.x, board_btn.y), (board_btn.x + board_btn.w, board_btn.y + board_btn.h),
                      (255, 255, 255), 2)

        if not hide_board:
            white_board.draw_rect(frame)
            canvas_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, img_inv = cv2.threshold(canvas_gray, 20, 255, cv2.THRESH_BINARY_INV)
            img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
            frame = cv2.bitwise_and(frame, img_inv)
            frame = cv2.bitwise_or(frame, canvas)

        if not hide_colors:
            for c in colors:
                c.draw_rect(frame)
                cv2.rectangle(frame, (c.x, c.y), (c.x + c.w, c.y + c.h), (255, 255, 255), 2)

            clear_btn.draw_rect(frame)
            cv2.rectangle(frame, (clear_btn.x, clear_btn.y), (clear_btn.x + clear_btn.w, clear_btn.y + clear_btn.h),
                          (255, 255, 255), 2)

        pen_btn.color = color
        pen_btn.draw_rect(frame)
        cv2.rectangle(frame, (pen_btn.x, pen_btn.y), (pen_btn.x + pen_btn.w, pen_btn.y + pen_btn.h), (255, 255, 255), 2)

        if not hide_pen_sizes:
            for pen in pens:
                pen.draw_rect(frame)
                cv2.rectangle(frame, (pen.x, pen.y), (pen.x + pen.w, pen.y + pen.h), (255, 255, 255), 2)

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)

        panel.img = img
        panel.config(image=img)
        panel.after(10, update_gui)

    panel = tk.Label(root)
    panel.pack(padx=10, pady=10)

    root.bind("<Button-1>", on_mouse_click)
    update_gui()

    root.mainloop()

if __name__ == "__main__":
    root_main = tk.Tk()
    main_menu = MainMenu(root_main)
    root_main.mainloop()
