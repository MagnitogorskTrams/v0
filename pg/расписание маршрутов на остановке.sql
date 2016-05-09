/*выбираем расписание интересующих маршрутов через выбранную остановку*/
select * from stop_schedule((select id from stops where name like '%Береговая%' and direction not like '%ТЭЦ%' limit 1))
where route_name in ('7','20','22','33','6') order by "time";