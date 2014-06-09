import wx


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, _RwsBase):
        super(TaskBarIcon, self).__init__()
        self.RwsBase = _RwsBase
        self.TRAY_TOOLTIP = "Reddit Wallpaper Switcher"
        self.TRAY_ICON = self.RwsBase.ASSETS_PATH+"/icon.ico"
        self.set_icon(self.TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.clicked)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Change Wallpaper', self.change_wallpaper)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, self.TRAY_TOOLTIP)

    def clicked(self, event):
        self.RwsBase.change_wallpaper()

    def change_wallpaper(self, event):
        self.RwsBase.change_wallpaper()

    def exit(self, event):
        self.RwsBase.quit_app = True
        wx.CallAfter(self.Destroy)

def main(RwsBase):
    app = wx.App()
    task_bar = TaskBarIcon(RwsBase)
    app.MainLoop()
