from log import log
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class TableWidget():
    def __init__(self, table):
        # 初始化表格控件
        self.table = table
        # 显示网格
        self.table.setShowGrid(True)
        # 设置表头是否自动排序
        self.table.setSortingEnabled(False)
        #  # 自动分配列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #  # 内容自适应
        self.table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        #  # 调整列宽
        #  self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        #  self.table.setColumnWidth(0, 25)
        #  # 选中表头不高亮
        self.table.horizontalHeader().setHighlightSections(False)
        #  # 取消隔行变色
        self.table.setAlternatingRowColors(False)
        #  # 隐藏垂直表头
        self.table.horizontalHeader().setVisible(True)
        self.table.verticalHeader().setVisible(False)
        #  # 不可编辑
        #  self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #  # 选中一行
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        #  # 多选模式
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        #  # 设置选中颜色
        self.table.setStyleSheet("selection-background-color:#047cd4;")
        self.model = QStandardItemModel()  # 存储任意结构数据
        self.table.setModel(self.model)

    def get_table_data(self) -> list:
        data = [{}]
        return data

    def init_table(self):
        """ 初始化表格 """
        # 清除表格内容
        self.model.setRowCount(0)
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['名称', '范围', '描述', "状态"])
        table_data = self.get_table_data()
        for row, data in enumerate(table_data):
            self.model.setRowCount(self.model.rowCount() + 1)
            for column, value in enumerate(data):
                newItem = QStandardItem(str(value))
                # 水平居中 | 垂直居中
                newItem.setTextAlignment(Qt.AlignCenter)
                self.model.setItem(row, column, newItem)

    def refresh_table_data(self, table_data=[]):
        """ 刷新表格数据 """
        if not table_data:
            return True
        for row, data in enumerate(table_data):
            for column, value in enumerate(data):
                newItem = QStandardItem(str(value))
                # 水平居中 | 垂直居中
                newItem.setTextAlignment(Qt.AlignCenter)
                self.model.setItem(row, column, newItem)

    def set_item_status(self, index, table_data={}):
        """ 设置表格数据 """
        for column, data in table_data.items():
            column = int(column)
            row = self.get_row_by_index(index)
            if not isinstance(row, int):
                log.warning(f"更新数据失败啦,木有找到对应的编号:{index}")
                break
            self.model.setItem(row, column, QStandardItem(data))
        self.table.viewport().update()

    def get_row_by_index(self, index):
        """ 获取指定表格项 """
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if not item:
                continue
            if index == item.text():
                return row
        return None

    def get_selected_list(self):
        ''' 获取已选择的列表 '''
        selected_list = self.table.selectedIndexes()
        selected_list = set([item.row() for item in selected_list])
        index_list = []
        for row in selected_list:
            index_list.append(row)
        return index_list

    def select_all(self):
        ''' 选择全部 '''
        self.table.selectAll()

    def select_cancel(self):
        ''' 取消选择 '''
        selected_list = self.table.selectedIndexes()
        selected_list = set([item.row() for item in selected_list])
        for index in selected_list:
            self.table.selectRow(index)

    def select_invert(self):
        ''' 反向选择 '''
        for index in range(self.model.rowCount()):
            self.table.selectRow(index)
