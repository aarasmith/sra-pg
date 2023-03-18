#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 18:02:40 2022

@author: andara
"""
import psycopg2

def get_connection(search_path, credentials):
    
    return psycopg2.connect(
            host=credentials['host'],
            database=credentials['database'],
            user=credentials['username'],
            password=credentials['password'],
            port=credentials['port'],
            options=f"-c search_path={search_path}"
        )

