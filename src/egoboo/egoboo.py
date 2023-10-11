from jinja2 import Environment, FileSystemLoader
import shutil
import os
import glob
import markdown
import codecs
from egoboo.store import Store, Base
import oyaml as yaml
import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase



class Site:
  env = None
  blah = None
  db = None
  config = None
  sections = {}

  def __init__(self, template_loader_path):
    self.blah = "blah"
    self.env = Environment(
      loader=FileSystemLoader(template_loader_path),
      trim_blocks=True,
      lstrip_blocks=True)
    

    persist_engine = create_engine('sqlite:///persist.db', echo=True)

    # create sql database if it doesn't exist
    Base.metadata.create_all(persist_engine)

    Session = sessionmaker(bind=persist_engine)
    self.db = Session()

    self.initialize_configs()
    print(self.config)


  def initialize_configs(self):
    if not os.path.exists("config.yaml"):
      shutil.copy("config.default.yaml", "config.yaml")

    # read site configurations
    with open("config.yaml", 'r') as stream:
      try:
        self.config = yaml.load(stream, Loader=yaml.FullLoader)
      except yaml.YAMLError as exc:
        print(exc)

  def generate_all(self):
    for key, section in self.sections.items():
      print("\nGenerating files for %s section..." % key)
      section.generate_output(self.config, self.db, self.sections)

  def copy_static(self, project_path, output_path):
    for filename in glob.glob(os.path.join(project_path, "*.*")):
      shutil.copy(filename, output_path)


class SiteSection:
  env = None
  dist_folder = ""
  template_name = ""
  template = None
  resources = {}
  def __init__(self, env, dist_folder, template):
    self.env = env
    self.dist_folder = dist_folder
    self.template = self.env.get_template(template)
    self.template_name = template
    self.resources = {}

  def generate_output(self, config, db, sections):
    os.makedirs(self.dist_folder, exist_ok=True)
    if len(self.resources) > 0:
      for page_key, page in self.resources.items():
        rendered_output = self.template.render(self.get_template_arguments(config, db, sections, page))
        output_filename = self.dist_folder + self.get_output_name(page)
        print("Generating %s..." % output_filename )

        with open(output_filename, "w") as fh:
          fh.write(rendered_output)
    else:
      rendered_output = self.template.render(self.get_template_arguments(config, db, sections, {}))
      output_filename = self.dist_folder + self.get_template_output_name()
      print("Generating %s..." % output_filename )

      with open(output_filename, "w") as fh:
        fh.write(rendered_output)


  def import_markdown(self, import_path):
    markdown_data = {}
    md = markdown.Markdown(extensions=['meta'])

    types = ['*.md', '*.md.jinja2']
    for extension in types:
      for filename in glob.glob(os.path.join(import_path, extension)):
        with codecs.open(filename, 'rb', "utf-8") as stream:
          md.reset()
          temprecord = {}
          
          temprecord['filename'] = filename
          temprecord['content'] = stream.read()

          # preprocess page through jinja if it has jinja2 extension
          temprecord['html'] = md.convert(temprecord['content'])
          if 'jinja2' in filename:
            page = self.env.from_string(temprecord['html'])
            temprecord['html'] = page.render()

          temprecord['meta'] = md.Meta

          if 'date' in md.Meta:
            tempdatestring = md.Meta['date'][0]
            if ':' not in tempdatestring:
              tempdatestring = tempdatestring + " 00:00:00"
            temprecord['dt'] = datetime.datetime.strptime(tempdatestring, "%Y-%m-%d %H:%M:%S")

          temprecord['link'] = self.generate_link(temprecord)

          # slug becomes the key in the array
          temprecord['output_filename'] = "%s.html" % md.Meta['slug'][0]
          self.resources[md.Meta['slug'][0]] = temprecord


  @staticmethod
  def get_template_arguments(config, db, sections, page):
    return {}

  @staticmethod
  def get_output_name(resource):
    return "%s" % resource['output_filename']

  def get_template_output_name(self):
    return "%s" % self.template_name.replace('.jinja2','')

  @staticmethod
  def get_link(resource):
    return "/%s" % resource['meta']['slug'][0]
