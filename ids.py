"""Datos ficticios deterministas para los 6 microservicios.
Todo se genera aqui, en memoria, con una semilla fija: los IDs que un microservicio
usa de otro (proyecto_id, recurso_id, usuario_id...) salen de las mismas formulas,
asi que siempre coinciden. Nada se lee de otras tablas."""
import hashlib
import random
from datetime import datetime, timedelta
from decimal import Decimal

SEMILLA = 42
TENANTS = ['ACM', 'ORACLE', 'LUDOTECA']

# Registros por tenant (x3 tenants = 30,000 en la tabla principal de cada micro)
N_USUARIOS = 10000
N_PORTAFOLIOS = 20
N_PROYECTOS = 10000
N_TAREAS = 10000
N_GASTOS = 10000          # presupuestos: 1 por proyecto (10,000)
N_RECURSOS = 500
N_ASIGNACIONES = 10000

PASSWORD = '123456'       # usuarios normales
PASSWORD_ADMIN = 'admin123'  # usuario 'admin' de cada tenant (para la demo)

ESTADOS_PROY = ['PLANIFICADO', 'EN_CURSO', 'COMPLETADO']
ESTADOS_TAREA = ['PENDIENTE', 'EN_CURSO', 'COMPLETADA']
PRIORIDADES = ['BAJA', 'MEDIA', 'ALTA']
PESOS = {'valor': Decimal('0.4'), 'urgencia': Decimal('0.3'),
         'costo': Decimal('0.2'), 'riesgo': Decimal('0.1')}
INVERTIDOS = ('costo', 'riesgo')

PREFIJOS = ['Migracion', 'Rediseno', 'Lanzamiento', 'Optimizacion', 'Integracion',
            'Auditoria', 'Expansion', 'Automatizacion', 'Modernizacion', 'Implementacion']
AREAS = ['CRM', 'ERP', 'App movil', 'Portal web', 'Data lake', 'Seguridad', 'Cloud',
         'Facturacion', 'Logistica', 'Soporte', 'Marketing', 'RRHH']
VERBOS = ['Disenar', 'Implementar', 'Revisar', 'Probar', 'Documentar', 'Desplegar',
          'Analizar', 'Corregir', 'Coordinar', 'Validar']
ROLES_REC = ['Desarrollador', 'Analista', 'Disenador', 'QA', 'DevOps', 'Project Manager']
CONCEPTOS = ['Licencias', 'Servidores', 'Consultoria', 'Capacitacion', 'Viaticos',
             'Hardware', 'Servicios cloud', 'Marketing']


# ---------- formulas de IDs ----------
def usuario_id(t, i): return 'admin' if i == 0 else f'USR-{t}-{i:06d}'
def portafolio_id(t, i): return f'POR-{t}-{i:03d}'
def proyecto_id(t, i): return f'PRY-{t}-{i:06d}'
def tarea_id(t, i): return f'TAR-{t}-{i:06d}'
def gasto_id(t, i): return f'GAS-{t}-{i:06d}'
def recurso_id(t, i): return f'REC-{t}-{i:04d}'
def asignacion_id(t, i): return f'ASG-{t}-{i:06d}'


def hash_password(p):  # igual que ms-auth/comun.py
    return hashlib.sha256(p.encode()).hexdigest()


def prioridad_de(p):   # igual que ms-priorizacion/comun.py
    return 'ALTA' if p >= Decimal('3.5') else 'MEDIA' if p >= Decimal('2.5') else 'BAJA'


def calcular_puntaje(v):
    total = sum(PESOS.values())
    s = Decimal(0)
    for c, peso in PESOS.items():
        x = Decimal(v[c])
        s += peso * ((6 - x) if c in INVERTIDOS else x)
    return (s / total).quantize(Decimal('0.01'))


BASE = datetime(2026, 1, 1)
def _ts(rnd): return (BASE + timedelta(minutes=rnd.randint(0, 300 * 24 * 60))).strftime('%Y-%m-%d %H:%M:%S')
def _dia(rnd, desde, dias): return (desde + timedelta(days=rnd.randint(0, dias))).strftime('%Y-%m-%d')


def generar(t):
    """Devuelve {nombre_tabla: [items]} para un tenant, todo consistente entre tablas."""
    rnd = random.Random(f'{SEMILLA}-{t}')
    out = {}

    # --- Auth ---
    usuarios = []
    for i in range(N_USUARIOS):
        admin = i == 0
        usuarios.append({
            'tenant_id': t, 'usuario_id': usuario_id(t, i),
            'password': hash_password(PASSWORD_ADMIN if admin else PASSWORD),
            'rol': 'ADMIN' if admin else rnd.choices(['MIEMBRO', 'GERENTE', 'ADMIN'], [90, 8, 2])[0]})
    out['t_usuarios'] = usuarios

    # --- Recursos ---
    recursos = {}
    for i in range(1, N_RECURSOS + 1):
        recursos[i] = {
            'tenant_id': t, 'recurso_id': recurso_id(t, i),
            'nombre': f'Recurso {i:04d}', 'rol': rnd.choice(ROLES_REC),
            'costo_hora': Decimal(rnd.randint(15, 120)),
            'capacidad_semanal': Decimal(rnd.choice([20, 30, 40])),
            'creado_en': _ts(rnd)}
    out['t_recursos'] = list(recursos.values())

    # --- Tareas (por proyecto: totales y completadas) ---
    tareas, tot, comp = [], {}, {}
    for i in range(1, N_TAREAS + 1):
        p = rnd.randint(1, N_PROYECTOS)
        estado = rnd.choices(ESTADOS_TAREA, [30, 25, 45])[0]
        tareas.append({
            'tenant_id': t, 'tarea_id': tarea_id(t, i), 'proyecto_id': proyecto_id(t, p),
            'titulo': f'{rnd.choice(VERBOS)} {rnd.choice(AREAS)} #{i}',
            'descripcion': f'Tarea ficticia {i} del proyecto {p}',
            'estado': estado, 'prioridad': rnd.choice(PRIORIDADES),
            'asignado_a': usuario_id(t, rnd.randint(1, N_USUARIOS - 1)),
            'fecha_limite': _dia(rnd, datetime(2026, 11, 1), 400),
            'horas': Decimal(rnd.randint(1, 40)), 'creado_en': _ts(rnd)})
        tot[p] = tot.get(p, 0) + 1
        if estado == 'COMPLETADA':
            comp[p] = comp.get(p, 0) + 1
    out['t_tareas'] = tareas

    # --- Gastos y presupuestos (1 presupuesto por proyecto) ---
    gastos, gasto_por = [], {}
    for i in range(1, N_GASTOS + 1):
        p = rnd.randint(1, N_PROYECTOS)
        monto = Decimal(rnd.randint(20000, 3000000)) / 100
        gastos.append({
            'tenant_id': t, 'gasto_id': gasto_id(t, i), 'proyecto_id': proyecto_id(t, p),
            'monto': monto, 'concepto': rnd.choice(CONCEPTOS),
            'fecha': _dia(rnd, datetime(2026, 1, 1), 300),
            'registrado_por': usuario_id(t, rnd.randint(0, N_USUARIOS - 1))})
        gasto_por[p] = gasto_por.get(p, Decimal(0)) + monto
    out['t_gastos'] = gastos

    # --- Asignaciones (costo proyectado por proyecto) ---
    asignaciones, costo_por = [], {}
    for i in range(1, N_ASIGNACIONES + 1):
        p, r = rnd.randint(1, N_PROYECTOS), rnd.randint(1, N_RECURSOS)
        horas = Decimal(rnd.randint(4, 120))
        ch = recursos[r]['costo_hora']
        asignaciones.append({
            'tenant_id': t, 'asignacion_id': asignacion_id(t, i), 'proyecto_id': proyecto_id(t, p),
            'recurso_id': recurso_id(t, r), 'horas': horas, 'costo_hora': ch,
            'costo': horas * ch, 'creado_en': _ts(rnd)})
        costo_por[p] = costo_por.get(p, Decimal(0)) + horas * ch
    out['t_asignaciones'] = asignaciones

    presupuestos, excedido = [], set()
    for p in range(1, N_PROYECTOS + 1):
        monto_total = Decimal(rnd.randint(500000, 6000000)) / 100
        gasto = gasto_por.get(p, Decimal(0))
        exc = gasto > monto_total
        if exc:
            excedido.add(p)
        presupuestos.append({
            'tenant_id': t, 'proyecto_id': proyecto_id(t, p), 'monto_total': monto_total,
            'gasto_acumulado': gasto, 'costo_proyectado': costo_por.get(p, Decimal(0)),
            'estado_presupuesto': 'EXCEDIDO' if exc else 'NORMAL', 'creado_en': _ts(rnd)})
    out['t_presupuestos'] = presupuestos

    # --- Portafolios, proyectos, puntajes ---
    out['t_portafolios'] = [{
        'tenant_id': t, 'portafolio_id': portafolio_id(t, i), 'nombre': f'Portafolio {i:03d}',
        'descripcion': f'Portafolio ficticio {i}', 'creado_en': _ts(rnd)}
        for i in range(1, N_PORTAFOLIOS + 1)]

    proyectos, puntajes = [], []
    resumen = {'tenant_id': t, 'clave': 'RESUMEN', 'total_proyectos': 0,
               'tareas_total': 0, 'tareas_completadas': 0, 'presupuestos_excedidos': 0}
    por_port = {}
    for p in range(1, N_PROYECTOS + 1):
        pid = proyecto_id(t, p)
        port = portafolio_id(t, (p - 1) % N_PORTAFOLIOS + 1)
        estado = rnd.choices(ESTADOS_PROY, [25, 50, 25])[0]
        valores = {c: rnd.randint(1, 5) for c in PESOS}
        if p in excedido:
            valores['costo'] = 5          # lo que haria el evento PresupuestoExcedido
        puntaje = calcular_puntaje(valores)
        prioridad = prioridad_de(puntaje)
        T, C = tot.get(p, 0), comp.get(p, 0)
        proyectos.append({
            'tenant_id': t, 'proyecto_id': pid, 'portafolio_id': port,
            'nombre': f'{rnd.choice(PREFIJOS)} {rnd.choice(AREAS)} {p}',
            'descripcion': f'Proyecto ficticio {p} del tenant {t}',
            'estado': estado, 'prioridad': prioridad,
            'avance_pct': round(100 * C / T) if T else 0,
            'tareas_total': T, 'tareas_completadas': C,
            'estado_presupuesto': 'EXCEDIDO' if p in excedido else 'NORMAL',
            'fecha_fin': _dia(rnd, datetime(2026, 11, 1), 500), 'creado_en': _ts(rnd)})
        puntajes.append({
            'tenant_id': t, 'proyecto_id': pid, 'portafolio_clave': f'{t}#{port}',
            'portafolio_id': port, 'puntaje': puntaje, 'prioridad': prioridad,
            'valores': {k: Decimal(v) for k, v in valores.items()},
            'evaluado_en': _ts(rnd)})
        resumen['total_proyectos'] += 1
        resumen[f'proy_{estado}'] = resumen.get(f'proy_{estado}', 0) + 1
        resumen['tareas_total'] += T
        resumen['tareas_completadas'] += C
        if p in excedido:
            resumen['presupuestos_excedidos'] += 1
        por_port[port] = por_port.get(port, 0) + 1
    out['t_proyectos'] = proyectos
    out['t_puntajes'] = puntajes
    out['t_resumen_tenant'] = [resumen] + [
        {'tenant_id': t, 'clave': f'PORT#{k}', 'total_proyectos': v} for k, v in por_port.items()]
    out['t_criterios'] = [{'tenant_id': t, 'criterio_id': c, 'peso': w,
                           'invertido': c in INVERTIDOS} for c, w in PESOS.items()]
    return out
