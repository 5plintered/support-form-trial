from supportfield import SupportField
from wtforms import BooleanField
from flask import request

class SFMultiselectCheckbox:
  # Multiselect could use SelectMultipleField, but for smaller lists should simply use checkboxes.
  def value(values, vis_class, formdata, field, field_items):
    names, descriptions = SupportField.combo_options(field_items, 'options')
    checked = []
    for name in field_items['options']:
      cbkey = field + "_" + name
      if formdata.get(cbkey, False):
        checked.append(name)
    if len(checked) == 0:
      return
    value = ", ".join(checked)
    SupportField.add_value(value, values, vis_class, formdata, field, field_items)

  def build(form, key, config):
    optional = config.get('optional', False)
    classes = 'any_required' if not optional else ''

    entries = []
    options = config.get('options')
    if isinstance(options, dict):
      for option_key, option in options.items():
        entries.append({ 
          'key': key + "_" + option_key,
          'name': option.get('name')
          })
    else:
      for option in options:
        entries.append({
          'key': key + "_" + option,
          'name': option
          })

    enabled_classes = config.get('enabled_for')
    for entry in entries:
      setattr(form, entry.get('key'), BooleanField())

    form.fragments.append({ 
      'key': key,
      'type': 'multiselect',
      'entries': entries,
      'template': 'checkbox_multiselect_.html',
      'columns': config.get('columns'),
      'caption': config.get('caption'),
      'compulsory': not optional,
      'enabled_classes': enabled_classes,
      'classes': classes
    })

  def default(form, fragment, result):
    for entry in fragment['entries']:
      key = entry.get('key')
      value = request.form.get(key) or request.args.get(key) or None
      form[key].default = value
      form.process()

