import csv, sys, time, heapq
LIMITE = 9.5
# Con esto leemos, ejecutamos y optimizamos los archivos grandes.

def leer_tareas():
    with open("tareas_FN.txt", encoding="utf-8") as f:
        return [{"id": x[0].strip(), "dur": int(x[1]), "cat": x[2].strip()} for x in csv.reader(f) if len(x) >= 3]

def leer_recursos():
    with open("recursos_FN.txt", encoding="utf-8") as f:
        return [{"id": x[0].strip(), "cats": set(y.strip() for y in x[1:] if y.strip())} for x in csv.reader(f) if len(x) >= 2]
# Leemos los archivos y los pasamos a diccionarios.

def compatibilidad(tareas, recursos):
    por_cat, comp, vers, cats_recurso = {}, {}, {}, {}
    for r in recursos:
        rid = r["id"]
        vers[rid] = len(r["cats"])
        cats_recurso[rid] = r["cats"]
        for c in r["cats"]:
            por_cat.setdefault(c, []).append(rid)
    for t in tareas:
        comp[t["id"]] = por_cat[t["cat"]]
    return comp, vers, cats_recurso, por_cat
# Construye compatibilidad por categoría para no recorrer todos los recursos por cada tarea.

def makespan(asignaciones):
    return max((a[3] for a in asignaciones), default=0)

def construir(tareas_ordenadas, comp, vers, cats_recurso):
    libre, asignaciones, heaps = {}, [], {}
    for t in tareas_ordenadas:
        c = t["cat"]
        if c not in heaps:
            h = [(libre.get(r, 0), vers[r], r) for r in comp[t["id"]]]
            heapq.heapify(h)
            heaps[c] = h
        h = heaps[c]
        while h and h[0][0] != libre.get(h[0][2], 0):
            heapq.heappop(h)
        if not h:
            for r in comp[t["id"]]:
                heapq.heappush(h, (libre.get(r, 0), vers[r], r))
            while h[0][0] != libre.get(h[0][2], 0):
                heapq.heappop(h)
        ini, _, mejor_r = heapq.heappop(h)
        fin = ini + t["dur"]
        asignaciones.append([t["id"], mejor_r, ini, fin])
        libre[mejor_r] = fin
        for k in cats_recurso[mejor_r]:
            if k in heaps:
                heapq.heappush(heaps[k], (fin, vers[mejor_r], mejor_r))
    return asignaciones
# Recorre las tareas y les asigna el recurso compatible menos cargado.

def mejorar(asignaciones, comp, limite):
    por_recurso, cargas = {}, {}
    for i, (_, r, _, f) in enumerate(asignaciones):
        por_recurso.setdefault(r, []).append(i)
        cargas[r] = f
    recursos = list(cargas)

    while time.time() < limite and recursos:
        r_critico = max(recursos, key=lambda r: cargas.get(r, 0))
        m = cargas.get(r_critico, 0)
        if m == 0 or not por_recurso.get(r_critico):
            break

        base_otros = max((cargas.get(r, 0) for r in recursos if r != r_critico), default=0)
        mejora = None

        for i in reversed(por_recurso[r_critico][-30:]):
            id_t, r_origen, ini, fin = asignaciones[i]
            d = fin - ini
            for r_destino in sorted(comp[id_t], key=lambda r: cargas.get(r, 0))[:10]:
                if r_destino == r_origen:
                    continue
                nuevo = max(base_otros, m - d, cargas.get(r_destino, 0) + d)
                if nuevo < m and (mejora is None or nuevo < mejora[0]):
                    mejora = (nuevo, i, r_destino, d)
            if mejora and mejora[0] <= base_otros:
                break

        if mejora is None:
            break

        _, i, r_destino, d = mejora
        id_t, r_origen, _, _ = asignaciones[i]
        cargas[r_origen] -= d
        nuevo_ini = cargas.get(r_destino, 0)
        nuevo_fin = nuevo_ini + d
        cargas[r_destino] = nuevo_fin
        por_recurso[r_origen].remove(i)
        por_recurso.setdefault(r_destino, []).append(i)
        asignaciones[i] = [id_t, r_destino, nuevo_ini, nuevo_fin]

    return asignaciones
# Intenta mejorar el cronograma moviendo tareas del recurso crítico a recursos menos cargados.

def escribir(asignaciones):
    with open("output.txt", "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(asignaciones)
# Se escribe en output las asignaciones creadas.

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <makespan_objetivo>")
        return

    objetivo = int(sys.argv[1])
    tareas, recursos = leer_tareas(), leer_recursos()
    comp, vers, cats_recurso, por_cat = compatibilidad(tareas, recursos)

    carga_cat = {}
    for t in tareas:
        carga_cat[t["cat"]] = carga_cat.get(t["cat"], 0) + t["dur"]

    ordenes = [
        sorted(tareas, key=lambda t: (-carga_cat[t["cat"]] / len(comp[t["id"]]), len(comp[t["id"]]), -t["dur"], t["id"])),
        sorted(tareas, key=lambda t: (len(comp[t["id"]]), -carga_cat[t["cat"]], -t["dur"], t["id"])),
        sorted(tareas, key=lambda t: (-t["dur"], len(comp[t["id"]]), t["id"]))
    ]
    # Crea distintos órdenes más útiles para minimizar makespan.

    mejor, mejor_m = [], float("inf")
    limite = time.time() + LIMITE

    for orden in ordenes:
        if time.time() >= limite:
            break
        cand = construir(orden, comp, vers, cats_recurso)
        cand = mejorar(cand, comp, limite)
        m = makespan(cand)
        if m < mejor_m:
            mejor, mejor_m = cand, m
        if mejor_m <= objetivo:
            break

    escribir(mejor)
    print("Makespan:", mejor_m)

if __name__ == "__main__":
    main()