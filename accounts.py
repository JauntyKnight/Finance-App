import requests
import datetime

# importing data from this website with EUR being the base currency
url = 'http://api.exchangeratesapi.io/v1/'

# Making the request
access_key = 'access_key=e855c4d178d5a941a369c3e0d2a76c4d'
data = requests.get(url + 'latest' + '?' + access_key).json()

months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def date_str_to_int(strdate: str):
    """
    :param strdate: DD/MM/YYYY representation of a date
    """
    return [int(i) for i in strdate.split('/')][::-1]


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
        self.balance = int(balance)
        self.currency = currency

    def __str__(self):
        return f'{self.name}: {self.currency}'

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name and self.currency == other.currency

    def __lt__(self, other):
        return self.name < other.name

    def add_funds(self, amount=0):
        for i in accounts:
            if i == self:
                i.balance += amount
                return

    def sub_funds(self, amount=0):
        self.add_funds(-amount)


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


categories = set()
categories.add(Category('Travel'))
categories.add(Category('Restaurants'))
categories.add(Category('Shopping'))
categories.add(Category('Online Shopping'))
categories.add(Category('Other'))
categories.add(Category('Living'))
categories.add(Category('Entertainment'))
categories.add(Category('Groceries'))


accounts = set()
accounts.add(Account('smth'))
accounts.add(Account('Card'))
accounts.add(Account('Cash'))


def validate_transaction(data):
    # checking the date
    try:
        Date(*date_str_to_int(data['Date']))
    except:
        return False
    # checking the amount
    try:
        a = int(data['Amount'])
        if a <= 0:
            return False
    except:
        return False
    # no need to check smth else, since the other options are choosen
    # from a set of options
    return True


def create_transaction_data(data):
    r = []
    r.append(Date(*date_str_to_int(data['Date'])))
    r.append(int(data['Amount']))
    r.append(data['Summary'])
    r.append(Category(data['Category']))
    accname, accur = data['Account'].split(': ')
    r.append(Account(accname, 0, accur))
    if data['Summary'] == 'Transfer':
        accname, accur = data['Account2'].split(': ')
        r.append(Account(accname, 0, accur))
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


class TransactionsList:
    def __init__(self, parent=None, filters=None):
        if not parent:
            self.list = []  # must always be sorted by the date of transaction
        else:
            self.list = self.filter(parent, filters)
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
        if 'Date from' in filters and filters['Date from'] > transaction.date:
            return False
        if 'Date to' in filters and filters['Date to'] < transaction.date:
            return False
        if 'Amount from' in filters and filters['Amount from'] > transaction.amount:
            return False
        if 'Amount to' in filters and filters['Amount to'] < transaction.amount:
            return False
        if 'Category' in filters and transaction.category not in filters['Category']:
            return False
        if 'Account' in filters and transaction.account not in filters['Account']:
            return False
        return True

    def filter(self, parent, filters):
        for i in parent:
            if self._check_filter(filters, i):
                yield i

    def push(self, transaction):
        """
        pushes a transaction onto the stack
        :param transaction: the transaction to be added
        :return: None
        """
        self.list.append(transaction)

    def remove(self, transaction):
        """
        TBA
        :param transaction:
        :return:
        """
        pass

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
