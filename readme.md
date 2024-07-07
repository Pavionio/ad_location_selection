# Подбор локаций для размещения рекламы

## Задача

На основе данных по уже проведенным
рекламным кампаниям (далее - адресные
программы, АП) содержащих в себе данные по
охвата по каждой отдельной поверхности и охвата
по нескольким поверхностям в совокупности, с
применением технологий машинного обучения,
создать инструмент, позволяющий
прогнозировать на заданное количество точек
максимально эффективный вариант их
расположения по локациям города, для получения
максимального показателя охвата

## Решение

Веб-интерфейс с картой города, разбитого на сектора (полигоны), в котором для заданного
количества точек и секторов выбираются точки, позволяющие
обеспечить максимальный охват

## Структура

[/models](https://github.com/Pavionio/ad_location_selection/tree/main/models) - все модели которые используются в программе или для сабмита    
[/preprocessing](https://github.com/Pavionio/ad_location_selection/tree/main/preprocessing) - здесь хранятся различные файлы для предобработки данных   
[/map](https://github.com/Pavionio/ad_location_selection/tree/main/map) - сайт с картой и интерфейсом

## Как запустить?

1. Создать виртуальную среду 

`python venv -m venv`

2. Активировать виртульную среду

`venv\Scripts\activate`

3. Установить зависимости

`pip install -r requirements.txt`

4. Скачать веса модели и по [ссылке](https://drive.google.com/file/d/1Z27Us179j-gzMEx9IuFItxn_3GpIba50/view?usp=sharing)
и поместить в каталог с исполняемым файлом(run.py)

5. Запустить сервер

`python run.py`

## Как пользоваться?
При попадании на сайт можно выбрать любой из доступных видов визуализации геоданных: обычная карта, heatmap и полигоны.

Для любой из карт следует задать параметры вашей целевой аудитории: ориентировочную возрастную группу (в годах), уровень дохода и пол.

При использовании обычной карты также нужно выбрать количество рекомендуемых меток и нажать “Предсказать”. Если данные введены корректно, то на карте можно будет наблюдать предложенные точки. И при нажатии на любую из точек будет выведена информация про ее расположение (ширина и долгота), а также предположительное значение охвата.

При использовании heatmap будет показана карта плотности распределения точек охвата.

При использовании полигонов можно выбрать интересующие части города и получить предсказания внутри выбранных мест. А также можно добавлять собственный полигон любого размера. 

Во вкладке файл можно загрузить данные в формате json о прошедших рекламных компаниях (со значением охвата или без) для последующего отображения 

## Ссылки

Архив с программой - https://disk.yandex.ru/d/PDrmD3VLThSvGQ   
Скринкаст -   
Веса моделей можно найти в файле [models.md](https://github.com/Pavionio/ad_location_selection/blob/main/models/models.md)
