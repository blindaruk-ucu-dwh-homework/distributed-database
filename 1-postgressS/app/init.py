import psycopg2
import logging

from concurrent.futures import ThreadPoolExecutor
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфігурація підключення до PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname="mydatabase",
        user="myuser",
        password="mypassword",
        host="db",
        port=5432
    )

def update_counter_to_0():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE user_counter SET counter = %s WHERE user_id = %s",
            (0, 1)
        )
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def get_counter():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "select counter FROM user_counter WHERE user_id = %s",
            (1, )
        )

        counter = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return counter
    except Exception as e:
        print(f"Error: {e}")


def update_counter_lost_update():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for _ in range(10000):
            cursor.execute("SELECT counter FROM user_counter WHERE user_id = %s", (1,))
            counter = cursor.fetchone()[0]
            counter += 1

            cursor.execute(
                "UPDATE user_counter SET counter = %s WHERE user_id = %s",
                (counter, 1)
            )
            conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def update_counter_in_place_update():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for _ in range(10000):
            cursor.execute("update user_counter set counter = counter + 1 where user_id = %s", (1, ))
            conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

def update_counter_lok_for_row_update():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        for _ in range(10000):
            cursor.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE")
            counter = cursor.fetchone()[0]

            counter = counter + 1
            cursor.execute("update user_counter set counter = %s where user_id = %s", (counter, 1))
            conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

def update_counter_optimisitc_cncurency_update():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for _ in range(10000):
            while (True):
                cursor.execute("SELECT counter, version FROM user_counter WHERE user_id = %s", (1,))
                result = cursor.fetchone()

                if result is None:
                    raise Exception("Запис для user_id = 1 не знайдено")

                counter, version = result
                counter += 1
                new_version = version + 1

                # Спробувати оновити запис
                cursor.execute(
                    "UPDATE user_counter SET counter = %s, version = %s WHERE user_id = %s AND version = %s",
                    (counter, new_version, 1, version)
                )
                conn.commit()

                # Перевірити, чи запис було оновлено
                if cursor.rowcount > 0:
                    break  # Завершити цикл, якщо оновлення пройшло успішно

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")



# Виконання з 10 потоків
if __name__ == "__main__":
    logger.info("START 1: LOST UPDATE")
    overall_start_time = time.time()  # Початок загального заміру часу

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_counter_lost_update) for _ in range(10)]

        for future in futures:
            future.result()

    overall_end_time = time.time()  # Кінець загального заміру часу
    logger.info(f"1. END 1: LOST UPDATE {overall_end_time - overall_start_time:.2f} seconds.")
    logger.info(f"1. END 1: LOST UPDATE {get_counter()} counter.")

    #########################
    logger.info("START 2: Counter in place")
    update_counter_to_0()
    overall_start_time = time.time()  # Початок загального заміру часу

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_counter_in_place_update) for _ in range(10)]

        for future in futures:
            future.result()

    overall_end_time = time.time()  # Кінець загального заміру часу
    logger.info(f"1. END 2: Counter IN PLace {overall_end_time - overall_start_time:.2f} seconds.")
    logger.info(f"1. END 2: {get_counter()} counter.")

    ############
    logger.info("START 3 Lok row")
    update_counter_to_0()
    overall_start_time = time.time()  # Початок загального заміру часу

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_counter_lok_for_row_update) for _ in range(10)]

        for future in futures:
            future.result()

    overall_end_time = time.time()  # Кінець загального заміру часу
    logger.info(f"1. END 3: Counter Lok row {overall_end_time - overall_start_time:.2f} seconds.")
    logger.info(f"1. END 3: {get_counter()} counter.")

    ############
    logger.info("START 4 Optimistic concurency update")
    update_counter_to_0()
    overall_start_time = time.time()  # Початок загального заміру часу

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_counter_optimisitc_cncurency_update) for _ in range(10)]

        for future in futures:
            future.result()

    overall_end_time = time.time()  # Кінець загального заміру часу
    logger.info(f"1. END 4:Optimistic concurency update {overall_end_time - overall_start_time:.2f} seconds.")
    logger.info(f"1. END 4: {get_counter()} counter.")

