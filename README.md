# seed-datos

Carga datos ficticios en las tablas de los 6 microservicios (3 tenants: ACM, ORACLE, LUDOTECA).

## Cantidades por tenant (x3 = total)
| Micro | Tabla principal | Por tenant | Total |
| --- | --- | --- | --- |
| Auth | t_usuarios | 10,000 | 30,000 |
| Proyectos | t_proyectos (+ 20 portafolios, resumen) | 10,000 | 30,000 |
| Tareas | t_tareas | 10,000 | 30,000 |
| Presupuestos | t_presupuestos + t_gastos | 10,000 + 10,000 | 30,000 + 30,000 |
| Recursos | t_asignaciones + t_recursos (500) | 10,000 | 30,000 |
| Priorizacion | t_puntajes (+ 4 criterios) | 10,000 | 30,000 |

## Uso
1. Desplegar los 6 microservicios (crean las tablas).
2. Credenciales de AWS Learner Lab en el terminal (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
   AWS_SESSION_TOKEN y AWS_DEFAULT_REGION=us-east-1).
3. `pip install -r requirements.txt`
4. Probar sin escribir: `python seed.py todos --dry-run`
5. Cargar: `python seed.py todos` (o un micro: `python seed.py tareas`)

Se puede repetir: usa put_item con las mismas claves, asi que sobrescribe sin duplicar.

## Login de la demo
- tenant_id `ACM` / `ORACLE` / `LUDOTECA`, usuario `admin`, password `admin123`
- Otros usuarios: `USR-ACM-000001` ... password `123456`

## Consistencia
Los IDs salen de formulas (`PRY-ACM-000123`, `REC-ACM-0042`...) y todo se genera con semilla 42,
asi que lo que Tareas, Presupuestos, Recursos y Priorizacion referencian existe en Proyectos.
Los campos calculados cuadran: avance_pct y tareas_* de cada proyecto salen de sus tareas,
gasto_acumulado de sus gastos, costo_proyectado de sus asignaciones, estado_presupuesto EXCEDIDO
cuando gasto > monto_total (y entonces su criterio costo = 5), y t_resumen_tenant con los contadores.

El seed escribe directo en las tablas: NO dispara eventos SNS/SQS ni correos.
