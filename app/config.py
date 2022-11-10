import yaml
import logging
from logging.handlers import RotatingFileHandler
import os

def config_items(key):
  return CONFIG_DATA[key]

def script_cfg():
  result = CONFIG_DATA['script'];
  # Insert expected values
  options = config_items('fields')['module']['options']
  result['expected_types'] = {k:v['expect'] for k,v in options.items()}
  return result

def field_value(field_name, key, value):
  options = config_items('fields')[field_name]['options']
  if isinstance(options, dict):
    return options[key][value]
  if value == 'name':
    return key
  return None

def types_receivers(ticket_type):
  if not ticket_type:
    return ['support@dug.com'], []
  values = config_items('fields')['type']['options'].get(ticket_type)
  return values['to'], values['cc']

def unsent_path():
  return full_path(CONFIG_DATA['logging']['unsent_path'])

def max_unsent():
  return CONFIG_DATA['logging']['max_unsent']

def setup_logger(logger, unit_testing):
  if not unit_testing:
    log_config = CONFIG_DATA['logging']
    handler = RotatingFileHandler(
      full_path(log_config['path']), 
      maxBytes=log_config['max_log_size_mb']*1024*1024, 
      backupCount=log_config['max_log_files'])
    
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

  logger.info("Started logging")

  if unit_testing:
    logger.info("UNIT TESTING MODE, WONT SEND EMAILS")

  return logger

def smtp_config():
  return CONFIG_DATA['smtp']

def test_receivers():
  test = CONFIG_DATA['test']
  return (test['to'], test['cc'])

def full_path(rel_or_abs_path):
  if os.path.isabs(rel_or_abs_path):
    return rel_or_abs_path
  return os.path.join(os.path.dirname(__file__), rel_or_abs_path)

def reload():
  global CONFIG_DATA
  
  with open(full_path("config.yaml"), "r") as f:
    CONFIG_DATA = yaml.load(f)

reload()
