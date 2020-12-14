#!bin/#!/usr/bin/env bash
export PGPASSWORD=alumnodb
dropdb -U alumnodb si1
createdb -U alumnodb si1
psql -U alumnodb si1 < dump_v1.2-P3.sql
psql -U alumnodb si1 < actualiza.sql
psql -U alumnodb si1 < setPrice.sql
psql -U alumnodb si1 < getTopMonths.sql
psql -U alumnodb si1 < getTopVentas.sql
psql -U alumnodb si1 < setOrderAmount.sql
psql -U alumnodb si1 < updOrders.sql
psql -U alumnodb si1 < updInventory.sql
exit
