from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from databases import Database

DATABASE_URL = "mysql+mysqlconnector://jtbc:1234@localhost/jtbc"

metadata = MetaData()

# users = Table(
#     "users",
#     metadata,
#     Column("id", Integer, primary_key=True, index=True, autoincrement=True),
#     Column("username", String(20), unique=True, index=True),
#     Column("hashed_password", String(100)),
#     Column("name", String(50))
# )

posts = Table(
    "posts",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("title", String(50)),
    Column("content", String(300)),
    Column("category", String(50)),
    Column("imgUrl", String(100))
)


engine = create_engine(DATABASE_URL)
metadata.create_all(engine, checkfirst=True)

database = Database(DATABASE_URL)
 