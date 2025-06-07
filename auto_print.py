import win32print
printer_name = win32print.GetDefaultPrinter()
file_name = r"C:\Users\мвидео\python\pasport_print\result.pdf"
win32print.SetDefaultPrinter(printer_name)
hPrinter = win32print.OpenPrinter(printer_name)

try:
    hJob = win32print.StartDocPrinter(
        hPrinter, 4, (file_name, None, "RAW"))
    win32print.StartPagePrinter(hPrinter)
    # with open(file_name, 'rb') as f:
    #     buf = f.read()
    # win32print.WritePrinter(hPrinter, buf)
    # win32print.EndPagePrinter(hPrinter)
    # win32print.EndDocPrinter(hPrinter)
finally:
    win32print.ClosePrinter(hPrinter)
