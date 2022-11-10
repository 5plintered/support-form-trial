# Common methods for fields

class SupportField:
  def combo_options(config, options_key):
    if isinstance(config[options_key], dict):
      options = config[options_key].items()
      return SupportField.kv_list(options, 'name'), SupportField.kv_list(options, 'description')
    return config[options_key], None

  def combo_list(li):
    if isinstance(li, dict):
      return [('','Select')] + [(k,v) for k,v in li.items()]
    return [('','Select')] + [(v,v) for v in li]

  def kv_list(items, value_key):
    for k,v in items:
      if not value_key in v:
        return None  
    return {k:v[value_key] for k,v in items}

  def add_value(value, values, vis_class, formdata, field, field_items):
    if 'enabled_for' in field_items and field_items['enabled_for'] != 'vis_all' and not vis_class in field_items['enabled_for']:
      return
    prefix = field_items.get('prefix', '')
    suffix = field_items.get('suffix', '')
    result = prefix + value + suffix
    values.append(result)

  def is_valid(list, key):
    return key in list and list[key]

