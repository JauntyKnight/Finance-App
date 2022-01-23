import gi
import accounts
import os

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
            os.path.join('img', file + '.png'), width=width, height=height, preserve_aspect_ratio=False
        )
    except:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            os.path.join('img', 'Other.png'), width=width, height=height, preserve_aspect_ratio=False
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

        self.okbtn = Gtk.Button(label='Ok')
        self.okbtn.connect('clicked', self.on_ok_clicked)
        cancelbtn = Gtk.Button(label='Cancel')
        self.ok = False
        self.connect('key_release_event', self.on_key_release)
        cancelbtn.connect('clicked', self.on_cancel_clicked)
        self.grid.attach(create_box_with_children(self.okbtn, cancelbtn), 0, len(self.data), 2, 1)
        self.grid.show_all()

    def on_key_release(self, widget, event):
        if event.keyval == 65293:
            # the Enter key has been released
            self.on_ok_clicked(None)

    def on_ok_clicked(self, btn):
        self.response = [entry.get_text() for entry in self.response]
        self.ok = True
        self.destroy()

    def on_cancel_clicked(self, btn):
        self.destroy()


class AddInputDialog(InputDialog):
    def __init__(self, title, *data):
        super(AddInputDialog, self).__init__(title, *data)
        self.okbtn.set_label('Add')


class SelectDialog(Gtk.Dialog):
    def __init__(self, title, iterator):
        super(SelectDialog, self).__init__(title=title)

        scrollWin = Gtk.ScrolledWindow()
        scrollWin.set_min_content_height(600)
        scrollWin.set_min_content_width(300)
        self.get_content_area().add(scrollWin)
        vbox = Gtk.VBox()
        scrollWin.add(vbox)
        self.response = None
        self.iterator = iterator
        for i in self.iterator:
            if self.iterator is accounts.categories:
                btn = ToolButton(i.name)
            elif self.iterator is accounts.accounts:
                btn = Gtk.Button(label=f'{i.name}: {i.currency}')
            else:
                btn = Gtk.Button(label=str(i))
            btn.connect('clicked', self.on_btn_click)
            vbox.pack_start(btn, True, True, 0)

        self.show_all()

    def on_btn_click(self, btn):
        if self.iterator is accounts.categories:
            self.response = btn.name
        else:
            self.response = btn.get_label()
        self.destroy()


class AddTransactionInputDialog(Gtk.Dialog):
    def __init__(self, title):
        super(AddTransactionInputDialog, self).__init__(title=title)
        # Input dialog designed for adding transactions

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.get_content_area().add(self.grid)

        self.response = {}

        self.grid.attach(Gtk.Label(label='Date'), 0, 0, 1, 1)
        entry = Gtk.Entry()
        # setting the default entry as today's date
        entry.set_text(str(accounts.get_todays_date()))
        self.response['Date'] = entry
        self.grid.attach(entry, 1, 0, 2, 1)

        self.grid.attach(Gtk.Label(label='Amount'), 0, 1, 1, 1)
        entry = Gtk.Entry()
        self.response['Amount'] = entry
        self.grid.attach(entry, 1, 1, 2, 1)

        self.grid.attach(Gtk.Label(label='Category'), 0, 2, 1, 1)
        for i in accounts.categories:
            self.category = Gtk.Label(label=i.name)
            break
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
        summaryExpense.set_active(True)
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

        self.okbtn = Gtk.Button(label='Add')
        self.okbtn.connect('clicked', self.on_ok_btn_clicked)
        self.connect('key_release_event', self.on_key_release)
        self.grid.attach(self.okbtn, 0, 5, 2, 1)
        self.cancelbtn = Gtk.Button(label='Cancel')
        self.cancelbtn.connect('clicked', lambda x: self.destroy())
        self.grid.attach(self.cancelbtn, 2, 5, 1, 1)

        self.ok = False

        self.show_all()

    def on_key_release(self, widget, event):
        if event.keyval == 65293:
            # the Enter key has been released
            self.on_ok_btn_clicked(None)

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


class MultipleSelectDialog(Gtk.Dialog):
    def __init__(self, title, iterator, prev_answer):
        super(MultipleSelectDialog, self).__init__(title=title)
        vbox = Gtk.VBox()
        scrollWin = Gtk.ScrolledWindow()
        scrollWin.set_min_content_height(600)
        scrollWin.set_min_content_width(300)
        self.get_content_area().add(scrollWin)
        scrollWin.add(vbox)
        self.response = set()

        if iterator is accounts.categories:
            for i in iterator:
                btn = Gtk.CheckButton(label=i.name)
                btn.connect('toggled', self.on_toggle)
                if len(prev_answer) == 0 or i.name in prev_answer:
                    btn.set_active(True)
                btn.set_size_request(150, 20)
                box = Gtk.Box()
                box.pack_start(btn, True, True, 0)
                box.pack_start(get_image_with_size(i.name, 30, 30), True, True, 0)
                vbox.pack_start(box, True, True, 0)
        else:
            for i in iterator:
                btn = Gtk.CheckButton(label=i.name)
                btn.connect('toggled', self.on_toggle)
                if len(prev_answer) == 0 or i.name in prev_answer:
                    btn.set_active(True)
                box = Gtk.Box()
                box.pack_start(btn, True, True, 0)
                box.pack_start(Gtk.Label(label=i.currency), True, True, 0)
                vbox.pack_start(box, True, True, 0)

        btn = Gtk.Button(label='Select')
        btn.connect('clicked', lambda x: self.destroy())
        vbox.pack_start(btn, True, True, 0)
        self.show_all()

    def on_toggle(self, btn):
        if btn.get_active():
            self.response.add(btn.get_label())
        else:
            self.response.remove(btn.get_label())


class FilterTransactionsInputDialog(Gtk.Dialog):
    def __init__(self, title):
        super(FilterTransactionsInputDialog, self).__init__(title=title)
        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.get_content_area().add(grid)

        self.response = dict()

        grid.attach(Gtk.Label(label='Date from'), 0, 0, 1, 1)
        entry = Gtk.Entry()
        self.response['Date from'] = entry
        grid.attach(entry, 1, 0, 2, 1)

        grid.attach(Gtk.Label(label='Date to'), 0, 1, 1, 1)
        entry = Gtk.Entry()
        entry.set_text(str(accounts.get_todays_date()))
        self.response['Date to'] = entry
        grid.attach(entry, 1, 1, 2, 1)

        grid.attach(Gtk.Label(label='Amount from'), 0, 2, 1, 1)
        entry = Gtk.Entry()
        entry.set_text('0.00')
        self.response['Amount from'] = entry
        grid.attach(entry, 1, 2, 2, 1)

        grid.attach(Gtk.Label(label='Amount to'), 0, 3, 1, 1)
        entry = Gtk.Entry()
        self.response['Amount to'] = entry
        grid.attach(entry, 1, 3, 2, 1)

        self.response['Summary'] = set()
        checkbtn = Gtk.CheckButton(label='Income')
        checkbtn.connect('toggled', self.on_check_btn_toggled)
        grid.attach(checkbtn, 0, 4, 1, 1)
        checkbtn = Gtk.CheckButton(label='Expense')
        checkbtn.connect('toggled', self.on_check_btn_toggled)
        checkbtn.set_active(True)
        grid.attach(checkbtn, 1, 4, 1, 1)
        checkbtn = Gtk.CheckButton(label='Transfer')
        checkbtn.connect('toggled', self.on_check_btn_toggled)
        grid.attach(checkbtn, 2, 4, 1, 1)

        self.response['Category'] = set([i.name for i in accounts.categories])
        grid.attach(Gtk.Label(label='Category'), 0, 5, 1, 1)
        btn = Gtk.Button(label='Select category..')
        btn.connect('clicked', self.on_select_click, True)
        grid.attach(btn, 1, 5, 2, 1)

        self.response['Account'] = set([i.name for i in accounts.accounts])
        grid.attach(Gtk.Label(label='Account'), 0, 6, 1, 1)
        btn = Gtk.Button(label='Select account..')
        btn.connect('clicked', self.on_select_click, False)
        grid.attach(btn, 1, 6, 2, 1)

        btn = Gtk.Button(label='Filter')
        btn.connect('clicked', self.on_ok_btn_click)
        self.ok = False
        self.connect('key_release_event', self.on_key_release)
        grid.attach(btn, 0, 7, 2, 1)
        btn = Gtk.Button(label='Cancel')
        btn.connect('clicked', lambda x: self.destroy())
        grid.attach(btn, 2, 7, 1, 1)

        self.show_all()

    def on_check_btn_toggled(self, btn):
        if btn.get_active():
            self.response['Summary'].add(btn.get_label())
        else:
            self.response['Summary'].remove(btn.get_label())

    def on_ok_btn_click(self, btn):
        self.ok = True
        self.response['Date from'] = self.response['Date from'].get_text()
        self.response['Date to'] = self.response['Date to'].get_text()
        self.response['Amount from'] = self.response['Amount from'].get_text()
        self.response['Amount to'] = self.response['Amount to'].get_text()
        self.destroy()

    def on_key_release(self, widget, event):
        if event.keyval == 65293:
            # the Enter key has been released
            self.on_ok_btn_clicked(None)

    def on_select_click(self, btn, selection):
        # opens a selection dialog for categories if selection
        # and for accounts if false
        if selection:
            dialog = MultipleSelectDialog('Select Categories', accounts.categories, self.response['Category'])
            dialog.run()
            dialog.destroy()
            self.response['Category'] = dialog.response
        else:
            dialog = MultipleSelectDialog('Select Accounts', accounts.accounts, self.response['Account'])
            dialog.run()
            dialog.destroy()
            self.response['Account'] = dialog.response
        # print(dialog.response)

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
        self.label = Gtk.Label(label=self.name)
        box.pack_start(self.label, True, True, 0)


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
            transaction.date, f'{transaction.amount:.2f}', transaction.category,
            transaction.summary,
            f'{transaction.account}: {accounts.find_account(transaction.account).currency}'
        ]
        if transaction.account2:
            data[-1] = f'{transaction.account} -> {transaction.account2}'
        for i in data:
            self.append(str(i))


class OverviewStore(Gtk.ListStore):
    def __init__(self, data=accounts.transactionList):
        super(OverviewStore, self).__init__(
            *(5 * [str])
        )
        self.data = data
        self._draw_transactions()

    def _draw_transactions(self):
        for transaction in self.data:
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
        self.filterApplied = False
        self.filterbtn.connect('clicked', self.on_filter_btn_clicked)
        self.tools.pack_start(self.filterbtn, True, True, 0)

        self.deletebtn = ToolButton('Delete')
        self.deletebtn.connect('clicked', self.on_delete_btn_clicked)
        self.tools.pack_start(self.deletebtn, True, True, 0)

        # the table itself
        self.header = Gtk.Box()
        self.attach(self.header, 0, 1, 1, 1)
        btns = ('Date', 'Amount', 'Category', 'Summary', 'Account')

        self.treeView = Gtk.TreeView()
        self.treeView.set_model(OverviewStore())
        self.treeView.set_size_request(1000, 800)
        self.treeView.set_activate_on_single_click(True)
        self.treeView.connect('row_activated', self.on_row_activated)
        self.treeView.set_enable_search(False)
        self.treeView.connect('key_release_event', self.on_key_release)
        self.selectedRow = None
        rendererText = Gtk.CellRendererText(font='Sans Serif 11', xalign=1)
        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_min_content_height(800)
        scrolledWindow.set_min_content_width(1000)
        scrolledWindow.add(self.treeView)

        for i in range(len(btns)):
            column = Gtk.TreeViewColumn(btns[i], rendererText, text=i)
            column.set_alignment(100)
            column.set_expand(True)
            column.set_clickable(True)
            column.connect('clicked', self.on_header_btn_clicked)
            self.treeView.append_column(column)
        self.treeView.show_all()
        self.attach(scrolledWindow, 0, 2, 1, 1)

    def on_header_btn_clicked(self, btn):
        if not self.filterApplied:
            accounts.transactionList.sort(btn.get_title())
            self.treeView.set_model(OverviewStore())
        else:
            accounts.filterTransactionList.sort(btn.get_title())
            self.treeView.set_model(OverviewStore(accounts.filterTransactionList))

    def on_key_release(self, widget, key):
        if key.keyval == 65535:
            # is the Delete key
            self.on_delete_btn_clicked(None)

    def on_add_btn_clicked(self, btn):
        # dialog = InputDialog(
        #     'Add transaction', 'Date', 'Amount', 'Category', 'Account'
        # )
        if len(accounts.categories) == 0:
            errordialog = InputDialog('Please, add a category')
            errordialog.run()
            errordialog.destroy()
            return
        if len(accounts.accounts) == 0:
            errordialog = InputDialog('Please, add an account')
            errordialog.run()
            errordialog.destroy()
            return
        dialog = AddTransactionInputDialog('Add Transaction')
        dialog.run()
        dialog.destroy()

        if not dialog.ok:
            return

        response = dialog.response
        if not accounts.validate_transaction(response):
            errordialog = InputDialog('Wrong data')
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
        if self.filterApplied:
            self.treeView.set_model(OverviewStore())
            self.filterbtn.label.set_label('Filter')
            self.filterApplied = False
            return

        dialog = FilterTransactionsInputDialog('Filter transactions')
        dialog.run()
        dialog.destroy()
        if not dialog.ok:
            return
        if not accounts.validate_filter(dialog.response):
            errordialog = InputDialog('Wrong data')
            errordialog.run()
            errordialog.destroy()
            return
        self.filterApplied = True
        self.filterbtn.label.set_label('Remove filter')
        accounts.transactionList.filter(dialog.response)
        self.treeView.set_model(OverviewStore(
            accounts.filterTransactionList
        ))

    def on_row_activated(self, tree, path, column):
        self.selectedRow = int(str(path))
        # print(self.selectedRow)

    def on_delete_btn_clicked(self, btn):
        if self.selectedRow is None:
            return
        try:
            accounts.delete_transaction(self.selectedRow)
        except IndexError:
            errordialog = InputDialog('There are no transactions')
            errordialog.run()
            errordialog.destroy()
        self.treeView.set_model(OverviewStore())


class AccountBtn(Gtk.Button):
    def __init__(self, account):
        super(AccountBtn, self).__init__()
        self.set_size_request(180, 300)
        self.account = account
        vbox = Gtk.VBox()
        self.add(vbox)
        vbox.pack_start(Gtk.Label(label=self.account.name), True, True, 0)
        vbox.pack_start(Gtk.Label(label=f'{self.account.balance:.2f}'), True, True, 0)
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
        dialog = AddInputDialog('New Account', 'Name', 'Balance', 'Currency')
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
            dialog = InputDialog('Wrong data')
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
        dialog = InputDialog('Edit Account', 'Name', 'Balance', 'Currency')
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
            errordialog = InputDialog('Wrong data')
            errordialog.run()
            errordialog.destroy()
            return

        self.delete_account(None, dialog, btn.account)
        accounts.accounts.add(accounts.Account(*dialog.response))
        self.draw_accounts()

    def delete_account(self, btn, dialog, account):
        dialog.destroy()
        accounts.delete_account(account)
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
            accounts.delete_category(btn.category)
            self.draw_categories()

    def on_add_btn_clicked(self, btn):
        dialog = AddInputDialog('Add New Category', 'Name')
        dialog.run()
        dialog.destroy()

        if not dialog.ok:
            # the user didn't click ok
            return

        name = dialog.response[0]

        if name == '' or accounts.Category(name) in accounts.categories:
            # a category with this name already exists
            errordialog = InputDialog('Wrong data')
            errordialog.run()
            errordialog.destroy()
            return

        accounts.categories.add(accounts.Category(name))
        self.draw_categories()


class ExchangeTab(Tab):
    def __init__(self):
        super(ExchangeTab, self).__init__()
        scrollWin = Gtk.ScrolledWindow()
        scrollWin.set_min_content_width(500)
        scrollWin.set_min_content_height(870)
        self.attach(scrollWin, 0, 0, 1, 1)

        # the left panel: exchange rate table
        treeView = Gtk.TreeView()
        treeView.set_model(self.create_tree_model())
        treeView.set_size_request(500, 1000)
        scrollWin.add(treeView)
        rendererText = Gtk.CellRendererText(xalign=1)
        rendererImage = Gtk.CellRendererPixbuf()
        btns = ('Currency', 'Yesterday', 'Today')
        for i in range(len(btns)):
            column = Gtk.TreeViewColumn(btns[i], rendererText, text=i)
            column.set_expand(True)
            treeView.append_column(column)
        column = Gtk.TreeViewColumn('Graph', rendererImage, pixbuf=3)
        treeView.append_column(column)

        # right panel: currency calculator
        vbox = Gtk.VBox(spacing=150)
        vbox.set_size_request(500, 900)
        self.attach(vbox, 1, 0, 1, 1)
        vbox.pack_start(Gtk.Label(label='Currency Calculator'), True, True, 0)

        box = Gtk.Box()
        self.curr1btn = Gtk.Button(label='CZK')
        self.curr1btn.connect('clicked', self.on_btn_click)
        self.curr1entry = Gtk.Entry(text='0.00')
        self.curr1entry.connect('activate', self.on_entry_activate)
        box.pack_start(self.curr1btn, True, True, 0)
        box.pack_start(self.curr1entry, True, True, 0)
        vbox.pack_start(box, True, True, 0)

        box = Gtk.Box()
        self.curr2btn = Gtk.Button(label='EUR')
        self.curr2entry = Gtk.Entry(text='0.00')
        self.curr2btn.connect('clicked', self.on_btn_click)
        self.curr2entry.connect('activate', self.on_entry_activate)
        box.pack_start(self.curr2btn, True, True, 0)
        box.pack_start(self.curr2entry, True, True, 0)
        vbox.pack_start(box, True, True, 0)

        box = Gtk.Box()
        self.curr3btn = Gtk.Button(label='USD')
        self.curr3entry = Gtk.Entry(text='0.00')
        self.curr3btn.connect('clicked', self.on_btn_click)
        self.curr3entry.connect('activate', self.on_entry_activate)
        box.pack_start(self.curr3btn, True, True, 0)
        box.pack_start(self.curr3entry, True, True, 0)
        vbox.pack_start(box, True, True, 0)


        self.show_all()

    def on_entry_activate(self, entry):
        val = entry.get_text()
        try:
            val = float(val)
            if val < 0:
                return
        except ValueError:
            return

        # a very ugly way to find the entry that generated the signal
        # i could have made a list of the entries, but there are only 3 of them anyway
        if entry is self.curr1entry:
            curr = self.curr1btn.get_label()
        elif entry is self.curr2entry:
            curr = self.curr2btn.get_label()
        else:
            curr = self.curr3btn.get_label()

        if self.curr1entry is not entry:
            self.curr1entry.set_text(f'{accounts.converted(val, curr, self.curr1btn.get_label()):.2f}')
        if self.curr2entry is not entry:
            self.curr2entry.set_text(f'{accounts.converted(val, curr, self.curr2btn.get_label()):.2f}')
        if self.curr3entry is not entry:
            self.curr3entry.set_text(f'{accounts.converted(val, curr, self.curr3btn.get_label()):.2f}')

    def on_btn_click(self, btn):
        dialog = SelectDialog('Select Currency', accounts.data['rates'].keys())
        dialog.run()
        dialog.destroy()
        # unfortunately, btn is just a copy, but I need the reference
        if btn is self.curr1btn:
            self.curr1btn.set_label(dialog.response)
        elif btn is self.curr2btn:
            self.curr2btn.set_label(dialog.response)
        else:
            self.curr3btn.set_label(dialog.response)

    def create_tree_model(self):
        model = Gtk.ListStore(str, str, str, GdkPixbuf.Pixbuf)
        for currency in accounts.data['rates'].keys():
            if accounts.data['rates'][currency] > accounts.pastData['rates'][currency]:
                graph = 'graph_up'
            elif accounts.data['rates'][currency] < accounts.pastData['rates'][currency]:
                graph = 'graph_down'
            else:
                graph = 'equal'
            model.append([
                currency, f"{accounts.pastData['rates'][currency]:.4f}",
                f"{accounts.data['rates'][currency]:.4f}",
                GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    os.path.join('img', graph + '.png'), width=30, height=30, preserve_aspect_ratio=False
                )
            ])
        return model


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


accounts.read_data()

win = Window()
win.connect('destroy', Gtk.main_quit)
win.show_all()
Gtk.main()

accounts.print_data()
