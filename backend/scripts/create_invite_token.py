import sys
import uuid
import pymysql
from src.dependencies import db_config

def createAndAddInviteToken():
    random_token = str(uuid.uuid4())
    sql_client = pymysql.connect(**db_config)
    with sql_client.cursor() as cur:
        cur.execute("""
            INSERT IGNORE INTO user_invites (invite_key)
                VALUES (%s)
        """, (random_token))
    return random_token

if __name__ == '__main__':
    random_token = createAndAddInviteToken()
    print(f'Invite Token {random_token}')