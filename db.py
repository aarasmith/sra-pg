#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 18:02:40 2022

@author: andara
"""
import psycopg2
import configparser

def get_connection(search_path, config_file = "connection.config"):
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    config_tag = 'DEFAULT'
    
    return psycopg2.connect(
            host=config[config_tag]['PG_HOST'],
            database=config[config_tag]['PG_DATABASE'],
            user=config[config_tag]['PG_USER'],
            password=config[config_tag]['PG_PASSWORD'],
            port=config[config_tag]['PG_PORT'],
            options=f"-c search_path={search_path}"
        )

