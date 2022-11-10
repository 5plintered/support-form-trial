from supportfield import SupportField
from wtforms import SelectField
from flask import request

class SFDualCombo:
  def value(values, vis_class, formdata, field, field_items):
    f1 = field + '1'
    f2 = field + '2'
    if not SupportField.is_valid(formdata, f1) and not SupportField.is_valid(formdata, f2):
      return
    value = ''
    if SupportField.is_valid(formdata, f1):
      if isinstance(field_items['options1'], dict):
        key = value
        value = field_items['options1'][key]['name']
      else:
        value = formdata[f1]
    if SupportField.is_valid(formdata, f2):
      if value:
        value += ' '
      if isinstance(field_items['options2'], dict):
        key = value
        value += field_items['options2'][key]['name']
      else:
        value += formdata[f2]
    SupportField.add_value(value, values, vis_class, formdata, field, field_items)

  # A field consisting of two combos
  def build(form, key, config):
    optional = config.get('optional', False)
    classes = 'required' if not optional else ''
    names1, descriptions1 = SupportField.combo_options(config, 'options1')
    names2, descriptions2 = SupportField.combo_options(config, 'options2')
    enabled_classes = config.get('enabled_for')
    key1 = key + '1'
    key2 = key + '2'
    setattr(form, key1, SelectField(choices=SupportField.combo_list(names1)))
    setattr(form, key2, SelectField(choices=SupportField.combo_list(names2)))
    form.fragments.append({ 
      'key': key,
      'type': 'dual_combo',
      'key1': key1,
      'key2': key2,
      'template': 'dual_combo_.html',
      'caption': config.get('caption'),
      'compulsory': not optional,
      'enabled_classes': enabled_classes,
      'classes': classes,
      'names1': names1,
      'descriptions1': descriptions1,
      'names2': names2,
      'descriptions2': descriptions2
    })

  def default(form, fragment, result):
    keys = [ 'key1', 'key2' ]
    for k in keys:
      key = fragment[k]
      result[key] = request.form.get(key) or request.args.get(key) or None
      value = request.form.get(key) or request.args.get(key) or None    
      if value is None:
        return
      form[key].default = value
      form.process()
