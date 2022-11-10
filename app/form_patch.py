from wtforms.widgets import Input
from wtforms.fields.core import Field

#from https://github.com/lepture/flask-wtf/issues/276, will be included in next flask-wtf release
class FileInput(Input):
  """Render a file chooser input.
  :param multiple: allow choosing multiple files
  """

  input_type = 'file'

  def __init__(self, multiple=False):
    super(FileInput, self).__init__()
    self.multiple = multiple

  def __call__(self, field, **kwargs):
    # browser ignores value of file input for security
    kwargs['value'] = False

    if self.multiple:
        kwargs['multiple'] = True

    return super(FileInput, self).__call__(field, **kwargs)


class FileField(Field):
  """Renders a file upload field.
  By default, the value will be the filename sent in the form data.
  WTForms **does not** deal with frameworks' file handling capabilities.
  A WTForms extension for a framework may replace the filename value
  with an object representing the uploaded data.
  """

  widget = FileInput()

  def _value(self):
    # browser ignores value of file input for security
    return False


class MultipleFileField(FileField):
  """A :class:`FileField` that allows choosing multiple files."""

  widget = FileInput(multiple=True)

  def process_formdata(self, valuelist):
    self.data = valuelist
