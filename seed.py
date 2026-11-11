"""Carga los datos ficticios en DynamoDB.
Uso:  python seed.py [auth|proyectos|tareas|presupuestos|recursos|priorizacion|todos] [--dry-run]
Requiere los microservicios YA desplegados (las tablas las crea el serverless.yml)."""
import sys
from concurrent.futures import ThreadPoolExecutor
import boto3
import ids

MICROS = {
    'auth': ['t_usuarios'],
    'proyectos': ['t_portafolios', 't_proyectos', 't_resumen_tenant'],
    'tareas': ['t_tareas'],
    'presupuestos': ['t_presupuestos', 't_gastos'],
    'recursos': ['t_recursos', 't_asignaciones'],
    'priorizacion': ['t_criterios', 't_puntajes'],
}
HILOS = 8


def _escribir_trozo(tabla, trozo):
    t = boto3.session.Session().resource('dynamodb').Table(tabla)  # un recurso por hilo
    with t.batch_writer() as bw:
        for item in trozo:
            bw.put_item(Item=item)
    return len(trozo)


def escribir(tabla, items):
    n = max(1, len(items) // HILOS + 1)
    trozos = [items[i:i + n] for i in range(0, len(items), n)]
    with ThreadPoolExecutor(HILOS) as ex:
        return sum(ex.map(lambda tr: _escribir_trozo(tabla, tr), trozos))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry-run' in sys.argv
    micro = args[0] if args else 'todos'
    elegidos = list(MICROS) if micro == 'todos' else [micro]
    if any(m not in MICROS for m in elegidos):
        sys.exit('Micro invalido. Opciones: ' + ', '.join(MICROS) + ', todos')
    for t in ids.TENANTS:
        datos = ids.generar(t)
        for m in elegidos:
            for tabla in MICROS[m]:
                items = datos[tabla]
                n = len(items) if dry else escribir(tabla, items)
                print(f'{"[dry] " if dry else ""}{t:9} {tabla:18} {n:6} items')
    print('Listo.')


if __name__ == '__main__':
    main()
