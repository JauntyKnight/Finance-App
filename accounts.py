import requests
import datetime
import json
import os


def date_str_to_int(strdate: str):
    """
    :param strdate: DD/MM/YYYY representation of a date
    """
    return [int(i) for i in strdate.split('/')][::-1]


def get_todays_date():
    s = str(datetime.datetime.today()).split()[0].split('-')
    return Date(*(int(i) for i in s))


class Date(datetime.date):
    def __init__(self, year, month, day):
        super(Date, self).__init__()

    def __str__(self):
        return f'{self.day:02d}/{self.month:02d}/{self.year}'

    def url_str(self):
        return f'{self.year}-{self.month:02d}-{self.day:02d}'


class Account:
    def __init__(self, name, balance=0, currency='EUR'):
        self.name = name
        self.balance = float(balance)
        self.currency = currency

    def __str__(self):
        # return f'{self.name}: {self.currency}'
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def add_funds(self, amount=0):
        for i in accounts:
            if i == self:
                i.balance += amount
                return

    def sub_funds(self, amount=0):
        self.add_funds(-amount)

    def to_dict(self):
        return {
            'Name': self.name,
            'Balance': self.balance,
            'Currency': self.currency
        }


class Category:
    def __init__(self, name=None):
        self.name = name

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def to_dict(self):
        return {
            'Name': self.name
        }


categories = set()
accounts = set()

# importing data from this website with EUR being the base currency
url = 'http://api.exchangeratesapi.io/v1/'

# Making the request
access_key = 'access_key=e855c4d178d5a941a369c3e0d2a76c4d'
data = requests.get(url + 'latest' + '?' + access_key).json()
yesterday = datetime.datetime.now() - datetime.timedelta(1)
yesterday = Date(yesterday.year, yesterday.month, yesterday.day)
pastData = requests.get(
        url + yesterday.url_str() + '?' + access_key
).json()


def validate_filter(data):
    if data['Date from'] != '':
        try:
            Date(*date_str_to_int(data['Date from']))
        except TypeError:
            return False
    if data['Date to'] != '':
        try:
            Date(*date_str_to_int(data['Date to']))
        except TypeError:
            return False
    if data['Amount from'] != '':
        try:
            a = float(data['Amount from'])
            if a < 0:
                return False
        except ValueError:
            return False
    if data['Amount to'] != '':
        try:
            a = float(data['Amount to'])
            if a < 0:
                return False
        except ValueError:
            return False
    return True

def validate_transaction(data):
    # checking the date
    try:
        Date(*date_str_to_int(data['Date']))
    except TypeError:
        return False
    # checking the amount
    try:
        a = float(data['Amount'])
        if a <= 0:
            return False
    except ValueError:
        return False

    if data['Summary'] == 'Transfer' and data['Account'] == data['Account2']:
        return False

    # no need to check smth else, since the other options are choosen
    # from a set of options
    return True


def create_transaction_data(data):
    r = []
    r.append(Date(*date_str_to_int(data['Date'])))
    r.append(float(data['Amount']))
    r.append(data['Summary'])
    r.append(Category(data['Category']))
    accname, accur = data['Account'].split(': ')
    r.append(Account(accname))
    if data['Summary'] == 'Transfer':
        accname, accur = data['Account2'].split(': ')
        r.append(Account(accname))
    return r


class Transaction:
    def __init__(self, date, amount, summary, category, account, account2=None):
        self.date = date
        self.amount = amount
        self.summary = summary
        self.category = category
        self.account = account
        self.account2 = account2

    def __eq__(self, other):
        return (
                self.date == other.date and self.amount == other.amount
                and self.summary == other.summary and self.account == other.account
                and self.category == other.category
        )

    def to_dict(self):
        return {
            'Date': str(self.date),
            'Amount': self.amount,
            'Summary': self.summary,
            'Category': str(self.category),
            'Account': str(self.account),
            'Account2': str(self.account2)
        }

class TransactionsList:
    def __init__(self, parent=None):
        if not parent:
            self.list = []  # must always be sorted by the date of transaction
        else:
            self.list = parent
        self.keys = ('Date', 'Amount', 'Category', 'Summary', 'Account')
        self.sortedBy = ''

    def sort(self, key):
        """
        sorts the list of transactions by the key
        :param key: key
        :return: None
        """
        if self.sortedBy == key:
            # demanded a new sorting by the same key
            # in which case the list should be sorted in reverse order
            self.list.reverse()
            return

        self.sortedBy = key

        if key == 'Date':
            self.list.sort(key=lambda x: x.date)
        elif key == 'Amount':
            self.list.sort(key=lambda x: x.amount)
        elif key == 'Summary':
            self.list.sort(key=lambda x: x.summary)
        elif key == 'Category':
            self.list.sort(key=lambda x: x.category if x.category else '')
        else:
            self.list.sort(key=lambda x: x.account)

    def _check_filter(self, filters, transaction):
        """
        Returns true if the transaction satisfies the criteria
        filters is a dictionary with the following keys:
        Date from: Date
        Date to: Date
        Amount from: Int
        Amount to: Int
        Category: list of categories
        Account: list of accounts
        """
        if (
                filters['Date from'] != ''
                and Date(*date_str_to_int(filters['Date from'])) > transaction.date
        ):
            return False
        if (
                filters['Date to'] != ''
                and Date(*date_str_to_int(filters['Date to'])) < transaction.date
        ):
            return False
        if (
                filters['Amount from'] != ''
                and float(filters['Amount from']) > transaction.amount
        ):
            return False
        if (
                filters['Amount to'] != ''
                and float(filters['Amount to']) < transaction.amount
        ):
            return False
        if transaction.summary not in filters['Summary']:
            return False
        if transaction.category.name not in filters['Category']:
            return False
        if (
            transaction.account.name not in filters['Account']
            and (
                transaction.account2 is None
                or transaction.account2.name not in filters['Account']
            )
        ):
            return False
        return True


    def filter(self, filters):
        global filterTransactionList
        # print(filters)
        r = []
        for i in self.list:
            if self._check_filter(filters, i):
                r.append(i)
        filterTransactionList = TransactionsList(r)

    def push(self, transaction):
        """
        pushes a transaction onto the stack
        :param transaction: the transaction to be added
        :return: None
        """
        self.list.append(transaction)

    def __iter__(self):
        return (i for i in self.list)


def converted(amount: int, curr1: str, curr2: str, date=None):
    """
    converts an amount of currency1 to currency2
    :param amount: amount of curr1
    :param curr1: currency to be converted from
    :param curr2: currency to be converted to
    :param date: optional: the historical date for the transaction; latest by default
    :return: amount of currency1 in currency2
    """
    if amount == 0:
        return 0
    if not date:
        return amount * data['rates'][curr2] / data['rates'][curr1]

    pastData = requests.get(
        url + date + '?' + access_key + '&symbols=' + curr1 + ',' + curr2
    ).json()
    return amount * pastData['rates'][curr2] / pastData['rates'][curr1]


def transaction_between_accounts(acc1: Account, acc2: Account, amount: int, date=None):
    # subtracts amount from acc1.balance and adds it to acc2.balance
    acc1.sub_funds(amount)
    acc2.add_funds(converted(amount, acc1.currency, acc2.currency, date))


transactionList = TransactionsList()
filterTransactionList = TransactionsList()

def delete_transaction(id):
    transaction = transactionList.list[id]
    if transaction.summary == 'Income':
        transaction.account.sub_funds(transaction.amount)
    elif transaction.summary == 'Expense':
        transaction.account.add_funds(transaction.amount)
    else:
        transaction_between_accounts(
            transaction.account2, transaction.account, converted(
                transaction.amount, transaction.account.currency, transaction.account2.currency
            )
        )
    del transactionList.list[id]


def delete_category(category):
    # this function deletes a category together with all the transactions attached to it
    # but it does not refund the accounts because i imagine the user wouldnt want it

    # deleting the transactions
    i = 0
    while i < len(transactionList.list):
        if transactionList.list[i].category == category:
            del transactionList.list[i]
        else:
            i += 1

    categories.remove(category)


def delete_account(account):
    # <almost-copy-pasted-part>this function deletes a category
    # together with all the transactions attached to it but it does not
    # refund the accounts because i imagine the user wouldnt want it</almost-copy-pasted-part>

    # deleting the transactions
    i = 0
    while i < len(transactionList.list):
        if transactionList.list[i].account == account:
            del transactionList.list[i]
        else:
            i += 1

    accounts.remove(account)


def find_account(account):
    for i in accounts:
        if account == i:
            return i


def read_data():
    # reads the transactions, accounts and categories from separate .json files
    with open(os.path.join('data', 'accounts.json'), 'r') as f:
        while True:
            s = f.readline()
            if s == '':
                break
            s = json.loads(s)
            accounts.add(Account(
                s['Name'],
                float(s['Balance']),
                s['Currency']
            ))

    with open(os.path.join('data', 'categories.json'), 'r') as f:
        while True:
            s = f.readline()
            if s == '':
                break
            s = json.loads(s)
            categories.add(Category(
                s['Name']
            ))

    with open(os.path.join('data', 'transactions.json'), 'r') as f:
        while True:
            s = f.readline()
            if s == '':
                break
            s = json.loads(s)
            transactionList.push(Transaction(
                Date(*date_str_to_int(s['Date'])),
                float(s['Amount']),
                s['Summary'],
                Category(s['Category']),
                Account(s['Account']),
                None if s['Account2'] == 'None' else Account(s['Account2'])
            ))


def print_data():
    # prints the transactions, accounts and categories into separate .json files
    with open(os.path.join('data', 'transactions.json'), 'w') as f:
        for transaction in transactionList:
            f.write(json.dumps(transaction.to_dict()) + '\n')

    with open(os.path.join('data', 'accounts.json'), 'w') as f:
        for account in accounts:
            f.write(json.dumps(account.to_dict()) + '\n')

    with open(os.path.join('data', 'categories.json'), 'w') as f:
        for category in categories:
            f.write(json.dumps(category.to_dict()) + '\n')
