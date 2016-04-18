/*
попытка восстановить маршрут по первому времени прохождения через остановки
только будние дни и без учета модификаций маршрута
*/
SELECT st.name, min(sch."time") as t 
FROM schedules sch INNER JOIN routes r ON r.id = sch.route_id
INNER JOIN stops st ON st.id = sch.stop_id
WHERE r.name = '1' and workday = true
group by st.name order by t;
