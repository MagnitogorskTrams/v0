--разница времени между соседними трамваями на остановке (141 - пл.Мира 
в сторону пл.Мира)
SELECT route_name, "time"
, (select "time" from stop_schedule(141, true) where "time"> m.time 
order by "time" limit 1)-"time"
FROM stop_schedule(141, true) m order by "time";
