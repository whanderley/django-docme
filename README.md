# Django-docme

Django-docme is a python library to generate user documentation automatically. For that it uses the behavior tests written with Behave.

# Basic usage
On environment.py, write like this:
```python
#imports
from docme import docme

#Hooks definitions like: before_all, after_scenario, etc.

options = {"output-formats": ["pdf"]}
docme.auto_doc(locals(), "App name", options)
```

The options variable provides the configuration parameters for generating the documentation. Possible parameters are:

* output-formats -> provide output documentation formats. Available formats are: 'pdf', 'html' e 'json'.
* step_vertical_html -> path to custom html file to document vertical formatted steps. This is optional.
* step_horizontal_html -> path to custom html file to document horizontal formatted steps. This is optional.
* css_file -> path to custom css file to customize the documentation style. This is optional.

# Marks on features files
 To guide the documentation process, it is necessary to create markups in the files that describe the features.
 The markings are added to the names of the features, scenarios and steps as shown below:
 ```
 Feature: showing off behave:docme
  Feature descripton

  Scenario: run a simple test:docme
     Scenario description
     Given we have behave installed:docme:vertical
     """
        Text that describes what the step does.
     """
     When we implement a test
     Then behave will test it for us!:docme
 ```
 The possible markings are:
 * :docme -> Indicates that the element (features, scenarios and steps), must be documented.
 * :vertical -> This mark is exclusive for steps. By default, the step is displayed horizontally in the documentation. A screenshot of the browser is displayed on the left side and its title and description on the right. With this mark, the step starts to be displayed vertically, that is, the scrrenshot above and title and description below.
 * :dumpme -> Unique for scenarios, this markup provides a sql dump after run scenario.
 * :before -> Unique for scenarios with :dumpme mark, this markup provides a sql dump before run scenario.
 