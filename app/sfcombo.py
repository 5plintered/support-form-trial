from supportfield import SupportField
from wtforms import SelectField
from flask import request
from wtforms.validators import InputRequired, required

class SFCombo:
  def value(values, vis_class, formdata, field, field_items):
    if not SupportField.is_valid(formdata, field):
      return
    value = formdata[field]
    if isinstance(field_items['options'], dict):
      key = value
      value = field_items['options'][key]['name']
    SupportField.add_value(value, values, vis_class, formdata, field, field_items)

  def build(form, key, config):
    optional = config.get('optional', False)
    classes = 'required' if not optional else ''
    names, descriptions = SupportField.combo_options(config, 'options')
    enabled_classes = config.get('enabled_for')
    attributes = {}
    if config.get('compulsory', False):
      attributes['required'] = ''
    setattr(form, key, SelectField(choices=SupportField.combo_list(names), render_kw=attributes))
    form.fragments.append({ 
      'key': key,
      'type': 'combo',
      'template': 'combo_.html',
      'caption': config.get('caption'),
      'compulsory': not optional,
      'enabled_classes': enabled_classes,
      'classes': classes,
      'names': names,
      'descriptions': descriptions
    })

  def default(form, fragment, result):
    key = fragment['key']
    value = request.form.get(key) or request.args.get(key) or None    
    if value is None:
      return
    form[key].default = value
    form.process()

