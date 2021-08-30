from pkg_resources import resource_string
import base64
from jinja2 import Template as JinjaTemplate
from string import Template
import os
from docme.output_formats import OutputFormat
from bs4 import BeautifulSoup

class HtmlDocumentation(object):

    def __init__(self, options):
        self.user_options = options
        self.string = """
            <html>
                <head>
                    <meta charset="utf-8"/>
                    <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
                    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
        """
        self.string += "css_path" in options and "<link rel = 'stylesheet' type=text/css href = '{}'  >".format(options["css_path"]) or " "
        self.string += """        
                </head>
                <body>
                <div class="container">
        """
    
    def ln(self):
        self.string += "<br/>"

    def hr(self):
        self.string += "<hr/>"

    def add_feature(self, feature):
        if "feature_html" in self.user_options:
            feature_string = open(
                self.user_options['feature_html'], "r").read()
        else:
            feature_string = resource_string(
                "docme", "assets/feature.html").decode('utf-8')
        t = Template(feature_string)
        self.string += t.substitute(
            feature_title=feature.name,
            feature_id="feature{}".format(feature.index),
            feature_keyword=feature.keyword,
            feature_description=((feature.text_description and feature.text_description) or ' ')
        )
 
    def add_scenario(self, scenario):
        if "scenario_html" in self.user_options:
            scenario_string = open(
                self.user_options['scenario_html'], "r").read()
        else:
            scenario_string = resource_string(
                "docme", "assets/scenario.html").decode('utf-8')
        t = Template(scenario_string)
        self.string += t.substitute(
            scenario_title = scenario.name,
            scenario_id = "scenario{}_feature{}".format(scenario.index, scenario.feature.index),
            scenario_keyword = scenario.keyword,
            scenario_description = ((scenario.text_description and scenario.text_description) or ' ')
        )
    def add_summary(self, context):
        feature_count = 1
        self.string += "<dl>"
        for feature in [feature for feature in context._runner.features if feature.docme]:
            self.string += """<dt><a href="#feature{}" target="_self">
                                {} - {} 
                            </a></dt>
                        """.format(feature.index, feature_count, feature.name)
            scenario_count = 1
            for i, scenario in enumerate([scenario for scenario in feature.scenarios if ":docme" in scenario.name]):
                self.string += """<dd><a href="#scenario{}_feature{}" target="_self">
                                {}.{} - {} 
                            </a></dd>
                        """.format(i, scenario.feature.index, feature_count, scenario_count,
                                scenario.name.replace(":docme", ""))
                scenario_count += 1
            feature_count += 1
        self.string += "</dl>"


    def add_examples_list(self, context):
        if context.table:
            self.string += "<ul>"
            for dado in context.table:
                self.string += """
                                <li>
                                    Preencha o campo {} com {}
                                </li>
                                """.format(dado['campo'], dado['valor'])
            self.string += "</ul>"

    def new_page(self):
        if not(self.string.endswith("<p class=new_page></p>")):
            self.string += "<p class=new_page></p>"

    def add_step(self, image_path, step, context):
        if step.no_screenshot:
            step_string = resource_string(
                "docme", "assets/noscreenshot_step.html").decode('utf-8')
            t = JinjaTemplate(step_string)
            step_string = t.render(step=step)
            atual_string = BeautifulSoup(self.string, 'html.parser')
            atual_string.find_all(
                class_="align-middle")[-1].append(BeautifulSoup(step_string, 'html.parser'))
            self.string = str(atual_string)
        else:
            if step.vertical:
                if "step_vertical_html" in self.user_options:
                    step_string = open(self.user_options['step_vertical_html'], "r").read()
                else:
                    step_string = resource_string(
                    "docme", "assets/step_vertical.html").decode('utf-8')
            else:
                if "step_horizontal_html" in self.user_options:
                    step_string = open(
                        self.user_options['step_horizontal_html'], "r").read()
                else:
                    step_string = resource_string(
                        "docme", "assets/step_horizontal.html").decode('utf-8')
            t = JinjaTemplate(step_string)
            base64_image = 'data:image/jpeg;base64,' +  base64.b64encode(open(image_path, 'rb').read()).decode()
            self.string += t.render(step_screenshot_base64=base64_image,
                                    step=step,
                                )

    def save(self, docs_dir):
        if "css_file" in self.user_options:
            css_string = open(self.user_options['css_file'], "r").read()
        else:
            css_string = resource_string(
                "docme", "assets/docme.css").decode('utf-8')
        self.string += """
                </body>
            </html>
            <style>
                @media print {
                    .row.step {
                        page-break-before: auto; /* 'always,' 'avoid,' 'left,' 'inherit,' or 'right' */
                        page-break-after: auto; /* 'always,' 'avoid,' 'left,' 'inherit,' or 'right' */
                        page-break-inside: avoid; /* or 'auto' */
                    }
                    p.new_page {
                        clear: both;
                        page-break-after: always;
                    }
                }
             """ + css_string + "</style>"
        output_formats = self.user_options["output-formats"] if "output-formats" in\
                             self.user_options else ['pdf']
        OutputFormat.save(self.string, output_formats, docs_dir)
           
    # def _noscheenshot_step_string(self, step):
