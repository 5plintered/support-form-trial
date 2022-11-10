import os
import tempfile
import re
import datetime

from config import config_items, field_value, script_cfg, types_receivers, test_receivers, setup_logger, smtp_config, unsent_path, max_unsent

from flask import current_app, Flask, Blueprint, request, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import ValidationError
from form_patch import MultipleFileField
from wtforms import StringField
from wtforms.validators import InputRequired, required
from werkzeug.utils import secure_filename
from flask_mail import Mail,Message

from smtplib import SMTPAuthenticationError

from sfcombo import SFCombo
from sfstring import SFString
from sfmultiselect import SFMultiselectCheckbox
from sfdualcombo import SFDualCombo
from sfbanner import SFBanner

api = Blueprint('api', __name__)
DEFAULT_CFG = {"MAIL_SUPPRESS_SEND": False, 
               "WTF_CSRF_ENABLED": False,
               "SECRET_KEY": "aafdsjfkldjasfklqwerewreworpiop",
               **smtp_config()}

FieldTypes = {
  'string': SFString,
  'combo': SFCombo,
  'dual_combo': SFDualCombo,
  'multiselect': SFMultiselectCheckbox,
  'banner': SFBanner
}

def create_app(cfg={}):
  global logger
  global MAIL

  app = Flask(__name__)
  app.config.update({**DEFAULT_CFG, **cfg})

  logger = setup_logger(app.logger, app.config["TESTING"])
  MAIL = Mail(app)

  app.jinja_env.lstrip_blocks = True
  app.jinja_env.trim_blocks = True

  app.register_blueprint(api)
  return app

@api.route('/', methods=['GET', 'POST'], strict_slashes=False)
def main_page():
  return get_main()

@api.route('/test', methods=['GET', 'POST'])
def main_test():
  logger.info("MAIL TESTING MODE")
  return get_main(True)

@api.route('/script.js')
def on_script():
  return render_template('script_.js', script=script_cfg())

def load_defaults(form):
  result = {}
  for fragment in form.fragments:
    FieldTypes[fragment['type']].default(form, fragment, result)
  fixed_fields = [ 'email', 'cc', 'date', 'subject' ]
  for field in fixed_fields:
    result[field] = request.form.get(field) or request.args.get(field) or ''
  if result['email'] == 'username':
    result['email'] = ''
  return result

def get_main(mail_testing=False):
  email_message = ()
  try :
    form = createSupportForm()
    if not form.validate_on_submit():
      return render_template(
        'form.html',         
        defaults=load_defaults(form),
        form=form,
        test=current_app.config["TESTING"] or mail_testing
      )
    email_message = compose_email(mail_testing)
    if not current_app.config["TESTING"]:
      send_support_email(*email_message)
    return success(form)
  except (SMTPAuthenticationError, ConnectionRefusedError) as e:
    logger.exception("Failed to send email")
    try_save_failed(email_message)
    return failed()
  except:
    logger.exception("Exception")
    try_save_failed(email_message)
    return failed()

def success(form):
  return render_template('sent.html', 
    css_url = url_for('static', filename='style.css'),
    urgency = request.form.get('urgency'),
    email = request.form.get('email'))

def failed():
  return render_template('failed.html', 
    css_url=url_for('static', filename='style.css'))

def set_defaults(formdata, key):
  v = formdata.get(key)
  if not v:
    value = config_items('fields')[key]['default_option']
    formdata[key] = value

def compose_email(mail_testing):
  formdata = request.form.copy()
  # Actually, we don't want to do this - if the user can't be bothered entering a Type, then we will fail with good reason.
  #set_defaults(formdata, 'type')
  sender = email_from_user(formdata.get('email'))
  to,cc = get_mail_recipients(formdata, mail_testing)
  subject = formdata.get('subject')
  vis_class = field_value('type', formdata.get('type'), 'vis_class')

  values = []
  for field, field_items in config_items('fields').items():
    FieldTypes[field_items['template']].value(values, vis_class, formdata, field, field_items)

  message = render_template("email.txt",
    product = field_value('type', formdata.get('type'), 'name'),
    date = formdata.get('date'),
    values = values)

  attachments = []
  for k in request.files.keys():
    v = request.files.getlist(k)
    if v and len(v) > 0:
      attachments = attachments + v

  return (sender, to, cc, subject, message, attachments)

def email_from_user(user):
  if (user.find("@") != -1):
    return user.replace("@dugeo.com", "@dug.com")
  return user + "@dug.com"

def emails_from_liststr(liststr):
  if not liststr:
    return []
  #Convert all @dugeo.com to @dug.com, so that we don't get multi-domain errors.
  users = re.split("[,;/\s|\\\\]+", liststr.replace("@dugeo.com", "@dug.com"))  
  return list(map(email_from_user, users))

def matching_condition(formdata, conditions):
  for k,v in conditions.items():
    fd_state = formdata.get(k)
    if v != fd_state:
      return False
  return True

def get_additional_recipients(formdata):
  result = []
  for k,v in config_items('additional_recipients').items():
    if matching_condition(formdata, v.get('conditions')):
      result = result + v.get('to');
  return result

def get_mail_recipients(formdata, mail_testing):
  if mail_testing:
    return test_receivers()
  to, cc = types_receivers(formdata.get('type'))
  return (to + get_additional_recipients(formdata), cc + emails_from_liststr(formdata.get('cc')) + [email_from_user(formdata.get('email'))])

def send_support_email(sender, to, cc, subject, message, attachments):
  msg = Message(sender=sender, recipients=to, cc=cc, subject=subject, body=message)

  #upload and attach files
  with tempfile.TemporaryDirectory() as temp_dir:
    for f in attachments:
      if not f:
        continue

      upload_path = os.path.join(temp_dir, secure_filename(f.filename))
      f.save(upload_path)

      with current_app.open_resource(upload_path) as fp:
        msg.attach(os.path.basename(upload_path), f.mimetype, fp.read())

  MAIL.send(msg)
  submitted_from = request.headers.get('X-Forwarded-For', request.remote_addr),
  logger.info("Sent message from %s to %s, subject: '%s', submitted from: %s", sender, to, subject, submitted_from)

def is_path_check(form, field):
  field.flags.not_full_path = False
  if field.data and "/" not in field.data:
    field.flags.not_full_path = True
    raise ValidationError(field.data + " is not a full workflow path")

def email_check(form, field):
  field.flags.has_yongzhong = False
  if field.data and "yongzhong" in field.data.lower():
    field.flags.has_yongzhong = True
    raise ValidationError("CC to Yongzhong")

def try_save_failed(email_message):
  if not email_message:
    return

  try:
    (sender, to, cc, subject, message, attachments) = email_message

    path = unsent_path()
    if not os.path.isdir(path):
      os.mkdir(path)
    filename = "%s.msg" % int(datetime.datetime.now().timestamp())
    full_path = os.path.join(path, filename)
    with open(full_path, "w") as f:
      f.write("from: %s\n" % sender)
      f.write("to: %s\n" % to)
      f.write("cc: %s\n" % cc)
      f.write("subject: %s\n\n" % subject)
      f.write("message: %s\n\n" % message)
    unsent = os.listdir(path)
    if len(unsent) > max_unsent():
      unsent.sort(reverse=False)
      os.remove(os.path.join(path, unsent[0]))

  except Exception:
    logger.exception("Failed to save message")


# Configurable fields we want added dynamically
def createSupportForm():
    class F(SupportForm):
      pass

    # Although the CGI will launch a new instance each time, if run from the script we need do this only once.
    if (len(F.fragments) != 0):
      F.fragments = []

    for field, field_items in config_items('fields').items():
      FieldTypes[field_items['template']].build(F, field, field_items)

    return F()

class SupportForm(FlaskForm):
  email = StringField('email',validators=[required()])
  date = StringField('date')
  cc = StringField('cc', validators=[email_check])
  subject = StringField('subject',validators=[required()])
  attachments = MultipleFileField('Attachment')
  fragments = []
  script = script_cfg()

if __name__ == "__main__":
  app = create_app()
  app.run(debug=True)
