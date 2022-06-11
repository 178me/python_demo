'''
@author: 178me
@description: window自动化操作
'''
try:
    import sys
    import warnings
    sys.coinit_flags = 2
    warnings.simplefilter("ignore", UserWarning)
except Exception as e:
    pass
import logging
import pywinauto
import pyautogui
import numpy as np
import cv2
from time import sleep, time
from random import randint
#  import easyocr

log = logging.getLogger('get_cookie')
log.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(levelname)s: %(message)s')
formatter.datefmt = "%H:%M:%S"
file_handler = logging.FileHandler('log.txt')
file_handler.setLevel(level=logging.WARN)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.addHandler(stream_handler)

screnn_width, screnn_height = pyautogui.size()

def smlMove(begin_x, begin_y, end_x, end_y, duration):
    xxy = []
    point = [
        {
            "x": begin_x,
            "y": begin_y
        },
        {
            "x": randint(begin_x-100, begin_x+100),
            "y": randint(begin_y, begin_y+50)
        },
        {
            "x": randint(end_x-100, end_x+100),
            "y": randint(end_y, end_y+50)
        },
        {
            "x": end_x,
            "y": end_y
        },
    ]

    def bezierCurves(cp, t):
        cx = 3.0 * (cp[1]["x"] - cp[0]["x"])
        bx = 3.0 * (cp[2]["x"] - cp[1]["x"]) - cx
        ax = cp[3]["x"] - cp[0]["x"] - cx - bx
        cy = 3.0 * (cp[1]["y"] - cp[0]["y"])
        by = 3.0 * (cp[2]["y"] - cp[1]["y"]) - cy
        ay = cp[3]["y"] - cp[0]["y"] - cy - by
        tSquared = t * t
        tCubed = tSquared * t
        return [int((ax * tCubed) + (bx * tSquared) + (cx * t) + cp[0]["x"]),
                int((ay * tCubed) + (by * tSquared) + (cy * t) + cp[0]["y"])]
    i = 0
    t = 0
    total_delay = 0
    distance = end_x - begin_x
    while t < 1:
        xxy.append(bezierCurves(point, t))
        if i > 0:
            mobile_distance = abs(xxy[i][0] - xxy[i-1][0])
            delay = duration * (mobile_distance / distance)
        else:
            delay = 0
        total_delay += delay
        xxy[i].append(delay)
        t += 0.08
        i += 1
    return xxy

class UtilsPos:
    def __init__(self):
        self.screnn_width, self.screnn_height = pyautogui.size()
        self.pag = pyautogui

    def find_image_by_template(self, template, target="all", find_time=5, **kw):
        timeout = time() + find_time
        images = []
        while time() < timeout:
            if target == "all":
                images = list(pyautogui.locateAllOnScreen(template, **kw))
            else:
                images = list(pyautogui.locateAll(template, target, **kw))
            if images:
                break
        return images

    def click_image(self, template, find_time=5, btn="left", delay=1, **kw):
        image = self.find_image_by_template(template, "all", find_time, **kw)
        if not image:
            #  raise Exception(f"{template} 图片未找到")
            return False
        point = pyautogui.center(image[0])
        sleep(delay)
        log.info(point)
        pyautogui.click(point.x, point.y, button=btn)

class Images:
    def __init__(self, app):
        self.app = app  # GUI需要
        self.screen = app.primaryScreen()

    def QImageToCvMat(self, incomingImage):
        '''  Converts a QImage into an opencv MAT format  '''
        qimg = incomingImage
        temp_shape = (qimg.height(), qimg.bytesPerLine()
                      * 8 // qimg.depth())
        temp_shape += (4,)
        ptr = qimg.bits()
        ptr.setsize(qimg.byteCount())
        result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
        result = result[..., :3]
        return result

    def window_screenshot(self, window_obj, image_name=None):
        ''' 窗口截图 '''
        try:
            hwnd = window_obj.element.handle
            if window_obj.get_dialog().is_minimized():
                window_obj.element.restore()
            img = self.screen.grabWindow(hwnd).toImage()
            if image_name:
                img.save(f"./image/{image_name}")
                return f"./temp/{hwnd}"
            img = self.QImageToCvMat(img)
            if isinstance(img, np.ndarray):
                return img
            raise Exception("图片格式未转换成功")
        except Exception as e:
            log.exception(e)
            raise Exception("窗口截图出错")

    def get_center_point(self, point):
        ''' 返回中心坐标 '''
        center_x = int(point[0] + (point[2] / 2))
        center_y = int(point[1] + (point[3] / 2))
        return (center_x, center_y)

    def find_image(self, query_image_path, window_object, **option):
        ''' 查找图片 '''
        if "find_way" in option:
            if option["find_way"] == "flann":
                find_fun = self.find_image_by_flann
            elif option["find_way"] == "template":
                find_fun = self.find_image_by_template
            else:
                find_fun = self.find_image_by_template
        else:
            find_fun = self.find_image_by_template
        if "region" in option:
            region = option["region"]
        else:
            if "find_image_by_template" in str(find_fun):
                region = None
            else:
                region = [0, 0, 0.99, 0.99]
        if "confidence" in option:
            confidence = option["confidence"]
        else:
            if "find_image_by_template" in str(find_fun):
                confidence = 0.99
            else:
                confidence = 0.7
        if "timeout" in option:
            timeout = time() + option["timeout"]
        else:
            timeout = time() + 3
        if "find_delay" in option:
            find_delay = option["find_delay"]
        else:
            find_delay = 0.1
        log.debug(f"find_fun: {str(find_fun)}")
        log.debug(f"region: {region}")
        log.debug(f"confidence: {confidence}")
        log.debug(f"timeout: {timeout}")
        count = 0
        while timeout > time():
            log.debug(f"第 {count} 次查找图片")
            img = find_fun(query_image_path, self.window_screenshot(
                window_object), region=region, confidence=confidence)
            if img:
                log.debug(f"查找图片成功,结果:")
                log.debug(img)
                if "find_image_by_template" in str(find_fun):
                    return [img.left, img.top, img.width, img.height]
                else:
                    return img
            sleep(find_delay)
            count += 1
        log.warning("查找图片超时")
        return None

    def find_image_by_flann(self, queryImagePath, trainImage, region=[0, 0, 0.99, 0.99], confidence=0.7):
        ''' 通过flann方法找图(特征找图)
        :param queryImagePath: 需要查找的图片路径
        :param trainImage: 需要查找的图片路径 或者 mat对象
        :param region: 需要查找的图片所在区域
        :param confidence: 相似度
        :from https://blog.csdn.net/zhuisui_woxin/article/details/84400439
        :note 本函数如果出错可以用以下代码调试查看图片
        cv2.imshow('窗口标题', Mat对象)
        cv2.waitKey(0)
        cv2.imshow('template', template)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        :return: True || False
        '''
        template = cv2.imread(queryImagePath, 0)  # queryImage
        if isinstance(trainImage, np.ndarray):
            target = cv2.cvtColor(trainImage, cv2.COLOR_BGR2GRAY)
        elif isinstance(trainImage, str):
            target = cv2.imread(trainImage, 0)  # trainImage
        # Initiate SIFT detector创建sift检测器
        sift = cv2.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(template, None)
        kp2, des2 = sift.detectAndCompute(target, None)
        # 创建设置FLANN匹配
        index_params = dict(algorithm=0, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        # store all the good matches as per Lowe's ratio test.
        good = []
        h, w = template.shape
        region[0] *= w
        region[1] *= h
        region[2] = (region[2] * w) + region[0]
        region[3] = (region[3] * h) + region[1]
        # 舍弃大于0.7的匹配
        for m, n in matches:
            if m.distance > confidence * n.distance:
                continue
            if region[0] > kp2[m.trainIdx].pt[0] or kp2[m.trainIdx].pt[0] > region[2]:
                continue
            if region[1] > kp2[m.trainIdx].pt[1] or kp2[m.trainIdx].pt[1] > region[3]:
                continue
            good.append(m)
        MIN_MATCH_COUNT = 10  # 设置最低特征点匹配数量
        if len(good) > MIN_MATCH_COUNT:
            # 获取关键点的坐标
            src_pts = np.float32(
                [kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32(
                [kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            # 计算变换矩阵和MASK
            M, mask = cv2.findHomography(
                src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()
            # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]
                             ).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)
            cv2.polylines(target, [np.int32(dst)],
                          True, 5, 2, cv2.LINE_AA)
        else:
            if len(good) != 0:
                logging.warning("Not enough matches are found - %d/%d/%d" %
                                (len(good), MIN_MATCH_COUNT, len(matches)))
            return None
        point_list = [kp2[value.trainIdx].pt for i,
                      value in enumerate(good)]
        rect = ()
        # 限制查找图的大小
        left = point_list[0][0]
        top = point_list[0][1]
        right = point_list[0][0]
        bottom = point_list[0][1]
        for key, value in enumerate(point_list):
            if value[0] < left:
                left = value[0]
            if value[1] < top:
                top = value[1]
            if value[0] > right:
                right = value[0]
            if value[1] > bottom:
                bottom = value[1]
        rect_w = right - left
        rect_h = bottom - top
        rect = (int(left), int(top), int(rect_w), int(rect_h))
        return rect

    def find_image_by_template(self, template, trainImage, **kw):
        ''' 模板找图 '''
        images = list(pyautogui.locateAll(template, trainImage, **kw))
        if not images:
            return None
        return images[0]

    def find_images_by_template(self, template, trainImage, **kw):
        ''' 模板找图多个 '''
        images = list(pyautogui.locateAll(template, trainImage, **kw))
        return images


class WindowObject:
    def __init__(self, element, window=None, app=None):
        self.element = element
        self.window = window
        self.app = app

    def all_info(self):
        self.window.dump_tree()

    def getattr(self, *args):
        ''' 获取窗口属性,传入属性的方法名
        'class_name', 'friendly_class_name', 'texts', 'control_id', 'rectangle', 'is_visible',
        'is_enabled', 'control_count', 'style', 'exstyle', 'user_data', 'context_help_id',
        'fonts', 'client_rects', 'is_unicode', 'menu_items', 'automation_id', 'selection_indices'
        '''
        attr = {}
        for arg in args:
            try:
                attr[arg] = eval("self.element."+arg+"()")
            except Exception as e:
                log.exception(e)
                log.warning("获取 {arg} 属性出错".format(arg=arg))
                continue
        return attr

    def close_window(self):
        ''' 关闭窗口 '''
        try:
            self.element.close_alt_f4()
        except Exception as e:
            log.exception(e)
            raise Exception("关闭窗口出错")

    def get_element_from_point(self, point):
        ''' 获取该坐标的元素 '''
        def sort_by_bounds(elem):
            return elem.rectangle().width() * elem.rectangle().height()
        try:
            point = list(point)
            point[0] += self.bounds().left
            point[1] += self.bounds().top
            elements = []
            dialog = self.get_dialog()
            for element in dialog.children():
                rect = element.rectangle()
                if not element.is_visible():
                    continue
                if point[0] < rect.left or point[0] > rect.right:
                    continue
                if point[1] < rect.top or point[1] > rect.bottom:
                    continue
                elements.append(element)
            if not elements:
                return self
            elements.sort(key=sort_by_bounds, reverse=False)
            print(elements[0])
            print(elements[0].handle)
            return WindowObject(elements[0], app=self.app)
        except Exception as e:
            log.exception(e)
            raise Exception("获取坐标元素出错")

    def get_dialog(self):
        ''' 获取顶层窗口 '''
        try:
            return self.element.top_level_parent()
        except Exception as e:
            log.exception(e)
            raise Exception("获取对话框窗口失败")

    def move_mouse(self, begin_x, begin_y, end_x, end_y, duration, **kw):
        ''' 鼠标移动 '''
        try:
            dialog = self.get_dialog()
            if dialog.is_minimized():
                dialog.restore()
            if self.element.is_dialog():
                raise Exception("该句柄无法滑动")
            move_arr = smlMove(begin_x, begin_y, end_x, end_y, duration)
            print(move_arr)
            i = 0
            while i < len(move_arr):
                if i == 0:
                    self.element.press_mouse(
                        coords=(move_arr[i][0], move_arr[i][1]), **kw)
                elif i == len(move_arr)-1:
                    self.element.release_mouse(
                        coords=(move_arr[i][0], move_arr[i][1]), **kw)
                else:
                    self.element.move_mouse(
                        coords=(move_arr[i][0], move_arr[i][1]), **kw)
                sleep(move_arr[i][2])
                i += 1
        except Exception as e:
            log.exception(e)
            raise Exception("鼠标移动出错")

    def click(self, **kw):
        ''' 控件点击 '''
        try:
            dialog = self.get_dialog()
            if dialog.is_minimized():
                dialog.restore()
            if "coords" in kw:
                point = list(kw["coords"])
                point[0] += self.bounds().left
                point[1] += self.bounds().top
                element = self.get_element_from_point(kw["coords"])
                point[0] -= element.bounds().left
                point[1] -= element.bounds().top
                point = tuple(point)
                kw["coords"] = point
                element = element.element
            else:
                element = self.element
            if element.is_dialog():
                raise Exception("该句柄无法点击")
            #  self.my_click(element.handle,**kw)
            element.click(**kw)
        except Exception as e:
            log.exception(e)
            raise Exception("控件点击出错")

    def click_center(self, **kw):
        ''' 真实点击 '''
        try:
            if "coords" in kw:
                rect = self.bounds()
                coords = (
                    int(rect.width() * kw["coords"][0]), int(rect.height() * kw["coords"][1]))
                kw["coords"] = coords
            self.element.click_input(**kw)
        except Exception as e:
            log.exception(e)
            raise Exception("真实点击出错")

    def drag_mouse(self, dst, src, duration):
        ''' 控件拖动 '''
        try:
            log.debug(dst)
            log.debug(src)
            log.debug(duration)
            pyautogui.moveTo(dst[0], dst[1])
            pyautogui.dragTo(src[0], src[1], duration)
        except Exception as e:
            log.exception(e)
            raise Exception("控件拖动出错")

    def set_window_size(self, **kw):
        ''' 设置窗口大小 '''
        try:
            self.element.move_window(**kw)
        except Exception as e:
            log.exception(e)
            raise Exception("设置窗口大小出错")

    def set_text(self, text, **kw):
        ''' 输入文本 '''
        try:
            self.element.type_keys(text, **kw)
        except Exception as e:
            log.exception(e)
            raise Exception("输入文本出错")

    def show(self):
        ''' 设置焦点 '''
        try:
            # if not self.element.has_focus():
            self.element.set_focus()
        except Exception as e:
            log.exception(e)
            raise Exception("显示窗口出错")

    def scroll_up(self, **kw):
        ''' 向上滚动 '''
        try:
            self.element.scroll("up", **kw)
        except Exception as e:
            log.exception(e)
            raise Exception("向上滚动出错")

    def scroll_down(self, **kw):
        ''' 向下滚动 '''
        try:
            self.element.scroll("down", **kw)
        except Exception as e:
            log.exception(e)
            raise Exception("向下滚动出错")

    def scroll_left(self, **kw):
        ''' 向左滚动 '''
        try:
            self.element.scroll("left", **kw)
        except Exception as e:
            log.exception(e)
            raise Exception("向左滚动出错")

    def scroll_right(self, **kw):
        ''' 向右滚动 '''
        try:
            self.element.scroll("right", **kw)
        except Exception as e:
            log.exception(e)
            raise Exception("向右滚动出错")

    def parent(self):
        ''' 父类控件 '''
        try:
            return self.element.parent()
        except Exception as e:
            log.exception(e)
            raise Exception("获取父类控件出错")

    def children(self):
        ''' 子类控件集合 '''
        try:
            return WindowCollection(WindowObject(self.element.children()))
        except Exception as e:
            log.exception(e)
            raise Exception("获取所有子类控件出错")

    def child_count(self):
        ''' 子类控件数量 '''
        try:
            return self.element.control_count()
        except Exception as e:
            log.exception(e)
            raise Exception("获取子类控件数量出错")

    def bounds(self):
        ''' 窗口边界 '''
        try:
            return self.element.rectangle()
        except Exception as e:
            log.exception(e)
            raise Exception("获取窗口边界出错")

    def find_element(self, find_time=5, **kw):
        ''' 查找元素 '''
        try:
            return WindowObject(self.window.child_window(**kw).wait("exists", timeout=find_time),
                                self.window, self.app)
        except Exception as e:
            log.exception(e)
            raise Exception("窗口对象查找元素出错")

    def find_elements(self, find_time=5, **kw):
        try:
            self.find_element(find_time, **kw)
            elements = []
            for i in range(99999):
                try:
                    elements.append(WindowObject(self.window.child_window(**kw,
                                                                          found_index=i).wait("exists", timeout=find_time),
                                                 self.window, self.app))
                except Exception as e:
                    break
            return WindowCollection(elements)
        except Exception as e:
            log.exception(e)
            raise Exception("窗口对象查找元素出错")


class WindowCollection:
    def __init__(self, collection):
        self.collection = collection

    def count(self):
        ''' 窗口数量 '''
        return len(self.collection)

    def get(self, i):
        ''' 获取指定窗口 '''
        try:
            return self.collection[i]
        except Exception as e:
            log.exception(e)
            raise Exception("获取 {i} 个窗口出错".format(i=i))

    def sort(self, **kw):
        ''' 窗口排序 '''
        try:
            self.collection.sort(**kw)
        except Exception as e:
            log.exception(e)
            raise "窗口排序出错"

    def empty(self):
        ''' 窗口空判断 '''
        return len(self.collection) == 0

    def noempty(self):
        ''' 窗口非空判断 '''
        return len(self.collection) != 0


class WindowSelector():

    def __init__(self, start_path=None):
        self.app = None
        self.window = None
        self.start_path = start_path

    def connect(self, i, connect_time=5, **kw):
        ''' 连接窗口对应的App '''
        try:
            timeout = time() + connect_time
            while timeout > time():
                app_list = pywinauto.findwindows.find_windows(**kw)
                if len(app_list) > i:
                    break
                sleep(0.5)
            if i != 0 and i >= len(app_list):
                if not self.start_path:
                    raise Exception("无效的启动路径")
                self.app = pywinauto.Application().start(self.start_path)
            else:
                self.app = pywinauto.Application().connect(handle=app_list[i])
        except Exception as e:
            log.exception(e)
            self.app = None
            raise Exception("连接窗口出错")

    def set_window(self, find_time=5, **kw):
        ''' 设置活跃窗口 '''
        try:
            self.window = self.app.window(**kw, found_index=0)
            if not self.window.exists(timeout=find_time):
                raise Exception("窗口不存在")
        except Exception as e:
            log.exception(e)
            self.window = None
            raise Exception("设置窗口出错")

    def find_element_in_app(self, find_time=5, **kw):
        ''' 在活跃窗口查找元素 '''
        try:
            if kw == {}:
                return WindowObject(self.window.wait("exists", timeout=find_time),
                                    self.window, self.app)
            if "found_index" not in kw:
                kw["found_index"] = 0
            return WindowObject(self.window.child_window(**kw).wait("exists", timeout=find_time),
                                self.window.child_window(**kw), self.app)
        except Exception as e:
            log.exception(e)
            raise Exception("查找元素出错")

    def find_element_in_windows(self, **attrs):
        ''' 在活跃窗口查找元素 '''
        try:
            count = 0
            for window in self.app.windows():
                print(window)
                for key in attrs.keys():
                    attr = eval("window."+key+"()")
                    if isinstance(attr, str):
                        if attrs[key] in attr:
                            count += 1
                if count == len(attrs):
                    return WindowObject(window, app=self.app)
                else:
                    count = 0
            return None
        except Exception as e:
            log.exception(e)
            raise Exception("查找元素出错")

    def find_elements_in_app(self, find_time=0.1, **kw):
        ''' 在活跃窗口查找元素 '''
        try:
            elements = []
            for i in range(0, 1000):
                try:
                    elements.append(WindowObject(self.window.child_window(**kw, found_index=i).wait("exists", timeout=find_time),
                                                 self.window.child_window(**kw), self.app))
                except:
                    break
            return WindowCollection(elements)
        except Exception as e:
            log.exception(e)
            raise Exception("查找元素出错")

    def all_info(self):
        ''' 显示App所有控件信息 '''
        try:
            window_list = []
            for window in self.app.windows():
                window_list.append(window.handle)
            for window_handle in window_list:
                print("窗口句柄为 {handle} ".format(handle=window_handle))
                self.app.window(handle=window_handle).dump_tree()
                print("-"*200)
        except Exception as e:
            log.exception(e)
            raise Exception("显示信息出错")


if __name__ == "__main__":
    print("测试代码")
    log.info("11")
    #  print(dir(log))
    #  print(log.handle)
    print(log.handlers[1].setStream())
    log.info("11")
