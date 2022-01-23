<h1>My first software project</h1>

<h2>The program is a PyGTK implementation of a finance app. 
It has the following features:</h2>

- Adding and deleting transactions
- Specifying a category for a transaction
- Specifying an account for a transaction
- Creating and deleting of categories and accounts
- Filtering the transactions
- Sorting the transactions by a specified criteria
- Exchange currency calculator

The data is stored in `.json()` files, and it is read at
the start of the program and written at the end of the
running cycle.

<h3>Overview tab:</h3>

It features a `Gtk.TreeView()` widget that holds the list of 
transactions. The list may be sorted by clicking on the 
header. A second click on the same column will sort the 
list in reverse order. The Python's STL sort method is
used for this, so it runs in _O(NlogN)_. In case of sorting
by the amount of a transaction, it ignores the currency
and sorts them by the absolute value, which I think is more
appropriate.

The tab has the buttons: **Add, Filter, Delete**. Their
functionality is pretty straightforward.

<h3>Accounts and Categories tabs:</h3>

Here the user can monitor his accounts and categories, 
respectively. There's an **Add** button present which may
add a new category or account. A new one must have an
original name. In case the user tries to add a new
account/category with an already existent name, an error
message will pop out.
The data is represented by the `Account()` and 
`Category()` classes, which have a `__hash__()` magic
method implemented, helping store the objects in a 
`set()`.

<h3>Exchange Tab</h3>

The tab features again a `Gtk.TreeView()` to help visualize
the exchange rates of a lot of currencies present in the world
relative to the Euro.
The right panel of the same tab features a currency
exchange calculator between 3 currencies simultaneously.
The user may select the currencies using the corresponding
buttons, in which case a selection dialog will pop up.
The values are converted at the press of the **Enter** key.



Andrei Lupasco
