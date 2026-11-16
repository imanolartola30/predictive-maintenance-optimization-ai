-- Average days since last failure by machine model and age
select machine_model, machine_age, avg(days_since_last_failure) as avg_days_since_last_failure from (
select m.age as machine_age, m.model as machine_model, 
julianday(f.datetime) - julianday(lag(f.datetime) over (partition by f.machineID order by f.datetime)) as days_since_last_failure
from (select distinct machineID, datetime from failures) as f
inner join machines as m on f.machineID = m.machineID)
group by machine_age, machine_model
order by machine_model, machine_age asc;


-- Averages and standard deviations of properties (voltage, rotation, pressure and vibration) in the previous 24h of each failure
select f.failure, avg(t.volt) as avg_voltage, sqrt(avg(t.volt*t.volt) - avg(t.volt)*avg(t.volt)) as stddev_voltage,
avg(t.rotate) as avg_rotation, sqrt(avg(t.rotate*t.rotate) - avg(t.rotate)*avg(t.rotate)) as stddev_rotation,
avg(t.pressure) as avg_pressure, sqrt(avg(t.pressure*t.pressure) - avg(t.pressure)*avg(t.pressure)) as stddev_pressure,
avg(t.vibration) as avg_vibration, sqrt(avg(t.vibration*t.vibration) - avg(t.vibration)*avg(t.vibration)) as stddev_vibration
from failures as f
inner join telemetry as t on f.machineID = t.machineID
where t.datetime >= datetime(f.datetime, '-24 hours') and t.datetime <= f.datetime
group by f.failure;

-- Averages and standard deviations of properties (voltage, rotation, pressure and vibration) for all telemetry data, to compare with the results above.
select avg(volt) as avg_voltage, sqrt(avg(volt*volt) - avg(volt)*avg(volt)) as stddev_voltage,
avg(rotate) as avg_rotation, sqrt(avg(rotate*rotate) - avg(rotate)*avg(rotate)) as stddev_rotation,
avg(pressure) as avg_pressure, sqrt(avg(pressure*pressure) - avg(pressure)*avg(pressure)) as stddev_pressure,
avg(vibration) as avg_vibration, sqrt(avg(vibration*vibration) - avg(vibration)*avg(vibration)) as stddev_vibration
from telemetry;

-- Percentage of times there is an error and has a failure in less than 48h
select e.errorID, count(*) as total_errors,
  sum(exists (select 1 from failures f where f.machineID = e.machineID
      and f.datetime > e.datetime and f.datetime <= datetime(e.datetime, '+48 hours'))) as followed_by_failure,
  round(100.0 * sum(exists (select 1 from failures f where f.machineID = e.machineID
      and f.datetime > e.datetime and f.datetime <= datetime(e.datetime, '+48 hours'))) / count(*), 2) as pct
from errors e group by e.errorID;