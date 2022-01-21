import gi
import accounts

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Pango


def get_image_with_size(file, width, height):
    """
    returns a GTK.Image() object from file with the requested size
    :param file: the path to the image
    :param width: desired width
    :param height: desired height
    :return: GTK.Image() object
    """
    img = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        'img/' + file + '.png', width=width, height=height, preserve_aspect_ratio=False
    )
    img.set_from_pixbuf(pixbuf)
    return img


def create_box_with_children(*children):
    box = Gtk.Box()
    for child in children:
        box.pack_start(child, True, True, 0)
    return box


def on_menu_btn_clicked(btn):
    # the tab change function
    global win
    if btn.name == win.activeTabName:
        # the selected tab is already running, no need to do anythin
        return

    win.box.remove(win.activeTab)
    if btn.name == 'Overview':
        win.activeTab = OverviewTab()
    elif btn.name == 'Accounts':
        win.activeTab = AccountsTab()
    elif btn.name == 'Categories':
        win.activeTab = CategoriesTab()
    else:
        win.activeTab = ExchangeTab()

    win.box.pack_start(win.activeTab, True, True, 0)
    win.activeTabName = btn.name
    win.show_all()


class InputDialog(Gtk.Dialog):
    def __init__(self, title, *data):
        super(InputDialog, self).__init__(title = title)
        # displays an input dialog with the form of a grid
        # to get input for each value from data
        # each row is represented by the label and entry for a value from data
        content = self.get_content_area()
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        content.add(grid)
        self.data = data
        self.response = [None] * len(self.data)

        for i in range(len(self.data)):
            self.response[i] = Gtk.Entry(max_length=20, margin_right=20)
            grid.attach(Gtk.Label(label=str(self.data[i]), margin_left=20), 0, i, 1, 1)
            grid.attach(self.response[i], 1, i, 1, 1)

        okbtn = Gtk.Button(label='Ok')
        okbtn.connect('clicked', self.on_ok_clicked)
        cancelbtn = Gtk.Button(label='Cancel')
        cancelbtn.connect('clicked', lambda btn: self.destroy())
        grid.attach(create_box_with_children(okbtn, cancelbtn), 0, len(self.data), 2, 1)
        grid.show_all()

    def on_ok_clicked(self, btn):
        self.response = [entry.get_text() for entry in self.response]
        self.destroy()


class MenuItem(Gtk.Button):
    def __init__(self, name):
        super(MenuItem, self).__init__()
        self.name = name
        self.id = id
        vbox = Gtk.VBox(spacing=5)
        self.add(vbox)

        img = get_image_with_size(self.name, 50, 50)
        label = Gtk.Label(label=self.name)
        vbox.pack_start(img, True, True, 0)
        vbox.pack_start(label, True, True, 0)

        self.connect('clicked', on_menu_btn_clicked)


class Menu(Gtk.VBox):
    def __init__(self):
        super(Menu, self).__init__()
        self.items = []
        self.set_hexpand(False)
        btns = ('Overview', 'Accounts', 'Categories', 'Exchange')
        for btn in btns:
            self.pack_start(MenuItem(btn), True, True, 0)


class ToolButton(Gtk.Button):
    def __init__(self, name):
        super(ToolButton, self).__init__()
        self.set_size_request(100, 50)
        box = Gtk.Box(spacing=5)
        self.add(box)
        self.name = name

        box.pack_start(get_image_with_size(self.name, 20, 20), True, True, 0)
        box.pack_start(Gtk.Label(label=self.name), True, True, 0)


class HeaderButton(Gtk.Button):
    def __init__(self, name):
        # the headers of the transactions/overview table
        super(HeaderButton, self).__init__()
        self.set_size_request(200, 50)
        self.name = name
        self.add(Gtk.Label(label=name))


class Tab(Gtk.Grid):
    def __init__(self):
        super().__init__()
        """
        template/superclass for the tabs present in the application
        the menu for accessing them is on the left side

        the class is designed only for inheritance
        """
        self.set_row_spacing(10)
        self.set_size_request(1000, 800)


class Transaction(list):
    def __init__(self, transaction):
        super(Transaction, self).__init__()
        data = (
            transaction.date, transaction.amount, transaction.category,
            transaction.summary, transaction.account
        )
        for i in data:
            self.append(str(i))


class OverviewStore(Gtk.ListStore):
    def __init__(self):
        super(OverviewStore, self).__init__(
            *[str for _ in range(5)]
        )

        self._draw_transactions()

    def _draw_transactions(self):
        for transaction in accounts.transactionList:
            self.append(Transaction(transaction))


class OverviewTab(Tab):
    def __init__(self):
        super(OverviewTab, self).__init__()
        # the tools menu
        self.tools = Gtk.Box()
        self.add(self.tools)
        self.addBtn = ToolButton('Add')
        self.addBtn.connect('clicked', self.on_tool_btn_clicked)
        self.tools.pack_start(self.addBtn, True, True, 0)

        self.tools.pack_start(ToolButton('Filter'), True, True, 0)

        # the table itself
        self.header = Gtk.Box()
        self.attach(self.header, 0, 1, 1, 1)
        btns = ('Date', 'Amount', 'Category', 'Summary', 'Account')

        self.treeView = Gtk.TreeView()
        self.treeView.set_model(OverviewStore())
        self.treeView.set_size_request(1000, 800)
        rendererText = Gtk.CellRendererText(font='Sans Serif 11', xalign=1)
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_min_content_height(900)
        scrolledWindow.set_min_content_width(800)
        scrolledWindow.add(self.treeView)

        for i in range(len(btns)):
            column = Gtk.TreeViewColumn(btns[i], rendererText, text=i)
            column.set_indicator = True
            column.set_fixed_width = 200
            column.set_alignment(100)
            column.set_expand(True)
            column.set_clickable(True)
            column.connect('clicked', self.on_header_btn_clicked)
            self.treeView.append_column(column)
        self.treeView.show_all()
        self.attach(scrolledWindow, 0, 2, 1, 1)

    def on_header_btn_clicked(self, btn):
        print(btn.get_title())
        accounts.transactionList.sort(btn.get_title())
        self.treeView.set_model(OverviewStore())

    def on_tool_btn_clicked(self, btn):
        if btn.name == 'Add':
            # the add button has been pressed
            dialog = InputDialog('Add transaction',
                'Date', 'Amount', 'Category', 'Account'
            )
        d = dialog.run()
        dialog.destroy()
        response = dialog.response


class AccountsTab(Tab):
    def __init__(self):
        super(AccountsTab, self).__init__()



class CategoriesTab(Tab):
    def __init__(self):
        super(CategoriesTab, self).__init__()


class ExchangeTab(Tab):
    def __init__(self):
        super(ExchangeTab, self).__init__()


class Window(Gtk.Window):
    def __init__(self):
        super().__init__(title='Finance App')
        self.box = Gtk.Box(spacing=5)
        """
        self.box holds all the widgets present on the window
        it has only 2 direct children: 
         - a vbox, the menu on the left
         - a grid on the right, the current displayed tab
        """
        self.add(self.box)
        self.menu = Menu()
        self.box.pack_start(Menu(), True, True, 0)
        self.activeTab = OverviewTab()
        self.activeTabName = 'Overview'
        self.box.pack_start(self.activeTab, True, True, 0)
        self.set_hexpand(False)






win = Window()
win.connect('destroy', Gtk.main_quit)
win.show_all()
Gtk.main()
