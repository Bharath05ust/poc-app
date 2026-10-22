from uuid import uuid4

from pydantic import BaseModel


class Book(BaseModel):
    book_id: str
    title: str
    category: str
    price: float
    stock: int
    description: str


class OrderReceipt(BaseModel):
    order_id: str
    book_id: str
    title: str
    quantity: int
    total: float
    status: str


class BookSearchResult(BaseModel):
    query: str
    total: int
    books: list[Book]


class ReadingPlan(BaseModel):
    goal: str
    steps: list[str]


BOOKS = [
    Book(book_id="b101", title="The API Handbook", category="Technology", price=28.50, stock=7, description="REST, HTTP, and practical service design."),
    Book(book_id="b102", title="Building with MCP", category="Technology", price=34.00, stock=4, description="Tools, resources, and prompts for AI hosts."),
    Book(book_id="b103", title="Python Services", category="Technology", price=31.25, stock=6, description="Build reliable backends with Python."),
    Book(book_id="b104", title="API Design Patterns", category="Technology", price=36.75, stock=5, description="Design stable and versioned HTTP APIs."),
    Book(book_id="b105", title="Async Python in Practice", category="Technology", price=29.90, stock=8, description="Use asynchronous Python for network services."),
    Book(book_id="b106", title="Secure Service Design", category="Technology", price=32.00, stock=5, description="Protect service endpoints and user data."),
    Book(book_id="b201", title="The Midnight Library", category="Fiction", price=18.99, stock=5, description="A novel about choices and possible lives."),
    Book(book_id="b202", title="Sea of Tranquility", category="Fiction", price=16.50, stock=3, description="A literary mystery across time."),
    Book(book_id="b203", title="Project Hail Mary", category="Fiction", price=19.50, stock=4, description="A science-fiction mission to save humanity."),
    Book(book_id="b204", title="The Long Way to a Small, Angry Planet", category="Fiction", price=17.25, stock=6, description="A found-family journey through space."),
    Book(book_id="b301", title="Making Data Useful", category="Non-fiction", price=24.50, stock=4, description="Turn everyday data into clear decisions."),
    Book(book_id="b302", title="The Science of Everyday Life", category="Science", price=22.00, stock=4, description="Explore the science behind familiar things."),
]


def list_books(query: str = "", category: str | None = None) -> list[Book]:
    normalized_query = query.strip().casefold()
    normalized_category = category.strip().casefold() if category else ""
    return [
        book
        for book in BOOKS
        if (not normalized_query or normalized_query in f"{book.title} {book.category} {book.description}".casefold())
        and (not normalized_category or normalized_category == book.category.casefold())
    ]


def place_order(book_id: str, quantity: int) -> OrderReceipt:
    book = next((item for item in BOOKS if item.book_id.casefold() == book_id.strip().casefold()), None)
    if book is None:
        raise ValueError(f"No book found with ID {book_id!r}.")
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")
    if quantity > book.stock:
        raise ValueError(f"Only {book.stock} copies of {book.title} are available.")

    book.stock -= quantity
    return OrderReceipt(
        order_id=f"DEMO-{uuid4().hex[:8].upper()}",
        book_id=book.book_id,
        title=book.title,
        quantity=quantity,
        total=round(book.price * quantity, 2),
        status="confirmed",
    )


def create_reading_plan(goal: str, available_books: list[Book] | None = None) -> ReadingPlan:
    normalized_goal = goal.strip().casefold()
    if not normalized_goal:
        raise ValueError("Describe what you want to learn.")

    catalog = available_books if available_books is not None else BOOKS
    books_by_id = {book.book_id: book for book in catalog if book.stock > 0}
    if any(word in normalized_goal for word in ("api", "backend", "python", "software")):
        preferred_ids = ("b101", "b103", "b102")
    else:
        preferred_ids = ("b103", "b102", "b101")
    selected = [books_by_id[book_id] for book_id in preferred_ids if book_id in books_by_id]
    selected.extend(book for book in catalog if book.stock > 0 and book not in selected)
    if not selected:
        raise ValueError("There are no books in stock to build a reading plan.")
    selected = selected[:3]

    return ReadingPlan(
        goal=goal.strip(),
        steps=[
            f"{index}. Read {book.title}: {book.description} ({book.stock} in stock)"
            for index, book in enumerate(selected, 1)
        ],
    )