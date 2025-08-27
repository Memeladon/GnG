import os
import redis

def redis_test_con():
    r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'),
                    username=os.getenv('REDIS_USER'), password=os.getenv('REDIS_PASSWORD'))
    try:
        info = r.info()
        print(info['redis_version'])
        response = r.ping()
        if response:
            print("Connection success!")
        else:
            print("Can't connect to redis db.")
    except redis.exceptions.RedisError as e:
        print(f"ERROR: {e}")

