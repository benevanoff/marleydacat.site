import sys
import pymysql
import nacl.pwhash.argon2id
from src.dependencies import db_config

if __name__ == '__main__':
    sql_client = pymysql.connect(**db_config)
    with sql_client.cursor() as cur:
        cur.execute("""
            INSERT IGNORE INTO users (username, email, password)
                VALUES (%s, %s, %s)
        """, (sys.argv[1], sys.argv[2], nacl.pwhash.argon2id.str(sys.argv[3].encode('utf-8')).decode('utf-8')))