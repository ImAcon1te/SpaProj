SPA приложение
Back-end - Python DRF
Front-end - Vue.js
БД - sqlite3
запуск docker-compose.yml 
```
docker-compose up --build 
```
адрес фронта после запуска докер контейнеров - http://localhost:8080
сервер на порте 8000

Функционал:
1. добавление комментариев
2. загрузка изображений формата JPG, GIF, PNG (валидация и на Frontend и на Backend) или текстового файла .txt
2.1 изображения будут уменьшены до 320х240 пикселей если его размер больше
2.2 текстовые файлы более 100кб не будут приниматься
3. капча генерируется на сервере, проверяется отдельным запросом
4. при отображении комментария содержимое и название текстового файла (если он был добавлен) будет отображаться на странице, изображения (если были добавлены) отображаться без названия
5. к каждому комментарию можно добавить сколько угодно ответов (других комментариев) которые тоже могут иметь собственные ответы
6. в тексте комментария можно использовать следующие теги - a code i strong.
7. Присутствует валидация на Frontend стороне, другие теги будут удалены, если не все теги будут закрыты валидация не даст сохранить комментарий
8. возможность создать аккаунт и авторизоваться
8.1 если пользователь авторизован при добавлении комментария значения username и email подставляются автоматически и используется аватар пользователя при отображении комментария
   
Минусы:
1. не сделана сортировка LIFO. Для реализации нужно описать стек, из-за болезни не успел это сделать и реализовывал древовидную структуру данных комментариев 
2. не сделана защита от XSS атак и SQL – инъекций. CSRF защита включена в DRF.
3. нет сортировки по полям и пагинации. 
4. нет хостинга
