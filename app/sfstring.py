from supportfield import SupportField
from wtforms import StringField
from wtforms.widgets import TextArea
from flask import request

class SFString:
  def value(values, vis_class, formdata, field, field_items):
    if SupportField.is_valid(formdata, field):
      SupportField.add_value(formdata[field], values, vis_class, formdata, field, field_items)

  def build(form, key, config):
    optional = config.get('optional', False)
    classes = 'required' if not optional else ''
    enabled_classes = config.get('enabled_for')
    if enabled_classes:
      classes += ' ';
      classes += enabled_classes
    cols = config.get('cols')
    if cols is None:
      setattr(form, key, StringField(key))
    else:
      setattr(form, key, StringField(key, widget=TextArea()))
    form.fragments.append({
      'key': key,
      'type': 'string',
      'template': 'string_.html',
      'caption': config.get('caption'),
      'compulsory': not optional,
      'enabled_classes': enabled_classes,
      'classes': classes,
      'optional': optional,
      'required_condition': config.get('required_condition'),
      'invalid': config.get('invalid'),
      'placeholder': config.get('placeholder'),
      'rows': config.get('rows'),
      'cols': cols
    })

  def default(form, fragment, result):
    key = fragment['key']
    value = request.form.get(key) or request.args.get(key) or None    
    if value is None:
      return
    form[key].default = value
    form.process()

