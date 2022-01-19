import psycopg2 as ps
import hashlib as h
import requests as r
import logging as log
import time as t

#define log format
log.basicConfig(filename="/var/log/weatherman/log.txt", level=log.INFO, format="%(asctime)s:%(message)s")
pathToOffers = "/var/log/weatherman/offers.txt"

def hashToDB(mess, db_info: list):
    c = 0
    with ps.connect(dbname=db_info[1], user=db_info[2]) as conn:
        with conn.cursor() as cursor:
            if mess.from_user.username:
                conn.autocommit = True
                command = f"select * from {db_info[0]}"
                cursor.execute(command)
                hashUsername = h.md5(mess.from_user.username.encode()).hexdigest()
                for row in cursor:
                    if hashUsername != row[1]:
                        c += 1
                if c == cursor.rowcount:
                    log.info("New user added")
                    command = f"insert into {db_info[0]} (hash) values ('{hashUsername}')"
                    cursor.execute(command)
                command = f"update {db_info[0]} set cnt = cnt + 1 where hash = '{hashUsername}'"
                cursor.execute(command)
                command = f"select * from {db_info[0]}"
                cursor.execute(command)
                for row in cursor.fetchall():
                    if not row[3]:
                        command = f"update {db_info[0]} set chatID = {mess.chat.id} where hash = '{hashUsername}'"
                        cursor.execute(command)
            
def getNumUsers(db_info: list):
    with ps.connect(dbname=db_info[1], user=db_info[2]) as conn:
        with conn.cursor() as cursor:
            conn.autocommit = True
            command = f"SELECT * FROM {db_info[0]}"
            cursor.execute(command)
            return cursor.rowcount

def getJoke() -> str:
    url = "http://rzhunemogu.ru/RandJSON.aspx?CType=1"
    response = r.get(url)
    if response.status_code < 300:
        log.info(f"Request to {url} was successful")
    else:
        log.info(f"Request to {url} was unsuccessful")
    return response.text[12:-3]

def getChatIDs(db_info: list) -> list:
    res = []
    with ps.connect(dbname=db_info[1], user=db_info[2]) as conn:
        with conn.cursor() as cursor:
            command = f"select * from {db_info[0]}"
            cursor.execute(command)
            for row in cursor:
                if row[-1]:
                    res.append(row[-1])
    return res

def appendToFile(mess: str, path: str) -> None:
    with open(path, "a") as f:
        mess = t.asctime() + ": " + mess + "\n"
        f.write(mess)

def saveOffer(message, bot):
    appendToFile(message.text, pathToOffers)
    bot.send_message(message.chat.id, "Спасибо!")
