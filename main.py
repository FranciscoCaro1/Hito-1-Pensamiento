import csv, sys, random, time 
LIMITE = 9.5
#Con esto leemos, ejecutamos, probamos orden aleatorio los archivos.

def leer_tareas():
    with open("tareas.txt", encoding="utf-8") as f:
        return [{"id": x[0].strip(), "dur": int(x[1]), "cat": x[2].strip()} for x in csv.reader(f) if len(x) >= 3]

def leer_recursos():
    with open("recursos.txt", encoding="utf-8") as f:
        return [{"id": x[0].strip(), "cats": set(y.strip() for y in x[1:] if y.strip())} for x in csv.reader(f) if len(x) >= 2]
##Leemos los archivos y los asamos a un diccionario

def compatibilidad(tareas, recursos):
    return {t["id"]: [r["id"] for r in recursos if t["cat"] in r["cats"]] for t in tareas}

#Construye un diccionario que dice qué recursos pueden hacer cada tarea

def makespan(asignaciones):
    return max((a[3] for a in asignaciones), default=0)

def construir(tareas_ordenadas, comp, vers):
    libre, asignaciones = {}, []
    for t in tareas_ordenadas:
        mejor_r, mejor_valor = None, None
        for r in comp[t["id"]]:
            ini = libre.get(r, 0)
            fin = ini + t["dur"]
            valor = fin + 0.15 * vers[r] * max(0, len(comp[t["id"]]) - 1) + 0.05 * ini
            if mejor_valor is None or valor < mejor_valor:
                mejor_valor, mejor_r = valor, r
        ini = libre.get(mejor_r, 0)
        fin = ini + t["dur"]
        asignaciones.append([t["id"], mejor_r, ini, fin])
        libre[mejor_r] = fin
    return asignaciones
#Recorre las tareas y le asigna un recurso

def reconstruir(asignaciones, tareas_por_id):
    por_recurso = {}
    for id_t, id_r, _, _ in asignaciones:
        por_recurso.setdefault(id_r, []).append(tareas_por_id[id_t])
    nuevas = []
    for r, lista in por_recurso.items():
        tiempo = 0
        for t in lista:
            nuevas.append([t["id"], r, tiempo, tiempo + t["dur"]])
            tiempo += t["dur"]
    return nuevas
#Como asignamos una tarea a un recurso, recontruimos los recursos

def mejorar(asignaciones, tareas_por_id, comp, limite):
    mejor = asignaciones[:]
    while time.time() < limite:
        m = makespan(mejor)
        cargas = {}
        for _, r, _, f in mejor:
            cargas[r] = max(cargas.get(r, 0), f)
        criticos = {r for r, c in cargas.items() if c == m}
        cambio = False
        for id_t, r_origen, _, _ in sorted(mejor, key=lambda x: x[3], reverse=True):
            if r_origen not in criticos:
                continue
            for r_destino in comp[id_t]:
                if r_destino == r_origen:
                    continue
                candidato = [[a,b,c,d] for a,b,c,d in mejor if a != id_t]
                candidato.append([id_t, r_destino, 0, 0])
                candidato = reconstruir(candidato, tareas_por_id)
                if makespan(candidato) < m:
                    mejor = candidato
                    cambio = True
                    break
            if cambio:
                break
        if not cambio:
            break
    return mejor
#Intenta mejorar un cronograma ya construido moviendo tareas de un recurso a otro

def escribir(asignaciones):
    with open("output.txt", "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(asignaciones)
#Se ecribe en el archivo "output" las asignaciones creadas

def mostrar_distribucion(asignaciones):
    por_recurso = {}
    for id_t, id_r, ini, fin in asignaciones:
        por_recurso.setdefault(id_r, []).append((id_t, ini, fin))
    print("\nDistribución:")
    for r in sorted(por_recurso):
        print(f"{r}: {por_recurso[r]}")
#Funcion para que haga print en el terminal de la distribucion con su respectivo recurso

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <makespan_objetivo>")        #Revisa si ejecutamos bien
        return

    objetivo = int(sys.argv[1])                             #Guarda el numero pedido
    tareas, recursos = leer_tareas(), leer_recursos()       #Lee datos
    comp = compatibilidad(tareas, recursos)                 #Construye compatibilidad
    vers = {r["id"]: len(r["cats"]) for r in recursos}
    tareas_por_id = {t["id"]: t for t in tareas}            #Accede a tareas
    rng = random.Random(42)
    ordenes = [
        sorted(tareas, key=lambda t: (-t["dur"], len(comp[t["id"]]), t["id"])),
        sorted(tareas, key=lambda t: (len(comp[t["id"]]), -t["dur"], t["id"])),
        random.sample(tareas, len(tareas))
    ]       #Crea distintos ordenes de tareas

    mejor, mejor_m = [], float("inf")       #Guarda la mejor
    limite = time.time() + LIMITE

    for orden in ordenes:
        if time.time() >= limite:
            break
        cand = construir(orden, comp, vers)
        cand = mejorar(cand, tareas_por_id, comp, limite)
        m = makespan(cand)
        if m < mejor_m:
            mejor, mejor_m = cand, m
        if mejor_m <= objetivo:
            break                           #Construye y mejora la solucion

    escribir(mejor)            
    print("Makespan:", mejor_m)     #Muestra resultado 
    mostrar_distribucion(mejor)

if __name__ == "__main__":      #Ejecuta el programa
    main()