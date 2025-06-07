import copy
import ctypes
from pprint import pprint
import win32ui
import win32con
import win32gui
import win32print


CreateFont = CreateFontW = ctypes.windll.gdi32.CreateFontW


def get_system_fonts():
    def callback(font, tm, fonttype, names):
        names.append(font.lfFaceName)
        return True
    fontnames = []
    hdc = None
    try:
        hdc = win32gui.GetDC(None)
        win32gui.EnumFontFamilies(hdc, None, callback, fontnames)
    finally:
        if hdc:
            win32gui.ReleaseDC(hdc, None)
            hdc = None
    fontnames.sort()
    return fontnames

class PrinterFontContext(object):

    def __init__(self, printer, font_config=None):
        self.printer = printer
        self.font_config = font_config
        if self.font_config:
            self.height = int(font_config.get("height", 0) * self.printer.lpty)
            self.width = int(font_config.get("width", 0) * self.printer.lptx)
            self.escapement = font_config.get("escapement", 0)
            self.orientation = font_config.get("orientation", 0)
            self.weight = font_config.get("weight", 0)
            self.italic = font_config.get("italic", 0)
            self.underline = font_config.get("underline", 0)
            self.strikeOut = font_config.get("strikeOut", 0)
            self.charSet = font_config.get("charSet", 0)
            self.outPrecision = font_config.get("outPrecision", 0)
            self.clipPrecision = font_config.get("clipPrecision", 0)
            self.quality = font_config.get("quality", 0)
            self.pitchAndFamily = font_config.get("pitchAndFamily", 0)
            self.faceName = font_config.get("faceName", "")

    def __enter__(self):
        if self.font_config:
            self.new_font_object = CreateFontW(
                self.height,
                self.width,
                self.escapement,
                self.orientation,
                self.weight,
                self.italic,
                self.underline,
                self.strikeOut,
                self.charSet,
                self.outPrecision,
                self.clipPrecision,
                self.quality,
                self.pitchAndFamily,
                self.faceName)
            self.old_font_object = win32gui.SelectObject(self.printer.printer_dc, self.new_font_object)

    def __exit__(self, *args, **kwargs):
        if self.font_config:
            win32gui.SelectObject(self.printer.printer_dc, self.old_font_object)
            win32gui.DeleteObject(self.new_font_object)


class Position(object):

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def pos(self):
        return (self.x, self.y)

    def set(self, x, y):
        self.x = x
        self.y = y

    def forward(self, x=0, y=0):
        self.x += x
        self.y += y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

class PrinterBase(object):

    def __init__(self, printer_name=None, doc_name=None, margin=None, linegap=0, default_font=None, auto_page=False):
        margin = margin and copy.deepcopy(margin) or (0, 0, 0, 0)
        self.printer_name = printer_name or self.get_default_printer_name()
        self.doc_name = doc_name or self.get_default_doc_name()
        self.default_font = default_font and copy.deepcopy(default_font) or {}
        self.printer = win32ui.CreateDC()  
        self.printer.CreatePrinterDC(self.printer_name) 
        self.printer_dc = self.printer.GetSafeHdc()
        self.printer.SetMapMode(win32con.MM_TWIPS)
        self.lppx = 1440 / self.printer.GetDeviceCaps(win32con.LOGPIXELSX) # LogicUnit Per PhysicalUnit on X-axis
        self.lppy = 1440 / self.printer.GetDeviceCaps(win32con.LOGPIXELSY) # LogicUnit Per PhysicalUnit on Y-axis
        self.lptx = 1440 / 72 # 1 Pt. to LogicUnit on X-axis
        self.lpty = 1440 / 72 # 1 Pt. to LoginUnit on Y-axis
        self.width = self.lppx * self.printer.GetDeviceCaps(win32con.HORZRES)
        self.height = self.lppy * self.printer.GetDeviceCaps(win32con.VERTRES)
        self.cursor = Position()
        self.linegap = linegap * self.lpty
        self.margin = (margin[0]*self.lptx, margin[1]*self.lpty, margin[2]*self.lptx, margin[3]*self.lpty)
        self.auto_page = auto_page

    @classmethod
    def get_default_printer_name(cls):
        return win32print.GetDefaultPrinterW()

    @classmethod
    def get_default_doc_name(cls):
        return "NoNameFile"

    def start(self):
        self.start_doc()
        self.start_page()
    
    def start_doc(self):
        self.printer.StartDoc(self.doc_name)

    def start_page(self):
        self.printer.StartPage()
        self.cursor.set(self.margin[0], self.margin[1])

    def end(self):
        self.end_page()
        self.end_doc()

    def end_doc(self):
        self.printer.EndDoc()

    def end_page(self):
        self.printer.EndPage()

    def new_page(self):
        self.end_page()
        self.start_page()

    def get_print_box(self):
        return tuple(map(int, (
            self.cursor.x,
            -1 * self.cursor.y,
            self.width - self.margin[2],
            -1 * (self.height - self.margin[3]),
        )))

    def setup_printer_font(self, font_config=None):
        config = {}
        config.update(self.default_font or {})
        config.update(font_config or {})
        return PrinterFontContext(self, config)

    def text(self, text, align="left", font_config=None):
        with self.setup_printer_font(font_config):
            print_box = self.get_print_box()
            print_flag = self.get_print_flag(align)
            if self.auto_page:
                # calc the target rect
                calc_flag = print_flag | win32con.DT_CALCRECT
                height, _ = win32gui.DrawTextW(self.printer_dc, text, -1, print_box, calc_flag)
                # try to do auto page
                if self.cursor.y + height + self.margin[3] > self.height:
                    self.new_page()
                    print_box = self.get_print_box()
            # do real print
            height, _ = win32gui.DrawTextW(self.printer_dc, text, -1, print_box, print_flag)
            self.cursor.forward(0, int(abs(height) + self.linegap))

    @classmethod
    def get_print_flag(cls, align="left"):
        print_flag = win32con.DT_TOP|win32con.DT_WORDBREAK|win32con.DT_NOCLIP
        if align == "left":
            print_flag |= win32con.DT_LEFT
        elif align == "center":
            print_flag |= win32con.DT_CENTER
        elif align == "right":
            print_flag |= win32con.DT_RIGHT
        return print_flag

class PrinterContext(object):

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args, **kwargs):
        self.end()


class Printer(PrinterContext, PrinterBase):
    pass
