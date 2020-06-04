from pkg_resources import resource_string
import json
import os
from docme.output_formats import OutputFormat


class JsonDocumentation(object):

    def __init__(self, options, app_name):
        self.user_options = options
        self.json = {app_name: {}}
        self.app_name = app_name
        
    def add_feature(self, feature):
        self.json[self.app_name][feature.name] = {
            'description': feature.text_description and feature.text_description,
            'scenarios': {},
        } 
        self.atual_feature = feature.name

    def add_scenario(self, scenario, fixtures):
        self.json[self.app_name][self.atual_feature]['scenarios'][scenario.name] = {
            'description': (scenario.text_description and scenario.text_description) or '',
            'fixtures': fixtures,
            'steps': {}
        }
        self.atual_scenario = scenario.name


    def add_step(self, current_path, step):
        if self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario]['steps'] == {}:
            self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario]['first_path'] = current_path
            # self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario]['dumpdata_path'] = step.dumpdata_path
        if current_path in self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario]['steps']:
            self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario]['steps'][current_path].append(
                {
                    "title": step.title,
                    "description": step.text or '',
                }
            )
        else:
            self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario]['steps'][current_path] = [{
                    "title": step.title,
                    "description": step.text or '',
                }]
        self.json[self.app_name][self.atual_feature]['scenarios'][self.atual_scenario][
            'steps'][current_path][-1]['examples'] = self.examples_list(step)

    def examples_list(self, step):
        if step.table and step.with_form_example:
            _string = "<ul>"
            for dados in step.table:
                _string += """
                                <li>
                                    Preencha o campo {} com {}
                                </li>
                                """.format(dados[step.table_label], dados[step.table_value])
            _string += "</ul>"
            return _string
        elif step.table and step.with_data_example:
            _string = "<ul>"
            for dados in step.table:
                _string += """
                                <li>
                                    {}
                                </li>
                                """.format(dados.cells[0])
            _string += "</ul>"
            return _string
        else:
            return ""

    def save(self, docs_dir):
        json_path = os.path.join(docs_dir, "doc.json")
        with open(json_path, 'w', encoding='utf8') as jp:
            json.dump(self.json, jp, indent=2)
