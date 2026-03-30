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
        cats = r["cats"]
        vers[rid] = len(cats)
        cats_recurso[rid] = cats
        for c in cats:
            por_cat.setdefault(c, []).append(rid)

    for t in tareas:
        comp[t["id"]] = por_cat.get(t["cat"], [])

    return comp, vers, cats_recurso, por_cat
# Construye compatibilidad por categoría para no recorrer todos los recursos por cada tarea.

def makespan(asignaciones):
    return max((a[3] for a in asignaciones), default=0)

def construir(tareas_ordenadas, comp, vers, cats_recurso):
    libre = {}
    asignaciones = []
    heaps = {}
    usados = {}

    for t in tareas_ordenadas:
        tid = t["id"]
        c = t["cat"]

        if c not in heaps:
            h = [(0, vers[r], r) for r in comp[tid]]
            heapq.heapify(h)
            heaps[c] = h
            usados[c] = len(h)

        h = heaps[c]

        while h and h[0][0] != libre.get(h[0][2], 0):
            heapq.heappop(h)

        if not h or len(h) > 4 * max(1, len(comp[tid])):
            # reconstruccion del heap de categoria
            h = [(libre.get(r, 0), vers[r], r) for r in comp[tid]]
            heapq.heapify(h)
            heaps[c] = h

        ini, _, mejor_r = heapq.heappop(heaps[c])
        fin = ini + t["dur"]

        asignaciones.append([tid, mejor_r, ini, fin])
        libre[mejor_r] = fin

        for k in cats_recurso[mejor_r]:
            if k in heaps:
                heapq.heappush(heaps[k], (fin, vers[mejor_r], mejor_r))

    return asignaciones
# Recorre las tareas y les asigna el recurso compatible menos cargado.

def mejorar(asignaciones, comp, limite):
    # Construir estructuras por recurso
    por_recurso = {}
    cargas = {}

    for i, (_, r, ini, fin) in enumerate(asignaciones):
        por_recurso.setdefault(r, []).append(i)
        cargas[r] = max(cargas.get(r, 0), fin)

    if not cargas:
        return asignaciones

    # Compatibilidades ordenadas una sola vez
    comp_ordenado = {
        tid: lista[:] for tid, lista in comp.items()
    }

    mejor_m = max(cargas.values(), default=0)

    while time.time() < limite:
        # recurso critico
        r_critico = max(cargas, key=cargas.get)
        carga_critica = cargas[r_critico]

        if carga_critica == 0 or not por_recurso.get(r_critico):
            break

        # tomar solo la ultima tarea del recurso critico
        i = por_recurso[r_critico][-1]
        id_t, r_origen, ini, fin = asignaciones[i]
        d = fin - ini

        mejor_destino = None
        mejor_nuevo_m = mejor_m

        # probar destinos compatibles, ordenados por carga
        for r_destino in sorted(comp_ordenado[id_t], key=lambda r: cargas.get(r, 0)):
            if r_destino == r_origen:
                continue

            nueva_carga_origen = carga_critica - d
            nueva_carga_destino = cargas.get(r_destino, 0) + d

            nuevo_m = 0
            for r, carga in cargas.items():
                if r == r_origen:
                    nuevo_m = max(nuevo_m, nueva_carga_origen)
                elif r == r_destino:
                    nuevo_m = max(nuevo_m, nueva_carga_destino)
                else:
                    nuevo_m = max(nuevo_m, carga)

            if nuevo_m < mejor_nuevo_m:
                mejor_nuevo_m = nuevo_m
                mejor_destino = r_destino

            if nuevo_m <= max((c for rr, c in cargas.items() if rr != r_origen and rr != r_destino), default=0):
                break

        if mejor_destino is None:
            break

        # aplicar movimiento valido: sacar ultima del origen y agregar al final del destino
        por_recurso[r_origen].pop()
        if not por_recurso[r_origen]:
            del por_recurso[r_origen]

        nuevo_ini = cargas.get(mejor_destino, 0)
        nuevo_fin = nuevo_ini + d

        asignaciones[i] = [id_t, mejor_destino, nuevo_ini, nuevo_fin]

        por_recurso.setdefault(mejor_destino, []).append(i)

        cargas[r_origen] -= d
        if cargas[r_origen] == 0 and r_origen not in por_recurso:
            del cargas[r_origen]

        cargas[mejor_destino] = nuevo_fin
        mejor_m = mejor_nuevo_m

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

    tareas = leer_tareas()
    recursos = leer_recursos()
    comp, vers, cats_recurso, por_cat = compatibilidad(tareas, recursos)

    for t in tareas:
        if not comp[t["id"]]:
            print("Instancia invalida: tarea sin recurso compatible:", t["id"])
            return

    lb = cota_inferior(tareas, recursos, por_cat)

    carga_cat = {}
    for t in tareas:
        carga_cat[t["cat"]] = carga_cat.get(t["cat"], 0) + t["dur"]

    get_carga_cat = carga_cat.get
    
    comp_len = {tid: len(rs) for tid, rs in comp.items()}

    base1 = sorted(
        tareas,
        key=lambda t: (
            -carga_cat[t["cat"]] / max(1, comp_len[t["id"]]),
            comp_len[t["id"]],
            -t["dur"],
            t["id"],
        ),
    )

    base2 = sorted(
        tareas,
        key=lambda t: (
            comp_len[t["id"]],
            -carga_cat[t["cat"]],
            -t["dur"],
            t["id"],
        ),
    )

    base3 = sorted(
        tareas,
        key=lambda t: (
            -t["dur"],
            comp_len[t["id"]],
            t["id"],
        ),
    )

    ordenes = [base1, base2, base3]
    for s in range(10):
        ordenes.append(perturbar(base1, s))
        ordenes.append(perturbar(base2, 100 + s))

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

        if mejor_m <= objetivo or mejor_m <= lb:
            break

    if not validar(mejor, tareas, comp):
        print("Salida invalida")
        return

    escribir(mejor)
    print("Makespan:", mejor_m)
    # Crea distintos órdenes más útiles para minimizar makespan.

def perturbar(base, seed):
    rng = __import__("random").Random(seed)
    arr = base[:]
    n = len(arr)
    for _ in range(min(20, n)):
        i = rng.randrange(n)
        j = rng.randrange(n)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def cota_inferior(tareas, recursos, por_cat):
    total = sum(t["dur"] for t in tareas)
    lb = (total + len(recursos) - 1) // len(recursos)

    carga_cat = {}
    for t in tareas:
        carga_cat[t["cat"]] = carga_cat.get(t["cat"], 0) + t["dur"]

    for cat, carga in carga_cat.items():
        k = len(por_cat.get(cat, []))
        if k > 0:
            lb = max(lb, (carga + k - 1) // k)

    return lb

def validar(asignaciones, tareas, comp):
    vistos = set()
    dur = {t["id"]: t["dur"] for t in tareas}
    por_recurso = {}

    for tid, rid, ini, fin in asignaciones:
        if tid in vistos:
            return False
        vistos.add(tid)

        if rid not in comp.get(tid, []):
            return False

        if fin - ini != dur[tid]:
            return False

        por_recurso.setdefault(rid, []).append((ini, fin))

    if len(vistos) != len(tareas):
        return False

    for r in por_recurso:
        xs = sorted(por_recurso[r])
        for i in range(1, len(xs)):
            if xs[i][0] < xs[i - 1][1]:
                return False

    return True

if __name__ == "__main__":
    main()