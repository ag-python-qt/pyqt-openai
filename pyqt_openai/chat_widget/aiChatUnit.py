import re

import pyperclip

from qtpy.QtCore import Qt
from qtpy.QtGui import QPalette, QColor
from qtpy.QtWidgets import QLabel, QWidget, QVBoxLayout, QApplication, QHBoxLayout, QSpacerItem, QSizePolicy, \
    QTextBrowser, QAbstractScrollArea, QPushButton
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from pyqt_openai.chat_widget.convUnitResultDialog import ConvUnitResultDialog
from pyqt_openai.svgButton import SvgButton

from circleProfileImage import RoundedImage


class SourceBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        menuWidget = QWidget()
        lay = QHBoxLayout()

        self.__langLbl = QLabel()
        fnt = self.__langLbl.font()
        fnt.setBold(True)
        self.__langLbl.setFont(fnt)

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        copyBtn = SvgButton()
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self.__langLbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(copyBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setStyleSheet('QWidget { background-color: #BBB }')

        self.__browser = QTextBrowser()
        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__browser)
        lay.setContentsMargins(5, 3, 5, 3)
        lay.setSpacing(0)
        self.setLayout(lay)

    def setText(self, lexer, text):
        self.__langLbl.setText(lexer.name)
        self.__browser.setText(text)
        self.__browser.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

    def getText(self):
        return self.__browser.toPlainText()

    def getLangName(self):
        return self.__langLbl.text().lower()

    def __copy(self):
        pyperclip.copy(self.__browser.toPlainText())


class AIChatUnit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__lbl = ''
        self.__plain_text = ''
        self.__find_f = False
        self.__result_info = ''

    def __initUi(self):
        # common
        menuWidget = QWidget()
        lay = QHBoxLayout()

        self.__icon = RoundedImage()
        self.__icon.setMaximumSize(24, 24)

        self.__infoBtn = SvgButton()
        self.__infoBtn.setIcon('ico/info.svg')
        self.__infoBtn.clicked.connect(self.__showInfo)

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        self.__copyBtn = SvgButton()
        self.__copyBtn.setIcon('ico/copy.svg')
        self.__copyBtn.clicked.connect(self.__copy)

        lay.addWidget(self.__icon)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__infoBtn)
        lay.addWidget(self.__copyBtn)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setStyleSheet('QWidget { background-color: #BBB }')

        lay = QVBoxLayout()
        self.__mainWidget = QWidget()
        self.__mainWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__mainWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.setLayout(lay)

        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(220, 220, 220))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def __copy(self):
        pyperclip.copy(self.text())

    def __showInfo(self):
        dialog = ConvUnitResultDialog(self.__result_info)
        dialog.exec()

    def text(self):
        text = ''
        lay = self.__mainWidget.layout()
        for i in range(lay.count()):
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    text += widget.text()
                elif isinstance(widget, SourceBrowser):
                    text += f'```{widget.getLangName()}\n{widget.getText()}```'

        return text

    def alignment(self):
        return Qt.AlignLeft

    def setAlignment(self, a0):
        lay = self.__mainWidget.layout()
        for i in range(lay.count()):
            if lay.itemAt(i) and lay.itemAt(i).widget():
                widget = lay.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    widget.setAlignment(a0)

    def disableGUIDuringGenerateResponse(self):
        self.__copyBtn.setEnabled(False)
        self.__infoBtn.setEnabled(False)

    def showConvResultInfo(self, info_dict):
        self.__copyBtn.setEnabled(True)
        self.__infoBtn.setEnabled(True)
        self.__result_info = info_dict

    def setText(self, text: str):
        self.__lbl = QLabel(text)

        self.__lbl.setAlignment(Qt.AlignLeft)
        self.__lbl.setWordWrap(True)
        self.__lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.__lbl.setOpenExternalLinks(True)

        self.__mainWidget.layout().addWidget(self.__lbl)

        # old code
        # chunks = text.split('```')
        # for i in range(len(chunks)):
        #     if i % 2 == 0:
        #         lbl = QLabel(chunks[i])
        #
        #         lbl.setAlignment(Qt.AlignLeft)
        #         lbl.setWordWrap(True)
        #         lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #         lbl.setOpenExternalLinks(True)
        #
        #         self.__mainWidget.layout().addWidget(lbl)
        #     else:
        #         browser = SourceBrowser()
        #
        #         lang_name = ''
        #         lang_text = ''
        #
        #         m = re.search('([\S]+)\n*(.+)', chunks[i], re.DOTALL)
        #         if m:
        #             lang_name = m.group(1)
        #             lang_text = m.group(2)
        #         try:
        #             lexer = get_lexer_by_name(lang_name)
        #         except Exception as e:
        #             lexer = get_lexer_by_name('Text')
        #
        #         # get the guessed language based on given code
        #         formatter = HtmlFormatter(style='colorful')
        #
        #         css_styles = formatter.get_style_defs('.highlight')
        #
        #         html_code = f"""
        #         <html>
        #             <head>
        #                 <style>
        #                     {css_styles}
        #                 </style>
        #             </head>
        #             <body>
        #                 {highlight(lang_text, lexer, formatter)}
        #             </body>
        #         </html>
        #         """
        #         browser.setText(lexer, html_code)
        #         self.__mainWidget.layout().addWidget(browser)

    def toPlainText(self):
        return self.__plain_text

    def addText(self, text: str):
        unit = self.__mainWidget.layout().itemAt(self.__mainWidget.layout().count()-1).widget()
        if isinstance(unit, QLabel):
            unit.setText(unit.text()+text)
        elif isinstance(unit, QTextBrowser):
            unit.append(text)

    def getIcon(self):
        return self.__icon.getImage()

    def setIcon(self, filename):
        self.__icon.setImage(filename)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = AIChatUnit()
    w.setText(
        '''
        of course, i can help you!
        ```python
        class ChatUnit(QWidget):
    def __init__(self, user_f=False, parent=None):
        super().__init__(parent)
        self.__initUi(user_f)

    def __initUi(self, user_f):
        # common
        menuWidget = QWidget()
        lay = QHBoxLayout()

        # SvgButton is supposed to be used like "copyBtn = SvgButton(self)" but it makes GUI broken so i won't give "self" argument to SvgButton
        copyBtn = SvgButton()
        copyBtn.setIcon('ico/copy.svg')
        copyBtn.clicked.connect(self.__copy)

        lay.addWidget(copyBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        # if chat unit generated by user
        if user_f:
            pass
        # generated by AI
        else:
            pass

        menuWidget.setLayout(lay)
        menuWidget.setMaximumHeight(menuWidget.sizeHint().height())
        menuWidget.setStyleSheet('QWidget { background-color: #BBB }')

        self.__lbl = QLabel()
        self.__lbl.setStyleSheet('QLabel { padding: 1rem }')

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__lbl)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def __copy(self):
        pyperclip.copy(self.__lbl.text())

    def getLabel(self) -> QLabel:
        return self.__lbl

    def text(self):
        return self.__lbl.text()

    def alignment(self):
        return self.__lbl.alignment()

    def setAlignment(self, a0):
        self.__lbl.setAlignment(a0)

    def setText(self, text: str):
        return self.__lbl.setText(text) 
        ```
        thanks, bye
        '''

    )
    w.show()
    sys.exit(app.exec())