"""Proyecto 5 · Rolling forecast y escenarios — Grupo Power Tower.
Genera datos mensuales pequeños (~450 filas en total). Ejecutar desde la carpeta del proyecto: python src/generar_datos.py"""
import numpy as np, pandas as pd, os
rng = np.random.default_rng(5)
OUT = "data"; os.makedirs(OUT, exist_ok=True)

cuentas = pd.DataFrame([
    [10,  "VEN",   "Ventas",                    "Detalle",  "Ventas"],
    [20,  "CV",    "Coste de ventas",           "Detalle",  "Coste de ventas"],
    [30,  "MB",    "Margen bruto",              "Subtotal", None],
    [40,  "PER",   "Gastos de personal",        "Detalle",  "Personal"],
    [50,  "MKT",   "Marketing y comercial",     "Detalle",  "Gastos generales"],
    [60,  "ALQ",   "Alquileres y suministros",  "Detalle",  "Gastos generales"],
    [70,  "OGG",   "Otros gastos generales",    "Detalle",  "Gastos generales"],
    [80,  "EBITDA","EBITDA",                    "Subtotal", None],
    [90,  "AMO",   "Amortización",              "Detalle",  "Amortización"],
    [100, "EBIT",  "EBIT",                      "Subtotal", None],
], columns=["Orden", "IdCuenta", "Cuenta", "Tipo", "GrupoDriver"])

lineas = pd.DataFrame([
    ["TOR", "Torres eólicas", "Fabricación de torres y estructuras"],
    ["MAN", "Mantenimiento",  "Operación y mantenimiento de parques"],
    ["ING", "Ingeniería",     "Proyectos de ingeniería y consultoría"],
    ["COR", "Corporativo",    "Gastos de estructura no asignados"],
], columns=["IdLinea", "Linea", "Descripcion"])

# ventas anuales 2025 (€) y % de coste por línea; estacionalidad mensual
vta25 = {"TOR": 46_000_000, "MAN": 26_000_000, "ING": 12_000_000}
pct_coste = {"TOR": 0.71, "MAN": 0.56, "ING": 0.48}
estac = {"TOR": [0.06,0.07,0.09,0.08,0.09,0.10,0.07,0.05,0.09,0.10,0.10,0.10],
         "MAN": [1/12]*12,
         "ING": [0.07,0.08,0.09,0.08,0.09,0.09,0.07,0.04,0.09,0.10,0.10,0.10]}
opex25 = {"PER": -11_400_000, "MKT": -2_100_000, "ALQ": -1_800_000, "OGG": -2_600_000, "AMO": -3_000_000}
crec_real_26 = {"TOR": 0.04, "MAN": 0.09, "ING": -0.02}       # lo que de verdad pasa en 2026
crec_ppto_26 = {"TOR": 0.10, "MAN": 0.08, "ING": 0.06}       # presupuesto ambicioso
infl_real_26, infl_ppto_26 = 0.045, 0.03

def fila(fecha, cta, lin, imp): return [fecha, cta, lin, round(imp)]
real, ppto = [], []
for y in (2025, 2026):
    for m in range(1, 13):
        f = pd.Timestamp(y, m, 1)
        for l, v in vta25.items():
            base = v * estac[l][m-1]
            if y == 2026 and m <= 9:
                vr = base * (1 + crec_real_26[l]) * rng.normal(1, 0.04)
                real += [fila(f, "VEN", l, vr), fila(f, "CV", l, -vr * (pct_coste[l] + 0.012) * rng.normal(1, 0.01))]
            if y == 2025:
                vr = base * rng.normal(1, 0.04)
                real += [fila(f, "VEN", l, vr), fila(f, "CV", l, -vr * pct_coste[l] * rng.normal(1, 0.01))]
            if y == 2026:
                vp = base * (1 + crec_ppto_26[l])
                ppto += [fila(f, "VEN", l, vp), fila(f, "CV", l, -vp * pct_coste[l])]
        for c, v in opex25.items():
            base = v / 12
            if c == "MKT": base *= [0.7,0.8,1.2,1.1,1,1,0.8,0.5,1.2,1.3,1.2,1.2][m-1]
            if y == 2025:
                real.append(fila(f, c, "COR", base * (1 if c == "AMO" else rng.normal(1, 0.03))))
            if y == 2026 and m <= 9:
                g = 0.02 if c == "AMO" else infl_real_26
                real.append(fila(f, c, "COR", base * (1 + g) * (1 if c == "AMO" else rng.normal(1, 0.03))))
            if y == 2026:
                g = 0.02 if c == "AMO" else infl_ppto_26
                ppto.append(fila(f, c, "COR", base * (1 + g)))

cols = ["Fecha", "IdCuenta", "IdLinea", "Importe"]
real, ppto = pd.DataFrame(real, columns=cols), pd.DataFrame(ppto, columns=cols)

escenarios = pd.DataFrame([[1, "Base", "Tendencia actual"], [2, "Optimista", "Recuperación de pedidos en torres"],
                           [3, "Pesimista", "Retraso de parques y presión de costes"]], columns=["Orden", "Escenario", "Descripcion"])
drivers = pd.DataFrame([
    ["Base", "Ventas", 0.06], ["Base", "Coste de ventas", 0.02], ["Base", "Personal", 0.04], ["Base", "Gastos generales", 0.03], ["Base", "Amortización", 0.02],
    ["Optimista", "Ventas", 0.12], ["Optimista", "Coste de ventas", 0.01], ["Optimista", "Personal", 0.05], ["Optimista", "Gastos generales", 0.03], ["Optimista", "Amortización", 0.02],
    ["Pesimista", "Ventas", -0.05], ["Pesimista", "Coste de ventas", 0.04], ["Pesimista", "Personal", 0.03], ["Pesimista", "Gastos generales", 0.02], ["Pesimista", "Amortización", 0.02],
], columns=["Escenario", "GrupoDriver", "Variacion"])

# Real: CSV exportado del ERP (separador ; y decimales sin formato) — Presupuesto: Excel "de controller" en formato ancho (meses en columnas)
real.assign(Fecha=real.Fecha.dt.strftime("%Y-%m")).rename(columns={"Fecha": "Periodo"}).to_csv(f"{OUT}/real_ERP.csv", sep=";", index=False)
MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
ancho = ppto.assign(Mes=ppto.Fecha.dt.month.map(lambda m: MESES[m-1])).pivot_table(index=["IdCuenta", "IdLinea"], columns="Mes", values="Importe", sort=False).reset_index()
ancho = ancho[["IdCuenta", "IdLinea"] + MESES]
with pd.ExcelWriter(f"{OUT}/presupuesto_2026.xlsx") as w:
    ancho.to_excel(w, index=False, sheet_name="Ppto2026")
with pd.ExcelWriter(f"{OUT}/maestros.xlsx") as w:
    cuentas.to_excel(w, index=False, sheet_name="Cuentas")
    lineas.to_excel(w, index=False, sheet_name="Lineas")
    escenarios.to_excel(w, index=False, sheet_name="Escenarios")
    drivers.to_excel(w, index=False, sheet_name="Drivers")
print("filas real", len(real), "ppto", len(ppto))
