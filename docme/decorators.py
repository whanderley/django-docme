import os
import sys
import shutil
from django.conf import settings
from urllib.parse import urlparse
from django.core.management import call_command
from docme.html_documentation import HtmlDocumentation
from docme.json_documentation import JsonDocumentation
from functools import reduce
import inspect
import types


class EnvironmentFunctionDecorator(object):

    def __init__(self, func, options, app_name):
        self.function = func
        self.options = options
        self.app_name = app_name

    def docs_dir(self):
        return os.path.join(os.path.dirname(self.function.__globals__["__file__"]), 'docs')

    def _clear_name(self, text):
        return reduce(lambda t, param: t.replace(param, ""), [text, ":before", ":docme",
                                                              ":dumpme", ":notitle", ":vertical",
                                                              ":withformexample", ":autotour",
                                                              ":withdataexample", ":after", ":noscreenshot"])

    def text_description(self, element):
        return "<br/>".join(element.description)


class BeforeAllDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context):
        if hasattr(settings, 'AUTO_DOC') and settings.AUTO_DOC:
            shutil.rmtree(self.docs_dir(), ignore_errors=True)
            setattr(context, 'html_documentation', self.create_html_doc())
            if 'json' in self.options['output-formats']:
                setattr(context, 'json_documentation', self.create_json_doc())
            for i, feature in enumerate(context._runner.features):
                feature.docme = ":docme" in feature.name
                feature.auto_tour = ":autotour" in feature.name
                setattr(feature, 'name', self._clear_name(feature.name))
                setattr(feature, 'index', i)
                setattr(feature, 'text_description',
                        self.text_description(feature))
            context.html_documentation.add_summary(context)
        else:
            for feature in context._runner.features:
                setattr(feature, 'name', self._clear_name(feature.name))
                for scenario in feature.scenarios:
                    setattr(scenario, "name", self._clear_name(scenario.name))
                    for step in scenario.steps:
                        setattr(step, 'name', self._clear_name(step.name))
        self.function(context)

    def create_html_doc(self):
        os.makedirs(self.docs_dir(), exist_ok=True)
        return HtmlDocumentation(self.options)

    def create_json_doc(self):
        os.makedirs(self.docs_dir(), exist_ok=True)
        return JsonDocumentation(self.options, self.app_name)


class AfterAllDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context):
        context.json_documentation.save(self.docs_dir())
        context.html_documentation.save(self.docs_dir())
        self.function(context)


class BeforeFeatureDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context, feature):
        if feature.docme:
            if feature.index > 0:
                context.html_documentation.new_page()
            context.html_documentation.add_feature(feature)
        if feature.auto_tour:
            context.json_documentation.add_feature(feature)
        for i, scenario in enumerate(feature.scenarios):
            setattr(scenario, "dumpme", ":dumpme" in scenario.name)
            setattr(scenario, "before", ":before" in scenario.name)
            setattr(scenario, "docme", ":docme" in scenario.name)
            setattr(scenario, "auto_tour", ":autotour" in scenario.name)
            setattr(scenario, "name", self._clear_name(scenario.name))
            setattr(scenario, "index", i)
            setattr(scenario, 'text_description',
                    self.text_description(scenario))

        self.function(context, feature)


class AfterFeatureDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context, feature):
        self.function(context, feature)


class BeforeScenarioDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context, scenario):
        if scenario.auto_tour:
            context.json_documentation.add_scenario(scenario, context.fixtures)
            for i, step in enumerate(scenario.steps):
                setattr(step, 'auto_tour', ':autotour' in step.name)
                if i == 0:
                    setattr(step, 'dumpdata', True)
        if scenario.docme:
            if scenario.index > 0:
                context.html_documentation.new_page()
            context.html_documentation.add_scenario(scenario)
            context.html_documentation.hr()
            for i, step in enumerate(scenario.steps):
                setattr(step, 'documented_step', False)
                setattr(step, 'scenario', scenario)
                setattr(step, 'no_title', ':notitle' in step.name)
                if ':docme' in step.name:
                    setattr(step, 'vertical', ':vertical' in step.name)
                    setattr(step, 'documented_step', True)
                    setattr(step, 'with_form_example',
                            ":withformexample" in step.name)
                    setattr(step, 'with_data_example',
                            ":withdataexample" in step.name)
                    setattr(step, 'after', ":after" in step.name)
                    setattr(step, 'no_screenshot',
                            ":noscreenshot" in step.name)
                    setattr(step, 'break_page', False)
                if i == 0:
                    setattr(step, 'dump_before',
                            scenario.dumpme and scenario.before)
                setattr(step, 'dump_dir',
                        self.dump_dir(scenario))
                setattr(step, 'name', self._clear_name(step.name))
                step.title = "" if step.no_title else step.name.capitalize()

        self.function(context, scenario)

    def dump_dir(self, scenario):
        return os.path.join(self.docs_dir(),
                            scenario.feature.name,
                            scenario.name.replace(':dumpme', '')).replace(' ', '_')


class AfterScenarioDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context, scenario):
        if scenario.dumpme and not(scenario.before):
            os.makedirs(self.dump_dir(scenario), exist_ok=True)
            command = 'pg_dump -U {} -d {} > {}'.format(
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['NAME'],
                self.dump_path(scenario).replace(' ', '\ '))
            os.system(command)

        self.function(context, scenario)

    def dump_path(self, scenario):
        return os.path.join(self.dump_dir(scenario), 'dump.sql')

    def dump_dir(self, scenario):
        return os.path.join(self.docs_dir(),
                            scenario.feature.name,
                            scenario.name)


class BeforeStepDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context, step):
        if hasattr(step, "dump_before") and step.dump_before:
            os.makedirs(step.dump_dir, exist_ok=True)
            command = 'pg_dump -U {} -d {} > {}'.format(
                settings.DATABASES['default']['USER'],
                settings.DATABASES['default']['NAME'],
                self.dump_path(step).replace(' ', '\ '))
            os.system(command)
        if hasattr(step, "documented_step") and step.documented_step and step.with_form_example:
            for i, h in enumerate(step.table.headings):
                if ':label' in h:
                    step.table_label = h.replace(':label', '')
                    step.table.__dict__[
                        'headings'][i] = h.replace(':label', '')
                if ':value' in h:
                    step.table_value = h.replace(':value', '')
                    step.table.__dict__[
                        'headings'][i] = h.replace(':value', '')
        if hasattr(step, "documented_step") and step.documented_step and not step.after:
            os.makedirs(self.image_path(step), exist_ok=True)
            image_path = ''
            if not step.no_screenshot:
                image_path = context.browser.screenshot(
                    self.image_path(step))
            context.html_documentation.add_step(image_path, step, context)
            setattr(step, "documented_step", False)
        if hasattr(step, "auto_tour") and step.auto_tour:
            if urlparse(context.browser.url).query:
                path = urlparse(context.browser.url).path + \
                    "/?" + urlparse(context.browser.url).query
            else:
                path = urlparse(context.browser.url).path
            context.json_documentation.add_step(path.replace('//', '/'), step)
        self.function(context, step)

    def image_path(self, step):
        return os.path.join(step.dump_dir, 'images/')

    def dump_path(self, step):
        return os.path.join(step.dump_dir, 'dump_before.sql')

    def dumpdata_path(self, step):
        return os.path.join(self.dumpdata_dir(), "{}_{}.json".format(step.scenario.feature.index, step.scenario.index))

    def dumpdata_dir(self):
        return os.path.join(self.docs_dir(), ".dumpsdatas")


class AfterStepDecorator(EnvironmentFunctionDecorator):

    def __call__(self, context, step):
        if hasattr(step, "documented_step") and step.documented_step and step.after:
            os.makedirs(self.image_path(step), exist_ok=True)
            image_path = context.browser.screenshot(
                self.image_path(step))
            # setattr(step, 'capitalized_name', step.name.capitalize())
            context.html_documentation.add_step(image_path, step, context)
            setattr(step, "documented_step", False)
        self.function(context, step)

    def image_path(self, step):
        return os.path.join(step.dump_dir, 'images/')
