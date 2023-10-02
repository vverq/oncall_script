**Для запуска приложения необходимо:**
1. установить все пакеты из requirements.txt
2. поднять oncall
3. запустить сам скрипт:

   `usage: main.py [-h] [-u USERNAME] [-p PASSWORD] [-o ONCALL]`

     options:

      `-h, --help  `          справка

     ` -u USERNAME, --username USERNAME`
                             имя пользователя для логина в oncall

     ` -p PASSWORD, --password PASSWORD`
                             пароль для логина в oncall

      `-o ONCALL, --oncall ONCALL`
                            урл, на котором поднять oncall, по умолчанию http://127.0.0.1:8080
`