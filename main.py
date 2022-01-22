import gi
import accounts

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Pango, Gio


def get_image_with_size(file: str, width: int, height: int):
    """
    returns a GTK.Image() object from file with the requested size
    :param file: the path to the image without the file extension
    :param width: desired width
    :param height: desired height
    :return: GTK.Image() object
    """
    img = Gtk.Image()
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            'img/' + file + '.png', width=width, height=height, preserve_aspect_ratio=False
        )
    except:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            'img/Other.png', width=width, height=height, preserve_aspect_ratio=False
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
        # the selected tab is already running, no need to do anything
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
        super(InputDialog, self).__init__(title=title)
        # displays an input dialog with the form of a grid
        # to get input for each value from data
        # each row is represented by the label and entry for a value from data
        content = self.get_content_area()
        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        content.add(self.grid)
        self.data = data
        self.response = [None] * len(self.data)

        for i in range(len(self.data)):
            self.response[i] = Gtk.Entry(max_length=20, margin_right=20)
            self.grid.attach(Gtk.Label(label=str(self.data[i]), margin_left=20), 0, i, 1, 1)
            self.grid.attach(self.response[i], 1, i, 1, 1)

        okbtn = Gtk.Button(label='Ok')
        okbtn.connect('clicked', self.on_ok_clicked)
        cancelbtn = Gtk.Button(label='Cancel')
        self.ok = False
        cancelbtn.connect('clicked', self.on_cancel_clicked)
        self.grid.attach(create_box_with_children(okbtn, cancelbtn), 0, len(self.data), 2, 1)
        self.grid.show_all()

    def on_ok_clicked(self, btn):
        self.response = [entry.get_text() for entry in self.response]
        self.ok = True
        self.destroy()

    def on_cancel_clicked(self, btn):
        self.destroy()


class SelectDialog(Gtk.Dialog):
    def __init__(self, title, iterator):
        super(SelectDialog, self).__init__(title=title)

        scrollWin = Gtk.ScrolledWindow()
        scrollWin.set_min_content_height(600)
        scrollWin.set_min_content_width(100)
        self.get_content_area().add(scrollWin)
        vbox = Gtk.VBox()
        scrollWin.add(vbox)
        self.response = None
        self.iterator = iterator
        for i in iterator:
            if iterator is accounts.categories:
                btn = ToolButton(i.name)
                btn.connect('clicked', self.on_btn_click)
                vbox.pack_start(btn, True, True, 0)
            else:
                btn = Gtk.Button(label=f'{i.name}: {i.currency}')
                btn.connect('clicked', self.on_btn_click)
                vbox.pack_start(btn, True, True, 0)

        self.show_all()

    def on_btn_click(self, btn):
        if self.iterator is accounts.categories:
            self.response = btn.name
        else:
            self.response = btn.get_label()
        self.destroy()


class AddInputDialog(Gtk.Dialog):
    def __init__(self, title):
        super(AddInputDialog, self).__init__(title=title)
        # Input dialog designed for adding transactions

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.get_content_area().add(self.grid)

        self.response = {}

        self.grid.attach(Gtk.Label(label='Date'), 0, 0, 1, 1)
        entry = Gtk.Entry()
        self.response['Date'] = entry
        self.grid.attach(entry, 1, 0, 2, 1)

        self.grid.attach(Gtk.Label(label='Amount'), 0, 1, 1, 1)
        entry = Gtk.Entry()
        self.response['Amount'] = entry
        self.grid.attach(entry, 1, 1, 2, 1)

        self.grid.attach(Gtk.Label(label='Category'), 0, 2, 1, 1)
        self.category = Gtk.Label(label='Other')
        self.response['Category'] = self.category
        self.grid.attach(self.category, 1, 2, 1, 1)
        btn = Gtk.Button(label='Select')
        btn.connect('clicked', self.on_category_btn_clicked)
        self.grid.attach(btn, 2, 2, 1, 1)

        self.summary = 'Income'
        summaryIncome = Gtk.RadioButton(group=None, label='Income')
        summaryIncome.connect('toggled', self.on_summary_selected)
        self.grid.attach(summaryIncome, 0, 3, 1, 1)
        summaryExpense = Gtk.RadioButton(group=summaryIncome, label='Expense')
        summaryExpense.connect('toggled', self.on_summary_selected)
        self.grid.attach(summaryExpense, 1, 3, 1, 1)
        summaryTransfer = Gtk.RadioButton(group=summaryIncome, label='Transfer')
        summaryTransfer.connect('toggled', self.on_summary_selected)
        self.grid.attach(summaryTransfer, 2, 3, 1, 1)

        self.grid.attach(Gtk.Label(label='Account'), 0, 4, 1, 1)
        for i in accounts.accounts:
            self.account = Gtk.Label(label=f'{i.name}: {i.currency}')
            break
        self.response['Account'] = self.account
        self.grid.attach(self.account, 1, 4, 1, 1)
        btn = Gtk.Button(label='Select')
        btn.connect('clicked', self.on_account_btn_clicked, 0)
        self.grid.attach(btn, 2, 4, 1, 1)

        for i in accounts.accounts:
            self.account2 = Gtk.Label(label=f'{i.name}: {i.currency}')
            break
        self.response['Account2'] = self.account2

        self.okbtn = Gtk.Button(label='Ok')
        self.okbtn.connect('clicked', self.on_ok_btn_clicked)
        self.grid.attach(self.okbtn, 0, 5, 2, 1)
        self.cancelbtn = Gtk.Button(label='Cancel')
        self.cancelbtn.connect('clicked', lambda x: self.destroy())
        self.grid.attach(self.cancelbtn, 2, 5, 1, 1)

        self.ok = False

        self.show_all()

    def on_ok_btn_clicked(self, btn):
        for key in self.response.keys():
            try:
                self.response[key] = self.response[key].get_label()
            except AttributeError:
                self.response[key] = self.response[key].get_text()
        self.response['Summary'] = self.summary
        # print(self.response)
        self.ok = True
        self.destroy()

    def on_category_btn_clicked(self, btn):
        dialog = SelectDialog('Select Category', accounts.categories)
        dialog.run()
        dialog.destroy()
        response = dialog.response
        if response:
            self.category.set_label(response)

    def on_account_btn_clicked(self, btn, condition):
        # sets the value for self.account2 if condition
        # and self.account if false
        dialog = SelectDialog('Select Category', accounts.accounts)
        dialog.run()
        dialog.destroy()
        response = dialog.response
        if response:
            if condition:
                self.account2.set_label(response)
            else:
                self.account.set_label(response)

    def on_summary_selected(self, btn):
        if self.summary == 'Transfer':
            self.grid.remove_row(5)
            self.grid.attach(self.okbtn, 0, 5, 2, 1)
            self.grid.attach(self.cancelbtn, 2, 5, 1, 1)
        if btn.get_active():
            self.summary = btn.get_label()
            if self.summary == 'Transfer':
                self.grid.insert_row(5)
                self.grid.attach(Gtk.Label(label='Account2'), 0, 5, 1, 1)
                self.grid.attach(self.account2, 1, 5, 1, 1)
                btn = Gtk.Button(label='Select')
                btn.connect('clicked', self.on_account_btn_clicked, 1)
                self.grid.attach(btn, 2, 5, 1, 1)
                self.grid.show_all()


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
        data = [
            transaction.date, transaction.amount, transaction.category,
            transaction.summary, transaction.account
        ]
        if transaction.account2:
            data[-1] = f'{transaction.account} -> {transaction.account2}'
        for i in data:
            self.append(str(i))


class OverviewStore(Gtk.ListStore):
    def __init__(self, data=accounts.transactionList):
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
        self.addBtn.connect('clicked', self.on_add_btn_clicked)
        self.tools.pack_start(self.addBtn, True, True, 0)

        self.filterbtn = ToolButton('Filter')
        self.tools.pack_start(self.filterbtn, True, True, 0)

        self.deletebtn = ToolButton('Delete')
        self.tools.pack_start(self.deletebtn, True, True, 0)

        # the table itself
        self.header = Gtk.Box()
        self.attach(self.header, 0, 1, 1, 1)
        btns = ('Date', 'Amount', 'Category', 'Summary', 'Account')

        self.treeView = Gtk.TreeView()
        self.treeView.set_model(OverviewStore())
        self.treeView.set_size_request(1000, 800)
        rendererText = Gtk.CellRendererText(font='Sans Serif 11', xalign=1)
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_min_content_height(800)
        scrolledWindow.set_min_content_width(1000)
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
        accounts.transactionList.sort(btn.get_title())
        self.treeView.set_model(OverviewStore())

    def on_add_btn_clicked(self, btn):
        # dialog = InputDialog(
        #     'Add transaction', 'Date', 'Amount', 'Category', 'Account'
        # )
        dialog = AddInputDialog('Add Transaction')
        dialog.run()
        dialog.destroy()

        if not dialog.ok:
            return

        response = dialog.response
        if not accounts.validate_transaction(response):
            errordialog = InputDialog('Error')
            errordialog.run()
            errordialog.destroy()
            return
        transaction = accounts.Transaction(*accounts.create_transaction_data(response))
        if transaction.summary == 'Income':
            transaction.account.add_funds(transaction.amount)
        elif transaction.summary == 'Expense':
            transaction.account.sub_funds(transaction.amount)
        else:
            accounts.transaction_between_accounts(
                transaction.account, transaction.account2, transaction.amount
            )
        accounts.transactionList.push(transaction)
        self.treeView.set_model(OverviewStore())

    def on_filter_btn_clicked(self, btn):
        pass

    def on_delete_btn_clicked(self, btn):
        pass


class AccountBtn(Gtk.Button):
    def __init__(self, account):
        super(AccountBtn, self).__init__()
        self.set_size_request(180, 300)
        self.account = account
        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.pack_start(Gtk.Label(label=self.account.name), True, True, 0)
        vbox.pack_start(Gtk.Label(label=self.account.balance), True, True, 0)
        vbox.pack_start(Gtk.Label(label=self.account.currency), True, True, 0)
        self.show_all()


class AccountsTab(Gtk.ScrolledWindow):
    def __init__(self):
        super(AccountsTab, self).__init__()
        self.grid = Gtk.Grid()
        self.grid.set_size_request(1000, 800)
        self.set_min_content_height(800)
        self.set_min_content_width(1000)
        self.add(self.grid)
        self.grid.set_row_spacing(20)
        self.grid.set_column_spacing(20)
        self.draw_accounts()

    def draw_accounts(self):
        # clear the grid first
        try:
            for i in range(5):
                self.grid.remove_column(0)
        except:
            pass

        row, column = 0, 0
        for account in accounts.accounts:
            btn = AccountBtn(account)
            btn.connect('clicked', self.on_account_btn_clicked)
            self.grid.attach(btn, column, row, 1, 1)
            column += 1
            if column == 5:
                row += 1
                column = 0
        btn = Gtk.Button()
        btn.add(get_image_with_size('Add', 150, 150))
        btn.connect('clicked', self.on_add_btn_clicked)
        self.grid.attach(btn, column, row, 1, 1)
        self.show_all()

    def on_add_btn_clicked(self, btn):
        dialog = InputDialog('New Account', 'Name', 'Balance', 'Currency')
        dialog.run()
        dialog.destroy()
        if not dialog.ok:
            # the user did not click ok
            return
        response = dialog.response
        if self.new_account_validation(response):
            accounts.accounts.add(accounts.Account(*response))
            self.draw_accounts()
        else:
            dialog = InputDialog('Error')
            dialog.run()
            dialog.destroy()

    def new_account_validation(self, data):
        if accounts.Account(data[0], currency=data[2]) in accounts.accounts:
            return False
        try:
            int(data[1])
        except:
            return False
        if data[2] not in accounts.data['rates']:
            return False
        return True

    def on_account_btn_clicked(self, btn):
        dialog = InputDialog('New Account', 'Name', 'Balance', 'Currency')
        dialog.response[0].set_text(btn.account.name)
        dialog.response[1].set_text(str(btn.account.balance))
        dialog.response[2].set_text(btn.account.currency)
        deletebtn = Gtk.Button(label='Delete')
        deletebtn.connect('clicked', self.delete_account, dialog, btn.account)
        dialog.grid.attach(deletebtn, 0, len(dialog.data) + 1, 2, 1)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

        # checking if the account has been deleted
        if not dialog.ok:
            return

        # if reached here, we have to change the data of the account
        if (
            dialog.response[0] != btn.account.name
            and not self.new_account_validation(dialog.response)
        ):
            errordialog = InputDialog('Error')
            errordialog.run()
            errordialog.destroy()
            return

        self.delete_account(None, dialog, btn.account)
        accounts.accounts.add(accounts.Account(*dialog.response))
        self.draw_accounts()

    def delete_account(self, btn, dialog, account):
        dialog.destroy()
        accounts.accounts.remove(account)
        self.draw_accounts()


class CategoryBtn(Gtk.Button):
    def __init__(self, category):
        super(CategoryBtn, self).__init__()
        self.set_size_request(180, 300)
        self.category = category
        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.pack_start(get_image_with_size(self.category.name, 150, 150), True, True, 0)
        vbox.pack_start(Gtk.Label(label=self.category.name), True, True, 0)
        self.show_all()


class CategoriesTab(Gtk.ScrolledWindow):
    def __init__(self):
        super(CategoriesTab, self).__init__()
        self.grid = Gtk.Grid()
        self.grid.set_size_request(1000, 800)
        self.set_min_content_height(800)
        self.set_min_content_width(1000)
        self.add(self.grid)
        self.grid.set_row_spacing(20)
        self.grid.set_column_spacing(20)
        self.draw_categories()

    def draw_categories(self):
        # clear the grid first
        try:
            for i in range(5):
                self.grid.remove_column(0)
        except:
            pass

        row, column = 0, 0
        for category in accounts.categories:
            btn = CategoryBtn(category)
            btn.connect('clicked', self.on_category_btn_clicked)
            self.grid.attach(btn, column, row, 1, 1)
            column += 1
            if column == 5:
                row += 1
                column = 0
        btn = Gtk.Button()
        btn.add(get_image_with_size('Add', 150, 150))
        btn.set_size_request(180, 300)
        btn.connect('clicked', self.on_add_btn_clicked)
        self.grid.attach(btn, column, row, 1, 1)
        self.show_all()

    def on_category_btn_clicked(self, btn):
        dialog = InputDialog('Delete this category?')
        dialog.run()
        dialog.destroy()
        if dialog.ok:
            accounts.categories.remove(btn.category)
            self.draw_categories()

    def on_add_btn_clicked(self, btn):
        dialog = InputDialog('New Category', 'Name')
        dialog.run()
        dialog.destroy()

        if not dialog.ok:
            # the user didn't click ok
            return

        name = dialog.response[0]

        if name == '' or accounts.Category(name) in accounts.categories:
            # a category with this name already exists
            errordialog = InputDialog('Error')
            errordialog.run()
            errordialog.destroy()
            return

        accounts.categories.add(accounts.Category(name))
        self.draw_categories()


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
