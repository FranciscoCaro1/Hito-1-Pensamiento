#Todo lo que necesito para importar archivos y sus tipos, usar tiempo limite y tambien tener aleatoriedad.

from __future__ import annotations

import csv
import random
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

Limite_tiempo = 9
#---------------------------------------------
@dataclass(frozen=True)                     #Transformamos la informacion del archivo tareas poder leerlo
class Tareas:
    tarea_id: str
    duracion: int
    categoria: str

@dataclass(frozen=True)                     #Transformamos la informacion del archivo recursos poder leerlo
class Recursos:
    recursos_id: str
    categorias: Set[str]

@dataclass(frozen=True)                     #Ordenamos los recursos y tareas (guardamos decision)
class Orden:
    tarea_id: str
    recurso_id: str
    timpo_inicial: int
    tiempo_final: int
#-----------------------------------------------------------
def Lectura_de_tareas(filename: str) -> List[Tareas]:
    tasks: List[Tareas] = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            tarea.append(
                Tareas(
                    tarea_id=row[0].strip(),
                    duracion=int(row[1].strip()),
                    categoria=row[2].strip(),
                )
            )

    return tarea 

def Lectura_de_recursos(filename: str) -> List[Recursos]:
    resources: List[Recursos] = []

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            recursos.append(
                Recursos(
                    recursos_id=row[0].strip(),
                    categorias={value.strip() for value in row[1:]},
                )
            )

    return recursos 
#Leen los archivos de tareas y recursos y las pasamos a listas
#------------------------------------------------------------------------
tareas.categoria in recursos.categorias


def compatible_resources_for_task(task: tarea, resources: List[recursos]) -> List[recursos]:
    return [resource for resource in resources if task.category in resource.categories]

def compatibility_map(tasks: List[tarea], resources: List[recursos]) -> Dict[str, List[recursos]]:
    result: Dict[str, List[recursos]] = {}
    for task in tasks:
        result[task.tarea_id] = compatible_resources_for_task(task, resources)
    return result

def compatibility_map(tasks: List[tarea], resources: List[Recursos]) -> Dict[str, List[Recursos]]:
    result: Dict[str, List[Recursos]] = {}
    for task in tasks:
        result[task.tarea_id] = compatible_resources_for_task(task, resources)
    return result



