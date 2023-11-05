from http.client import HTTPException
from typing import Union
from fastapi import FastAPI, Depends, HTTPException, Request
import MySQLdb
from mysql.connector import pooling
import mysql.connector.pooling
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import socket
# from fastapi import HTTPException

# DB config
db_config = {
    'host': '202.28.34.197',
    'db': 'web65_64011212125',
    'user': 'web65_64011212125',
    'password': '64011212125@csmsu',
}

db_connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="my_pool",
    pool_size=5,
    **db_config
)

def get_db():
    connection = db_connection_pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()


# api
app = FastAPI()

# model
class User(BaseModel):
    username: str 
    email: str

class Login(BaseModel):
    username: str
    password: str


@app.get("/")
def read_root():
    return {"Hello": "SDSD5454454"}



@app.get("/user/{user_id}")
def read_item(user_id: int, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM user WHERE uid = %s"
    cursor.execute(query, (user_id,))
    data = cursor.fetchone()
    cursor.close()
    if data is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = {
        "uid": data[0],
        "username": data[1],
        "name": data[3],
        "email": data[4],
        "phone": data[5]   
    }
    return JSONResponse(content=user_data)

@app.post("/user/login")
async def login(login_data: Request, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    login_dataJson = await login_data.json()
    cursor = db.cursor()
    query = "SELECT uid FROM user WHERE username = %s or email = %s"
    cursor.execute(query, (login_dataJson["username"], login_dataJson["username"]))
    user = cursor.fetchone()
    # print('fdddddd')
    
    user_data = ""
    if user is None:
        print("sdfffffffffffffffffff")
        cursor.close()
        raise HTTPException(status_code=404, detail="User not found")
    # else:
    #     print(type(user[0]))
    else:
        query = "SELECT password FROM user WHERE uid = %s"
        cursor.execute(query, (user[0],))
        chkPwd = cursor.fetchone()
        if chkPwd[0] == login_dataJson["password"]:
            query = "SELECT * FROM user WHERE uid = %s"
            cursor.execute(query, (user[0],))
            data = cursor.fetchone()
            cursor.close()
            user_data = {
                "uid": data[0],
                "username": data[1],
                "name": data[3],
                "email": data[4],
                "phone": data[5]     
            }
        else:
             cursor.close()
             raise HTTPException(status_code=401, detail="Password not Correct")


    return JSONResponse(content=user_data)

@app.post("/user/register")
async def regis(regis_data: Request, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    regis_dataJson = await regis_data.json()
    cursor = db.cursor()
    query_check = "SELECT * FROM user WHERE username = %s"
    cursor.execute(query_check, (regis_dataJson["username"],))
    existing_user = cursor.fetchone()

    if existing_user:
        # มีข้อมูลซ้ำ
        print("มีผู้ใช้นี้แล้ว")
        raise HTTPException(status_code=422, detail="User already exists")

    else:
        query = "INSERT INTO user (uid, username, password, name, email, phone) VALUES (NULL, %s, %s, %s, %s, %s);"
        try:
            cursor.execute(query, (regis_dataJson["username"], regis_dataJson["password"], regis_dataJson["name"], regis_dataJson["email"], regis_dataJson["phone"]))
            db.commit()
            print("เพิ่มข้อมูลสำเร็จ")
        except mysql.connector.Error as err:
            print("Error:", err)
            db.rollback()

        data = {"1_record_insert_id": cursor.lastrowid}
        cursor.close()
    # print('fdddddd')

    return JSONResponse(content=data)


@app.post("/user/update")
async def regis(regis_data: Request, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    regis_dataJson = await regis_data.json()
    cursor = db.cursor()
    query_check = "SELECT * FROM user WHERE uid = %s"
    cursor.execute(query_check, (regis_dataJson["uid"],))
    existing_user = cursor.fetchone()

    if existing_user:
        # มีข้อมูลซ้ำ
        print("มีผู้ใช้")
        query = "UPDATE user SET name = %s, email = %s, phone = %s WHERE uid = %s;"
        try:
            cursor.execute(query, (regis_dataJson["name"], regis_dataJson["email"], regis_dataJson["phone"],regis_dataJson["uid"]))
            db.commit()
            print("แก้ไขข้อมูลสำเร็จ")
        except mysql.connector.Error as err:
            print("Error:", err)
            db.rollback()
            

        data = {"1_record_insert_id": cursor.lastrowid}
        cursor.close()

    else:
        raise HTTPException(status_code=404, detail="user not found")
        
    

    return JSONResponse(content=data)


@app.get("/books")
def read_books(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT books.bid, books.bookName, books.wid, books.tid, books.bookPic, bookType.typeName, writer.writeName FROM books JOIN bookType ON books.tid = bookType.tid JOIN writer ON books.wid = writer.wid;"
    cursor.execute(query)
    books = cursor.fetchall()
    cursor.close()
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    books_data = []
    for book in books:
        book_data = {
            "bid": book[0],
            "bookName": book[1],
            "wid": book[2],
            "tid": book[3],
            "bookPic": book[4],
            "typeName": book[5],
            "writeName": book[6]
        }
        books_data.append(book_data)
    return JSONResponse(content=books_data)


@app.get("/books/chapters")
def read_chapters(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM chapter"
    cursor.execute(query)
    chapters = cursor.fetchall()
    cursor.close()
    if not chapters:
        raise HTTPException(status_code=404, detail="Books not found")
    chapters_data = []
    for chapter in chapters:
        chapter_data = {
            "chid": chapter[0],
            "bid": chapter[1],
            "chNum": chapter[2],
            "chName": chapter[3],
            "content": chapter[4]
            
        }
        chapters_data.append(chapter_data)
    return JSONResponse(content=chapters_data)

@app.get("/books/chapters/{book_id}")
def read_chapters(book_id: int, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM chapter WHERE bid = %s"
    cursor.execute(query, (book_id,))
    chapters = cursor.fetchall()
    cursor.close()
    if not chapters:
        raise HTTPException(status_code=404, detail="Books not found")
    chapters_data = []
    for chapter in chapters:
        chapter_data = {
            "chid": chapter[0],
            "bid": chapter[1],
            "chNum": chapter[2],
            "chName": chapter[3],
            "content": chapter[4]
        }
        chapters_data.append(chapter_data)
    return JSONResponse(content=chapters_data)

@app.get("/booktypes")
def read_booktypes(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM bookType"
    cursor.execute(query)
    types = cursor.fetchall()
    cursor.close()
    if not types:
        raise HTTPException(status_code=404, detail="types not found")
    types_data = []
    for type in types:
        type_data = {
            "tid": type[0],
            "typeName": type[1]
        }
        types_data.append(type_data)
    return JSONResponse(content=types_data)

@app.get("/writers")
def read_writers(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM writer"
    cursor.execute(query)
    writers = cursor.fetchall()
    cursor.close()
    if not writers:
        raise HTTPException(status_code=404, detail="writers not found")
    writers_data = []
    for writer in writers:
        writer_data = {
            "wid": writer[0],
            "writeName": writer[1]
        }
        writers_data.append(writer_data)
    return JSONResponse(content=writers_data)

@app.get("/favbooks")
def read_favbooks(db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM favBooks"
    cursor.execute(query)
    favbooks = cursor.fetchall()
    cursor.close()
    if not favbooks:
        raise HTTPException(status_code=404, detail="writers not found")
    favbooks_data = []
    for favbook in favbooks:
        favbook_data = {
            "fid": favbook[0],
            "uid": favbook[1],
            "bid": favbook[2]
        }
        favbooks_data.append(favbook_data)
    return JSONResponse(content=favbooks_data)

@app.get("/favbooks/{uid}")
def read_userfavbooks(uid:int, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT books.bid, books.bookName, books.wid, books.tid, books.bookPic, bookType.typeName, writer.writeName FROM favBooks JOIN books ON favBooks.bid = books.bid JOIN bookType ON books.tid = bookType.tid JOIN writer ON books.wid = writer.wid WHERE favBooks.uid = %s;" 
    cursor.execute(query, (uid,))
    favbooks = cursor.fetchall()
    cursor.close()
    if not favbooks:
        raise HTTPException(status_code=404, detail="favBooks not found")
    favbooks_data = []
    for favbook in favbooks:
        favbook_data = {
            "bid": favbook[0],
            "bookName": favbook[1],
            "wid": favbook[2],
            "tid": favbook[3],
            "bookPic": favbook[4],
            "typeName": favbook[5],
            "writeName": favbook[6]
        }
        favbooks_data.append(favbook_data)
    return JSONResponse(content=favbooks_data)

@app.get("/user/favbooks/{uid}/{bid}")
def read_userfavbooks(uid:int, bid:int, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    query = "SELECT * FROM favBooks WHERE uid = %s AND bid =%s;" 
    cursor.execute(query, (uid,bid))
    favbook = cursor.fetchone()
    cursor.close()
    if not favbook:
        raise HTTPException(status_code=404, detail="favBooks not found")
    else:
        raise HTTPException(status_code=200, detail="favBooks found")
    
    


@app.post("/favbook/addordelete")
async def favbookAdd(favbook_data: Request, db: mysql.connector.connection.MySQLConnection = Depends(get_db)):
    favbook_dataJson = await favbook_data.json()
    cursor = db.cursor()
    query_check = "SELECT * FROM favBooks WHERE uid = %s and bid = %s "
    cursor.execute(query_check, (favbook_dataJson["uid"],favbook_dataJson["bid"]))
    existing_favbook = cursor.fetchone()

    if existing_favbook:
        # มีข้อมูลซ้ำ
        print("มีหนังสือเล่มนี้แล้ว")
        query_check = "DELETE FROM favBooks WHERE uid = %s and bid = %s "
        cursor.execute(query_check, (favbook_dataJson["uid"],favbook_dataJson["bid"]))
        db.commit()
        cursor.close()
        raise HTTPException(status_code=422, detail="FavBook already exists Delete Success")

    else:
        query = "INSERT INTO favBooks (fid, uid, bid) VALUES (NULL, %s, %s);"
        try:
            cursor.execute(query, (favbook_dataJson["uid"], favbook_dataJson["bid"]))
            db.commit()
            print("เพิ่มข้อมูลสำเร็จ")
            cursor.close()
            raise HTTPException(status_code=200, detail="FavBook insert Success")
        except mysql.connector.Error as err:
            print("Error:", err)
            db.rollback()
            raise HTTPException(status_code=201, detail="FavBook insert Fail")


    