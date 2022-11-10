
class SFBanner:
    def value(values, vis_class, formdata, field, field_items):
        # There is no email, so nothing to do.
        return

    def build(form, key, config):
        enabled_classes = config.get('enabled_for')
        form.fragments.append({
            'key': key,
            'type': 'banner',
            'template': 'banner_.html',
            'enabled_classes': enabled_classes,
            'required_condition': config.get('required_condition'),
            'href': config.get('href')
        })        

    def default(form, fragment, result):
        # There is no value to persist, so nothing to do.
        return