#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app
from app import database
from flask import render_template, request, url_for
import os
import sys
import time

@app.route('/borraCliente', methods=['POST','GET',])
def borraCliente():
    if 'customerid' in request.form:
        customerid = request.form["customerid"]
        bSQL       = request.form["txnSQL"]
        bCommit = "bCommit" in request.form
        bFallo  = "bFallo"  in request.form
        duerme  = request.form["duerme"]
        dbr = database.delCustomer(customerid, bFallo, bSQL=='1', int(duerme), bCommit)
        return render_template('borraCliente.html', dbr=dbr)
    else:
        return render_template('borraCliente.html')
