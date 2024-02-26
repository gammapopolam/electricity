# Визуализация электрических сетей

Набор функций, осуществляющих поиск параллельных линий в сети и их параллельный сдвиг с сохранением топологических отношений исходной сети.
Для улучшения производительности реализован простой пространственный индекс, основанный на буферных зонах сегментов сети.

## Input
Электрическая сеть (желательно) в формате GeoJSON. Каждая электросеть должна иметь поле id. Данные должны быть спроецированы в прямоугольные координаты.

## Output
To be filled...

## TODO:
- Параметры поиска параллельных линий на основе заданного масштаба
- Параметр сдвига параллельных линий на основе заданного масштаба
- Исправление багов в поиске параллельных линий
- Добавление тестов 