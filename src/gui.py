import wx
import utils


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, _rws_base):
        super(TaskBarIcon, self).__init__()
        self.rws_base = _rws_base
        self.TRAY_TOOLTIP = "Reddit Wallpaper Switcher"
        self.TRAY_ICON = self.rws_base.ASSETS_PATH+"/icon.ico"
        self.set_icon(self.TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.clicked)

    def create_popup_menu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Change Wallpaper', self.change_wallpaper)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, self.TRAY_TOOLTIP)

    def clicked(self, event):
        self.rws_base.change_wallpaper()

    def change_wallpaper(self, event):
        self.rws_base.change_wallpaper()

    def exit(self, event):
        self.rws_base.quit_app = True
        wx.CallAfter(self.Destroy)


def main(rws_base):
    #TODO: This isn't working on Linux; it ends immediately
    app = wx.App()
    task_bar = TaskBarIcon(rws_base)
    utils.log("GUI Started", utils.MsgTypes.INFO)
    app.MainLoop()
    utils.log("GUI Ended", utils.MsgTypes.INFO)
