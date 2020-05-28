from django.conf import settings
from django.core.management import call_command
from pkg_resources import resource_string
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from jinja2 import Template
import json

def json_script():
    json_scripts = [json.load(open(json_script))
                    for json_script in settings.AUTO_TOUR_SCRIPTS]
    json_doc = {}
    for json_script in json_scripts:
        json_doc.update(json_script)
    return json_doc

def auto_tour_index(request):
    return render(request, 'docme/index.html', {'json_doc':json_script()})

def start_tour(request):
    scenario = json_script()[request.GET['app']][request.GET['feature_name']
                                                 ]['scenarios'][request.GET['scenario_name']]
    call_command('flush')
    # call_command('sync_permissions', verbosity=0)
    for fixture in scenario['fixtures']:
        call_command('loaddata', fixture, skip_checks=True)
    # ==== Lixo ====
    from comum.models import User
    from ponto.models import Frequencia, Maquina, Observacao, ObservacaoChefia
    from django.contrib.auth.models import Group
    from rh.models import Servidor
    from datetime import datetime, date
    us = User.objects.get(username='1111111')
    us.set_password('T3st3!@#')
    us.save()
    usuario = User.objects.get(username='1111111')
    grupo = Group.objects.get(name='Servidor')
    usuario.groups.add(grupo)
    usuario = User.objects.get(username='1111111')
    grupo = Group.objects.get(name='Chefe de Setor')
    usuario.groups.add(grupo)
    servidor = Servidor.objects.get(matricula='3333333')
    maquina = Maquina.objects.get(id=55)
    Frequencia(vinculo=servidor.vinculo_set.all()[0], horario=datetime(
        2018, 1, 21, 7, 0, 1), acao='E', maquina=maquina).save()
    Frequencia(vinculo=servidor.vinculo_set.all()[0], horario=datetime(
        2018, 1, 21, 12, 0, 1), acao='S', maquina=maquina).save()
    Frequencia(vinculo=servidor.vinculo_set.all()[0], horario=datetime(
        2018, 1, 21, 13, 0, 1), acao='E', maquina=maquina).save()
    Frequencia(vinculo=servidor.vinculo_set.all()[0], horario=datetime(
        2018, 1, 21, 16, 00, 1), acao='S', maquina=maquina).save()
    return JsonResponse({'next_path': scenario['first_path']})


def get_steps(request):
    scenario = json_script()[request.GET['app']][request.GET['feature_name']
                                                 ]['scenarios'][request.GET['scenario_name']]
    return JsonResponse({'steps': scenario['steps'][request.GET['current_path']]})
