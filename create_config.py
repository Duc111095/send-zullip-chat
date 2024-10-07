import configparser

config = configparser.ConfigParser()

config['datasource'] = {'server': '192.168.100.53\\sql2014',
                        'database': 'MinhAn_App',
                        'username': 'sa',
                        'password': '123456a@@'}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
