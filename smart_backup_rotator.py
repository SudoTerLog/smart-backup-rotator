# ---------------------------------------------------------------------------
# БЛОК 1: ПОДКЛЮЧЕНИЕ МОДУЛЕЙ И СИСТЕМНЫХ БИБЛИОТЕК
# BLOCK 1: CONNECTING MODULES AND SYSTEM LIBRARIES
# ---------------------------------------------------------------------------
import yaml
import shutil
from datetime import datetime
import os
from pathlib import Path
from tqdm import tqdm
import time
# ---------------------------------------------------------------------------
# БЛОК 2: ФУНКЦИИ ЛОГИРОВАНИЯ И СБОРА СТАТУС-ОТЧЕТОВ (YAML STATE LOG)
# BLOCK 2: FUNCTIONS FOR LOGGING AND COLLECTION OF STATUS REPORTS (YAML STATE LOG)
# ---------------------------------------------------------------------------
# функция создания YAML-файла куда скрип будет заносить отчеты о проделанной работе
# the function of creating a YAML file where the script will record reports on the work done
def write_yaml_log(status, details):
    """Функция для автоматического добавления записи в YAML-историю"""
    report_data = {
    "backup_report":{
        "check_date": currect_time,
        "processed_file": latest_file.name,
        "status": status,
        "details": details
    }
}
    with open('config.yaml', 'a', encoding='utf-8') as yaml_report_file:
        # Перед каждой новой записью принудительно пишем разделитель документов YAML
        # Before each new record, we force a YAML document separator to be written
        yaml_report_file.write("\n---\n")
        # записываем наш словарь в формате YAML с красивымы оступами
        # we write our dictionary in YAML format with beautiful margins
        yaml.dump(report_data, yaml_report_file, allow_unicode=True, default_flow_style=False)
# заносим в переменную откуда будем копировать файлы
# we put it in a variable from where we will copy the files
source_dir = Path(r"C:\TestBackups")
# Поиск самого свежего бэкапа
# Finding the most recent backup
latest_file = max(source_dir.glob('*'), key=os.path.getmtime)
# Узнаем точную дату и время
# Find out the exact date and time
currect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(latest_file.name)
# Узнаем точный размер найденного свежего файла бэкапа в чистых байтах
# Find out the exact size of the found fresh backup file in pure bytes
file_size = latest_file.stat().st_size
# Запрашиваем у операционной системы емкость диска D: (все значения возвращаются в байтах)
# Нижнее подчеркивание в total и use означает, что эти переменные нам не нужны
# We ask the operating system for the capacity of disk D: (all values ​​are returned in bytes)
# The underscore in total and use means we don't need these variables
total, use, free = shutil.disk_usage('D:')
# Переводим свободные байты в понятные человеку Гигабайты (делим на 1024 в кубе)
# Округляем до целого числа с помощью функции int()
# We convert free bytes into human-readable Gigabytes (divide by 1024 cubed)
# Round to an integer using the int() function
free_pc = int(free/ (1024**3))
print(file_size, free_pc)
# Защитная проверка безопасности (SecOps): влезет ли файл на диск?
# Сравниваем строго байты с байтами (free и file_size), чтобы избежать ошибок
# Protective security check (SecOps): will the file fit on the disk?
# We strictly compare bytes with bytes (free and file_size) to avoid errors
if free < file_size:
    # Формируем сообщение об ошибке с указанием точных цифр
    # We generate an error message indicating exact numbers
    msg = f"Недостаточно места на целевом диске! Требуется: {file_size} байт, свободно {free} байт."
    print(f"[!!!] {msg}")
    # Записываем аварийный статус в наш YAML-аудит
    # We record the emergency status in our YAML audit
    write_yaml_log("Error (No space)", msg)
    # Принудительно останавливаем скрипт, так как копирование невозможно
    # Forcefully stop the script, since copying is impossible
    exit()
# ---------------------------------------------------------------------------
# БЛОК 3: ИНИЦИАЛИЗАЦИЯ ПУТЕЙ НАЗНАЧЕНИЯ И ПРОВЕРКА ИДЕМПОТЕНТНОСТИ (НАЛИЧИЯ ФАЙЛОВ)
# BLOCK 3: INITIALIZING DESTINATION PATHS AND CHECKING IDEMPOTENCY (PRESENCE OF FILES)
# ---------------------------------------------------------------------------
# Объявляем абсолютные пути к целевым папкам с помощью библиотеки pathlib
# Declaring absolute paths to target folders using the pathlib library
dest_pc_dir = Path(r"D:\Backups")  # Локальное хранилище на твоем ПК / # Local storage on your PC
dest_server_new_dir = Path(r"D:\Server-new") # Папка имитации Нового Сервера / # New Server Simulation Folder
dest_server_dir = Path(r"C:\TestBackups") # Папка Старого Сервера (откуда берем бэкап) / # Old Server folder (where we get the backup from)
# Формируем полные пути к будущим файлам, склеивая путь к папке и имя бэкапа через слэш "/"
# We form full paths to future files by concatenating the folder path and the backup name using a slash “/”
file_on_pc = dest_pc_dir / latest_file.name
file_on_server = dest_server_dir / latest_file.name
file_on_server_new = dest_server_new_dir / latest_file.name
# Проверяем физическое наличие этого конкретного бэкапа в каждой целевой папке.
# Метод .exists() вернет True, если файл уже скопирован, и False, если его там нет.
# We check the physical presence of this specific backup in each target folder.
# The .exists() method will return True if the file is already copied, and False if it is not there.
has_pc = file_on_pc.exists()
has_server = file_on_server.exists()
has_server_new = file_on_server_new.exists() 
# ---------------------------------------------------------------------------
# БЛОК 4: ИДЕМПОТЕНТНОЕ КОПИРОВАНИЕ БЭКАПОВ С ПОЛОСОЙ ПРОГРЕССА (TQDM)
# BLOCK 4: IDEMPOTENT COPYING BACKUPS WITH PROGRESS BAR (TQDM)
# ---------------------------------------------------------------------------
try:
    if not has_pc:
        print(f"Запуск копирования файла {latest_file.name} на ПК...")
        with open(latest_file, 'rb') as f_src, open(file_on_pc, 'wb') as f_dst:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Копирование на ПК") as pbar:
                while True:
                    #  это ровно 1 Мегабайт в байтах
                    # «Не пытайся засунуть весь огромный бэкап целиком в оперативную память (иначе сервер зависнет). Читай его аккуратными кусочками по 1 Мегабайту»
                    # this is exactly 1 megabyte in bytes
                    # “Don’t try to put the entire huge backup entirely into RAM (otherwise the server will freeze). Read it in neat pieces of 1 Megabyte"
                    chunk = f_src.read(1024 * 1024)
                    if not chunk:
                       break
                    f_dst.write(chunk)
                    # Берет размер прочитанного кусочка (1 МБ) и сдвигает полосу прогресса tqdm вперед на этот размер
                    # takes the size of the read piece (1 MB) and moves the tqdm progress bar forward by this size
                    pbar.update(len(chunk))
        print(f"Бэкап сохранен на ПК: {dest_pc_dir}")
         
    if not has_server_new:
        print(f"Запуск копирования файла {latest_file.name} на Сервер Б...")
        # Менеджер контекста, который открывает сразу два файла одновременно (один — откуда копируем, второй — куда записываем)
        # A context manager that opens two files at once (one is where we copy from, the second is where we write)
        with open(latest_file, 'rb') as f_scr, open(file_on_server_new, 'wb') as f_dst:
            # Копирование большими кусками (чанками) с полосой
            # Copying in large chunks (chunks) with a stripe
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Копирование на Сервер") as pbar:
                while True:
                    chunk = f_scr.read(1024 * 1024)
                    if not chunk:
                        break
                    f_dst.write(chunk)
                    pbar.update(len(chunk))
        print(f"Бэкап сохранен на ПК: {dest_server_new_dir}")
    # если все копирование прошло успешно заносим в лог-отчет
    # if all copying was successful, enter it into the log report
    success_msg = f"Бэкапы успешно выгружены. ПК: {dest_pc_dir} | Сервер: {dest_server_new_dir}"
    write_yaml_log("Success", success_msg)
    # блок занесения в лог информации проверки файлов на месте ли они
    # block for logging information to check if files are in place
    if has_pc and has_server_new:
        success_msg = f"Все бэкапы на месте. ПК: {dest_pc_dir}. Сервер {dest_server_new_dir}"
        write_yaml_log("Success", success_msg)
    # Блок занесения в лог информации по поводу копирования бэкапов
    # Block for logging information about copying backups
    else:
        success_msg = f"Все успешно выгружены. ПК: {dest_pc_dir}. Сервер {dest_server_new_dir}"
        write_yaml_log("Success", success_msg)
        
except Exception as error_msg:
    # блок ошибки если будет какая то ошибка то она будет занесена в лог для прочтения дежурным админом
    # error block if there is any error, it will be entered into the log for reading by the duty admin
    critical_msg = f"Критический сбой при копировании файл! Системная ошибка: {error_msg}"
    print(f"[Критическая ошибка] {critical_msg}")
    write_yaml_log("Error (Critical)", critical_msg)
# ---------------------------------------------------------------------------
# БЛОК 5: РОТАЦИЯ ХРАНИЛИЩА — ОЧИСТКА СТАРЫХ ФАЙЛОВ И АУДИТ «ДВОРНИКА»
# BLOCK 5: STORAGE ROTATION - CLEANING OLD FILES AND AUDITING THE WIPERER
# ---------------------------------------------------------------------------
print("Проверка старых бэкапов на удаление")
# Вычисляем критическую точку во времени (7 дней назад в секундах)
# 7 дней * 24 часа * 60 минут * 60 секунд
# Calculate the critical point in time (7 days ago in seconds)
# 7 days * 24 hours * 60 minutes * 60 seconds
seven_days_ago = time.time() - (7 * 24 * 60 * 60)
deleted_files = []
# .iterdir() - это метод pathlib который берет все файлы в ппапке по очереди
# .iterdir() is a pathlib method that takes all the files in a subfolder one by one
for file_path in dest_pc_dir.iterdir():
    # Проверяем что это именно файл а не случайная папка
    # We check that this is a file and not a random folder
    if file_path.is_file():
        # узнаем время последнего изменения этого файла
        # find out the last modification time of this file
        file_age = file_path.stat().st_mtime
        # проверяем был ли изменен файл раньше чем 7 днгей назад
        # Checking whether the file was changed earlier than 7 days ago
        if file_age < seven_days_ago:
            print(f"Файл {file_path.name} старше 7 дней. Удаляем...")
            # .unlink() - это метод pathlib для удаления файла!
            # .unlink() is pathlib's method to remove a file!
            file_path.unlink()
            # добавляем имя удаленного файла в список для отчета
            # add the name of the remote file to the list for the report
            deleted_files.append(file_path.name)
# блок проверки бэкапов на старость если бэкапов старше 7 дней нет то заносим в отчет результат
# block for checking backups for old age, if there are no backups older than 7 days, then we enter the result in the report
if not deleted_files:
    details_msg = f"Старых бэкапов не обнаружено, все файлы в порядке."
    write_yaml_log("Success", details_msg)
    print("Отчет занесен с лог")
# если файл страшне 7 дней был найден и удален то заносим результат в лог
# if a file more than 7 days old was found and deleted, then we record the result in the log
else:
    details_msg = f"Успешно удалены старые бэкапы: {deleted_files}"
    write_yaml_log("Success", details_msg)
    print("Отчет занесен с лог")