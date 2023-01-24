# ratesProj

Порядок установки проекта 
1. Установка базы 
   Сразу после клонирования проекта необходимо развернуть БД. Выполняем действия в командной строке:
   1.1 set FLASK_API=run.py
   1.2 flask db upgrate
 2. Запускаем на выполнение **run.py**
 3. Возможные режимы работы
   3.1 Отобразить все валюты по которым ведется история 
   
      /allcurrancy
      
   
   3.2. Отображать всю историю курсов за все время
   
      /allrates
   
   3.3. Отобрать историю с фильтром по коду валют (code) и даты с которой (date_from) хотим посмотреть историю
   
      /api/currency/history?date_from=2023-01-10&code=UAH
      
         отбирает курсы с фильтром по валюте и дате. 
      
      /api/currency/history?code=UAH
      
         отбирает курсы с фильтром по валюте за все время
      
      /api/currency/history
      
         отбирает все курсы по всей валюте за все время, по которой ведется история
      
      ОБРАТИТЕ ВНИМАНИЕ! Если в фильтре укажем валюту, по которой не ведется история отобразится курс на сегодня
      
      
