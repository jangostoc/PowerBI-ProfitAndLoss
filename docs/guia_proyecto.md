# Proyecto 5 · Rolling forecast y escenarios

> **Área:** FP&A · **Nivel:** intermedio · **Datos:** 363 filas · **Tiempo estimado:** 6–8 h
> Si un paso no te sale o algo no cuadra con las cifras ✅, mándame una captura.

## El caso
**Grupo Power Tower** fabrica torres eólicas, mantiene parques y presta servicios de ingeniería. Es octubre de 2026 y ya están cerrados los datos reales hasta septiembre. El director financiero quiere saber:
1. **¿Cómo cerramos 2026** frente al presupuesto, en tres escenarios (base, optimista y pesimista)?
2. **¿Qué esperamos para los próximos 12 meses** (rolling forecast de octubre de 2026 a septiembre de 2027)?
3. **¿Cuánto EBITDA ganamos o perdemos por cada 1 % de ventas** de más o de menos?

Tu informe tiene que dejar que el usuario **cambie de escenario y mueva las ventas con un deslizador** y ver el impacto al momento.

## Datos (`data/`)
| Fichero | Contenido | Lo que tienes que resolver |
|---|---|---|
| `real_ERP.csv` | Real mensual ene-2025 → sep-2026 por cuenta y línea de negocio (231 filas) | Separador `;`; el periodo viene como texto `2025-01` |
| `presupuesto_2026.xlsx` | Presupuesto 2026 en **formato ancho**, con los meses en columnas (`ene`…`dic`) | Despivotar y convertir el nombre del mes en una fecha |
| `maestros.xlsx` → *Cuentas* | Estructura de la cuenta de resultados con orden, tipo (Detalle/Subtotal) y grupo de driver | Es la clave para pintar los subtotales |
| `maestros.xlsx` → *Lineas* | Torres eólicas · Mantenimiento · Ingeniería · Corporativo | |
| `maestros.xlsx` → *Escenarios* y *Drivers* | Variación % por escenario y grupo de driver | Tablas **desconectadas** |

**Signos:** los ingresos son positivos y los gastos negativos. Así, una desviación positiva siempre es favorable, sea ingreso o gasto. Coméntalo en el README: es un detalle de FP&A que se valora.

## Lógica del forecast (tenla clara antes de tocar DAX)
Para cada mes futuro y cada cuenta:

| Grupo de driver | Forecast del mes |
|---|---|
| Ventas | Real del mismo mes del año anterior × (1 + g ventas + ajuste del deslizador) |
| Coste de ventas | Real del mismo mes del año anterior × (1 + g ventas + ajuste) × (1 + inflación de costes) |
| Personal, gastos generales y amortización | Real del mismo mes del año anterior × (1 + g del grupo) |

Así el coste de ventas se mueve con el volumen. Si subes las ventas, también sube su coste. Es un error típico olvidarlo.

---

## FASE 0 · Preparación

1. Descomprime el zip. Dentro de `05-rolling-forecast\data\` tienes **tres archivos**: `real_ERP.csv`, `presupuesto_2026.xlsx` y `maestros.xlsx`.
2. Abre Power BI Desktop → *Informe en blanco*.
3. *Archivo → Guardar como* → elige la carpeta `05-rolling-forecast` → tipo **Archivos de proyecto de Power BI (*.pbip)** → nombre `RollingForecast`.

## FASE 1 · Power Query: cargar y limpiar los datos

### Antes de empezar: qué vas a construir
Cada archivo (o cada hoja de Excel) que importas se convierte en una **consulta** de Power Query. Al cerrar el editor, cada consulta pasa a ser una **tabla** del modelo. El nombre de la consulta es el que tú le pongas. Te propongo estos nombres, siguiendo la convención habitual:
- **`f` + nombre** = tabla de **hechos**: los números (importes por mes).
- **`d` + nombre** = **dimensión**: los catálogos con los que filtras (cuentas, líneas de negocio, escenarios).

Al terminar esta fase tendrás **6 tablas**:

| Nombre de la tabla | Archivo de origen | Hoja | Qué contiene | Filas |
|---|---|---|---|---|
| `fReal` | `real_ERP.csv` | (es un CSV, no tiene hojas) | Importes reales por mes, cuenta y línea | 231 |
| `fPresupuesto` | `presupuesto_2026.xlsx` | `Ppto2026` | Importes presupuestados de 2026 | 132 (tras despivotar) |
| `dCuenta` | `maestros.xlsx` | `Cuentas` | Las 10 líneas de la cuenta de resultados | 10 |
| `dLinea` | `maestros.xlsx` | `Lineas` | Las 4 líneas de negocio | 4 |
| `dEscenario` | `maestros.xlsx` | `Escenarios` | Base, Optimista y Pesimista | 3 |
| `fDrivers` | `maestros.xlsx` | `Drivers` | % de variación por escenario y grupo | 15 |

💡 **Dónde ver el número de filas:** en el Editor de Power Query, abajo a la izquierda, pone por ejemplo «4 COLUMNAS, 231 FILAS».

---

### 1.1 `fReal`: el real del ERP (archivo `real_ERP.csv`)

**Qué hay en el archivo:** 4 columnas. `Periodo` es un texto como `2025-01`, `IdCuenta` es un código como `VEN` (ventas) o `CV` (coste de ventas), `IdLinea` es un código como `TOR` (torres) y `Importe` es el importe en euros.
**Qué tiene que salir:** las mismas filas, pero con una columna `Fecha` de tipo fecha (01/01/2025) en lugar del texto `Periodo`. Sin una fecha de verdad no podremos usar la tabla calendario ni comparar con el año anterior.

**Paso a paso:**
1. *Inicio → Obtener datos → Texto o CSV* → selecciona `data\real_ERP.csv` → *Abrir*.
2. En la ventana de vista previa, comprueba:
   - *Origen del archivo*: **65001: Unicode (UTF-8)**.
   - *Delimitador*: **Punto y coma**.
   - Debe verse en 4 columnas. Pulsa **Transformar datos**, no *Cargar*. Así se abre el Editor de Power Query.
3. **Ponle nombre:** en el panel derecho (*Configuración de la consulta → Propiedades → Nombre*) cambia `real_ERP` por **`fReal`**.
4. **Borra el paso automático de tipos:** en *Pasos aplicados* (panel derecho) verás `Origen`, `Encabezados promovidos` y `Tipo cambiado`. Pasa el ratón por encima de `Tipo cambiado` y pulsa la **X**. ⚠️ Borra solo ese: si quitas `Encabezados promovidos`, los nombres de columna vuelven a la primera fila. Los tipos los pondremos nosotros al final. Es una buena costumbre: el paso automático a veces se equivoca, por ejemplo convirtiendo códigos como "01" en el número 1.
5. **Crea la columna `Fecha`:** *Agregar columna → Columna personalizada*.
   - Nombre de la nueva columna: `Fecha`
   - Fórmula (bórrale el `=` inicial si lo duplica):
     ```m
     #date(Number.FromText(Text.Start([Periodo], 4)), Number.FromText(Text.End([Periodo], 2)), 1)
     ```
   - Qué hace: `Text.Start([Periodo], 4)` coge los 4 primeros caracteres («2025»), `Text.End([Periodo], 2)` los 2 últimos («01»), `Number.FromText` los convierte en números y `#date(año, mes, 1)` construye la fecha 01/01/2025.
6. **Tipos de datos:** haz clic en el icono que hay a la izquierda del nombre de cada columna, en la cabecera:
   - `Fecha` → **Fecha**
   - `IdCuenta` e `IdLinea` → **Texto**
   - `Importe` → **Número decimal fijo** (es el tipo correcto para dinero)
7. **Quita `Periodo`:** clic derecho en la cabecera de `Periodo` → **Quitar**.
8. ✅ **Comprueba:** abajo a la izquierda debe poner **«4 COLUMNAS, 231 FILAS»**. La columna `Fecha` muestra fechas tipo 01/01/2025, sin errores.

### 1.2 `fPresupuesto`: el presupuesto (archivo `presupuesto_2026.xlsx`)

**Qué hay en el archivo:** el formato típico de un Excel de controller, con **una fila por cuenta y línea y los 12 meses en columnas** (`ene`, `feb`, … `dic`). Son 11 filas × 12 meses.
**Qué tiene que salir:** el mismo formato que `fReal` (`Fecha · IdCuenta · IdLinea · Importe`), **una fila por mes**: 11 × 12 = 132 filas. Si las dos tablas tienen el mismo formato, real y presupuesto se pueden comparar.

**Paso a paso:**
1. Sin salir del editor: *Inicio → Nuevo origen → Libro de Excel* → `data\presupuesto_2026.xlsx`.
2. En el *Navegador*, marca la hoja **`Ppto2026`** → **Aceptar**.
3. Renombra la consulta a **`fPresupuesto`**. Si arriba ves `Column1`, `Column2`… en lugar de `IdCuenta`, `IdLinea`, `ene`…, ve a *Inicio → Usar la primera fila como encabezado*. Después borra el paso `Tipo cambiado`, como antes.
4. **Despivota los meses:** selecciona la columna `IdCuenta`, mantén **Ctrl** y selecciona `IdLinea` → clic derecho en una de las dos cabeceras → **Anular dinámica de otras columnas**.
   - Resultado: 4 columnas en lugar de 14: `IdCuenta`, `IdLinea`, `Atributo` (con los valores ene, feb…) y `Valor`.
5. Renombra con doble clic en la cabecera: `Atributo` → **`Mes`** y `Valor` → **`Importe`**.
6. **Crea `Fecha`:** *Agregar columna → Columna personalizada*, con el nombre `Fecha`:
   ```m
   #date(2026, List.PositionOf({"ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"}, [Mes]) + 1, 1)
   ```
   - Qué hace: `List.PositionOf` busca el texto del mes en la lista y devuelve su posición empezando en 0 (ene = 0, feb = 1…). Por eso se suma 1. Es más limpio que hacer 12 veces «Reemplazar valores».
7. Tipos: `Fecha` → Fecha · `IdCuenta` e `IdLinea` → Texto · `Importe` → Número decimal fijo.
8. Quita la columna `Mes` (clic derecho → Quitar).
9. ✅ **Comprueba:** **«4 COLUMNAS, 132 FILAS»**.

### 1.3 Los maestros: `dCuenta`, `dLinea`, `dEscenario` y `fDrivers` (archivo `maestros.xlsx`)

1. *Inicio → Nuevo origen → Libro de Excel* → `data\maestros.xlsx`.
2. En el *Navegador*, marca la casilla **«Seleccionar varios elementos»** y marca las 4 hojas: `Cuentas`, `Lineas`, `Escenarios` y `Drivers` → **Aceptar**. Se crean 4 consultas de golpe.
3. Renómbralas: `Cuentas` → **`dCuenta`** · `Lineas` → **`dLinea`** · `Escenarios` → **`dEscenario`** · `Drivers` → **`fDrivers`**.
4. **Comprueba los encabezados** en cada una: si las columnas se llaman `Column1`, `Column2`…, ve a *Inicio → Usar la primera fila como encabezado*. En *Pasos aplicados* tiene que aparecer «Encabezados promovidos» debajo de «Navegación».
5. En cada una, borra `Tipo cambiado` y pon los tipos a mano:

| Consulta | Columnas y tipos |
|---|---|
| `dCuenta` | `Orden` → Número entero · `IdCuenta`, `Cuenta`, `Tipo`, `GrupoDriver` → Texto |
| `dLinea` | Todas → Texto |
| `dEscenario` | `Orden` → Número entero · `Escenario`, `Descripcion` → Texto |
| `fDrivers` | `Escenario`, `GrupoDriver` → Texto · `Variacion` → **Número decimal** |

En `dCuenta` verás que `GrupoDriver` está vacío (null) en las filas de subtotal (Margen bruto, EBITDA, EBIT). Es correcto: los subtotales no tienen datos propios, se calculan.

### 1.4 Cargar al modelo
*Inicio → **Cerrar y aplicar***. En la vista de tabla (icono de cuadrícula, a la izquierda de Power BI) deben aparecer las 6 tablas.

✅ **Control de la fase 1:** `fReal` = **231** filas · `fPresupuesto` = **132** · `dCuenta` = 10 · `dLinea` = 4 · `dEscenario` = 3 · `fDrivers` = 15.

### 1.5 (Recomendado para GitHub) Ruta relativa con un parámetro
Ahora mismo cada consulta tiene escrita la ruta de **tu** ordenador (`C:\Users\…\data\`). Si alguien clona tu repositorio, no le funcionará. Para arreglarlo:
1. *Transformar datos* → *Inicio → Administrar parámetros → Nuevo* → Nombre **`RutaDatos`** · Tipo **Texto** · Valor actual: la ruta de tu carpeta `data` **terminada en `\`**, por ejemplo `C:\GitHub\pbi-finanzas\05-rolling-forecast\data\`.
2. En cada consulta: *Inicio → Editor avanzado* → busca la ruta escrita entre comillas y sustitúyela así:
   - Antes: `File.Contents("C:\GitHub\...\data\real_ERP.csv")`
   - Después: `File.Contents(RutaDatos & "real_ERP.csv")`
3. En el README explica: «para abrir el proyecto, cambia el parámetro `RutaDatos` por tu ruta».

### 1.6 Si te atascas: el código M completo de cada consulta
Lo que haces con clics, Power Query lo escribe en lenguaje M. Puedes verlo en *Inicio → Editor avanzado*. Si algo no te sale, abre el editor avanzado de esa consulta, borra todo y pega la solución. Si no has hecho el paso 1.5, cambia `RutaDatos & "…"` por la ruta completa entre comillas.

**fReal**
```m
let
    Origen   = Csv.Document(File.Contents(RutaDatos & "real_ERP.csv"), [Delimiter = ";", Encoding = 65001]),
    Encabez  = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    ConFecha = Table.AddColumn(Encabez, "Fecha", each
                  #date(Number.FromText(Text.Start([Periodo], 4)), Number.FromText(Text.End([Periodo], 2)), 1), type date),
    Tipos    = Table.TransformColumnTypes(ConFecha, {{"IdCuenta", type text}, {"IdLinea", type text}, {"Importe", Currency.Type}}),
    Final    = Table.RemoveColumns(Tipos, {"Periodo"})
in
    Final
```

**fPresupuesto**
```m
let
    Origen    = Excel.Workbook(File.Contents(RutaDatos & "presupuesto_2026.xlsx"), null, true),
    Hoja      = Origen{[Item = "Ppto2026", Kind = "Sheet"]}[Data],
    Encabez   = Table.PromoteHeaders(Hoja, [PromoteAllScalars = true]),
    Despivot  = Table.UnpivotOtherColumns(Encabez, {"IdCuenta", "IdLinea"}, "Mes", "Importe"),
    Meses     = {"ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"},
    ConFecha  = Table.AddColumn(Despivot, "Fecha", each #date(2026, List.PositionOf(Meses, [Mes]) + 1, 1), type date),
    Tipos     = Table.TransformColumnTypes(ConFecha, {{"IdCuenta", type text}, {"IdLinea", type text}, {"Importe", Currency.Type}}),
    Final     = Table.RemoveColumns(Tipos, {"Mes"})
in
    Final
```

**dCuenta** (las otras tres hojas siguen el mismo patrón; solo cambian el nombre de la hoja y los tipos)
```m
let
    Origen   = Excel.Workbook(File.Contents(RutaDatos & "maestros.xlsx"), null, true),
    Hoja     = Origen{[Item = "Cuentas", Kind = "Sheet"]}[Data],
    Encabez  = Table.PromoteHeaders(Hoja, [PromoteAllScalars = true]),
    Tipos    = Table.TransformColumnTypes(Encabez, {
                  {"Orden", Int64.Type}, {"IdCuenta", type text}, {"Cuenta", type text},
                  {"Tipo", type text}, {"GrupoDriver", type text}})
in
    Tipos
```

💡 Mejora para el README: el año 2026 de `fPresupuesto` está escrito a mano. Puedes sacarlo de un parámetro o del nombre de la hoja.

## FASE 2 · Modelo

### 2.1 Calendario (tiene que llegar hasta 2027, porque el forecast vive ahí)
```dax
dCalendario =
ADDCOLUMNS (
    SELECTCOLUMNS ( CALENDAR ( DATE ( 2025, 1, 1 ), DATE ( 2027, 12, 31 ) ), "Fecha", [Date] ),
    "Año",       YEAR ( [Fecha] ),
    "MesNum",    MONTH ( [Fecha] ),
    "Mes",       FORMAT ( [Fecha], "mmm" ),
    "AñoMes",    FORMAT ( [Fecha], "yyyy-mm" ),
    "InicioMes", DATE ( YEAR ( [Fecha] ), MONTH ( [Fecha] ), 1 )
)
```
**Márcala como tabla de fechas.** Aquí es obligatorio: más abajo te explico por qué. Después: `Mes` ordenado por `MesNum`.

### 2.2 Relaciones
Hay que crear **6 relaciones**: cada tabla de hechos (`fReal` y `fPresupuesto`) se une con las tres dimensiones (`dCalendario`, `dCuenta` y `dLinea`).

**Cómo crearlas (opción A, arrastrando):**
1. Ve a la **vista de modelo**, el tercer icono de la barra izquierda (tres cajitas unidas).
2. Arrastra el campo `Fecha` de **`fReal`** (tabla de hechos) y suéltalo sobre el campo `Fecha` de **`dCalendario`** (dimensión).
3. En la ventana que se abre, `fReal` aparece **arriba** y `dCalendario` **abajo**. Comprueba: *Cardinalidad* = **Varios a uno (\*:1)** y *Dirección del filtro cruzado* = **Única** → *Aceptar*.
4. Repite con las demás, arrastrando siempre **desde la tabla de hechos hacia la dimensión**.

⚠️ **Si te sale el error «La columna … contiene un valor duplicado … no se permite para las columnas del lado uno»**, es que la relación está al revés: la tabla de hechos ha quedado abajo. Cambia la cardinalidad a **Uno a varios (1:\*)** y se arregla. La regla es que el **1** va siempre en la dimensión y el **\*** en la tabla de hechos, porque en `fReal` cada fecha se repite (una fila por cuenta y línea).

**Opción B:** *Modelado → Administrar relaciones → Nueva*. Arriba eliges la **tabla de hechos** y su columna; abajo, la **dimensión** y la suya. Mismos ajustes.

| # | Tabla de hechos (lado «varios») | Columna | Dimensión (lado «uno») | Columna |
|---|---|---|---|---|
| 1 | `fReal` | `Fecha` | `dCalendario` | `Fecha` |
| 2 | `fReal` | `IdCuenta` | `dCuenta` | `IdCuenta` |
| 3 | `fReal` | `IdLinea` | `dLinea` | `IdLinea` |
| 4 | `fPresupuesto` | `Fecha` | `dCalendario` | `Fecha` |
| 5 | `fPresupuesto` | `IdCuenta` | `dCuenta` | `IdCuenta` |
| 6 | `fPresupuesto` | `IdLinea` | `dLinea` | `IdLinea` |

⚠️ **Revisa las relaciones automáticas:** al cargar, Power BI crea algunas solo cuando ve columnas con el mismo nombre. En *Administrar relaciones*, no dupliques las que ya estén. **Si hay una entre `dEscenario` y `fDrivers`, elimínala**: estas dos tablas tienen que quedar sin ninguna línea.

✅ El diagrama debe tener **6 líneas** y `dEscenario` y `fDrivers` sueltas.

📘 **¿Por qué desconectadas?** El escenario no filtra ningún dato que exista: modifica **un cálculo**. La segmentación de escenario solo sirve para que la medida lea qué ha elegido el usuario con `SELECTEDVALUE`. Es el patrón de las tablas de supuestos en FP&A.

`dCuenta[Cuenta]` → *Ordenar por columna* → `Orden`.

### 2.3 Parámetro de simulación
*Modelado → Nuevo parámetro → Intervalo numérico*:
- Nombre `Ajuste Ventas` · Número decimal · Mínimo `-0,1` · Máximo `0,1` · Incremento `0,01` · Predeterminado `0`.
- Power BI crea una tabla, una segmentación y una medida (con un nombre parecido a `Valor de Ajuste Ventas`). **Renombra la medida a `Ajuste Ventas Valor`** y dale formato de %.

## FASE 3 · DAX

### 3.1 Básicas
```dax
Real = SUM ( fReal[Importe] )

Ppto = SUM ( fPresupuesto[Importe] )

Último Mes Real =
CALCULATE ( MAX ( fReal[Fecha] ), REMOVEFILTERS () )
```
`Último Mes Real` devuelve 01/09/2026. Cuando cargues octubre, el forecast se desplaza solo: **por eso es un rolling forecast**.

### 3.2 Forecast (la medida importante del proyecto)
```dax
Forecast =
VAR vUltimoReal   = [Último Mes Real]
VAR vFinHorizonte = EDATE ( vUltimoReal, 12 )
VAR vEscenario    = SELECTEDVALUE ( dEscenario[Escenario], "Base" )
VAR vGVentas =
    LOOKUPVALUE ( fDrivers[Variacion], fDrivers[Escenario], vEscenario, fDrivers[GrupoDriver], "Ventas" )
        + [Ajuste Ventas Valor]
VAR vMesesFuturos =
    FILTER (
        VALUES ( dCalendario[InicioMes] ),
        dCalendario[InicioMes] > vUltimoReal
            && dCalendario[InicioMes] <= vFinHorizonte
    )
RETURN
    SUMX (
        vMesesFuturos,
        SUMX (
            VALUES ( dCuenta[GrupoDriver] ),
            VAR vGrupo = dCuenta[GrupoDriver]
            VAR vG =
                LOOKUPVALUE ( fDrivers[Variacion], fDrivers[Escenario], vEscenario, fDrivers[GrupoDriver], vGrupo )
            VAR vFactor =
                SWITCH (
                    vGrupo,
                    "Ventas",          1 + vGVentas,
                    "Coste de ventas", ( 1 + vGVentas ) * ( 1 + vG ),
                    1 + vG
                )
            VAR vBaseAnoAnterior =
                CALCULATE ( [Real], SAMEPERIODLASTYEAR ( dCalendario[Fecha] ) )
            RETURN
                vBaseAnoAnterior * vFactor
        )
    )
```
📘 **Cómo funciona, por capas:**
1. **`SELECTEDVALUE ( dEscenario[Escenario], "Base" )`** lee la segmentación. Si no hay nada seleccionado, o hay más de un escenario, usa «Base». Esto es lo que hace funcionar una tabla desconectada.
2. **`LOOKUPVALUE`** busca en `fDrivers` como un BUSCARV con dos criterios.
3. **`vMesesFuturos`** se queda con los meses visibles en el contexto que caen después del último real y dentro del horizonte de 12 meses. En una tarjeta del año 2026 salen oct, nov y dic; en una columna de enero de 2025, ninguno, y el forecast queda en blanco.
4. **Primer `SUMX`, mes a mes:** hace falta porque cada mes mira **su** mismo mes del año anterior.
5. **Segundo `SUMX`, grupo a grupo:** cada grupo de cuentas tiene su propio factor.
6. **`SAMEPERIODLASTYEAR`** dentro de `CALCULATE`: la transición de contexto convierte el mes actual de la iteración en un filtro, y esta función lo desplaza un año atrás.

⚠️ **Por qué era obligatorio marcar la tabla de fechas:** en una matriz con la columna *Año = 2027*, `SAMEPERIODLASTYEAR` devuelve fechas de 2026, pero el filtro *Año = 2027* seguiría activo y el resultado sería… vacío. Con la tabla marcada como tabla de fechas, DAX **quita automáticamente** el resto de filtros del calendario cuando filtras su columna de fecha. Si te sale el forecast en blanco en 2027, es esto.

⚠️ En los nombres de **variables** (`VAR`) no uses ñ ni tildes: DAX da el error «token no válido». En medidas y columnas sí se pueden usar, porque van entre corchetes.

✅ **Control:** forecast de Ventas en oct-2026 (escenario base, ajuste 0) = **8.293.177 €**.

### 3.3 Real + Forecast
```dax
Cierre = [Real] + [Forecast]
```
Real y Forecast nunca coinciden en el mismo mes: uno está vacío cuando el otro tiene valor. En 2026 esta medida da el **cierre estimado del año**: real de enero a septiembre más forecast de octubre a diciembre.

### 3.4 Subtotales de la cuenta de resultados (patrón FP&A clásico)
Margen bruto, EBITDA y EBIT no tienen datos: son **filas de subtotal**. Las calculamos sumando todas las cuentas de detalle que están por encima en el orden.

```dax
PyG Cierre =
VAR vTipo  = SELECTEDVALUE ( dCuenta[Tipo] )
VAR vOrden = SELECTEDVALUE ( dCuenta[Orden] )
RETURN
    IF (
        vTipo = "Subtotal",
        CALCULATE ( [Cierre], REMOVEFILTERS ( dCuenta ), dCuenta[Orden] < vOrden, dCuenta[Tipo] = "Detalle" ),
        [Cierre]
    )
```
Crea **`PyG Real`** y **`PyG Ppto`** con la misma estructura, cambiando `[Cierre]` por `[Real]` o `[Ppto]`.
📘 Funciona porque los gastos están en negativo: «todo lo que está por encima del EBITDA» sumado **es** el EBITDA.

```dax
Desv. vs Ppto = [PyG Cierre] - [PyG Ppto]

Desv. % vs Ppto = DIVIDE ( [Desv. vs Ppto], ABS ( [PyG Ppto] ) )

PyG Real Año Anterior = CALCULATE ( [PyG Real], SAMEPERIODLASTYEAR ( dCalendario[Fecha] ) )
```
❓ ¿Por qué `ABS` en el denominador? *Prueba sin él en la fila de coste de ventas y mira el signo.*

### 3.5 KPIs para tarjetas
```dax
Ventas Cierre    = CALCULATE ( [PyG Cierre], dCuenta[IdCuenta] = "VEN" )
EBITDA Cierre    = CALCULATE ( [PyG Cierre], dCuenta[IdCuenta] = "EBITDA" )
EBITDA Ppto      = CALCULATE ( [PyG Ppto],   dCuenta[IdCuenta] = "EBITDA" )
Margen EBITDA %  = DIVIDE ( [EBITDA Cierre], [Ventas Cierre] )
Gap EBITDA vs Ppto = [EBITDA Cierre] - [EBITDA Ppto]

Forecast 12M =
CALCULATE ( [Forecast], REMOVEFILTERS ( dCalendario ) )
```
Para comprobar el forecast a 12 meses de una línea concreta de la cuenta de resultados: `CALCULATE ( [Forecast 12M], dCuenta[IdCuenta] = "VEN" )`, o para el EBITDA `CALCULATE ( [Forecast 12M], dCuenta[Tipo] = "Detalle", dCuenta[Orden] < 80 )`.

📘 `EBITDA Cierre` funciona porque, al filtrar `IdCuenta = "EBITDA"`, `PyG Cierre` ve una fila de tipo Subtotal y aplica la lógica de subtotales. Reutilizas la medida en vez de reescribirla.

### 3.6 Validación en la vista de consultas DAX
```dax
EVALUATE
SUMMARIZECOLUMNS (
    dEscenario[Escenario],
    TREATAS ( { 2026 }, dCalendario[Año] ),
    "EBITDA Cierre", [EBITDA Cierre],
    "EBITDA Ppto",   [EBITDA Ppto],
    "Gap",           [Gap EBITDA vs Ppto]
)
```
✅ **Cifras de control** (ajuste = 0 %; pueden diferir en ±1 € por redondeos):
| | Ventas | EBITDA |
|---|---|---|
| Real 2025 | 83.223.947 | 13.015.381 |
| Real ene–sep 2026 | 63.700.917 | 8.926.441 |
| Presupuesto 2026 | 91.400.000 | 15.206.596 |
| **Cierre 2026 · Base** | 88.548.348 | **12.886.141** |
| Cierre 2026 · Optimista | 89.954.807 | 13.518.872 |
| Cierre 2026 · Pesimista | 85.969.841 | 11.742.718 |
| Forecast 12M (oct-26 → sep-27) · Base | 92.370.403 | 12.884.248 |

## FASE 4 · Informe (3 páginas)

### 4.0 Antes de empezar: las partes de la pantalla
Trabajas en la **vista de informe** (primer icono de la barra izquierda). Tiene 4 zonas:

| Zona | Dónde | Para qué |
|---|---|---|
| **Lienzo** | Centro | La página en blanco donde colocas los gráficos |
| **Visualizaciones** | Derecha | Arriba, los iconos de tipos de gráfico. Debajo, dos pestañas: **Generar objeto visual** (los «huecos» donde arrastras campos: Eje, Valores, Filas…) y **Formato** (el icono del pincel: colores, títulos, tamaños) |
| **Datos** | Derecha del todo | Tus tablas y medidas. De aquí arrastras los campos |
| **Filtros** | Entre el lienzo y Visualizaciones (puede estar plegado, con una flecha `<`) | Filtros de *este objeto visual*, *esta página* o *todas las páginas* |

**El gesto básico, siempre igual:**
1. Haz clic en una zona vacía del lienzo, para no tener nada seleccionado.
2. Haz clic en el icono del tipo de gráfico en *Visualizaciones*. Aparece un recuadro vacío en el lienzo.
3. Con ese recuadro seleccionado, **arrastra campos** desde *Datos* a los huecos de *Generar objeto visual*.
4. Mueve y redimensiona el recuadro con el ratón.
5. Para darle formato: con el objeto visual seleccionado, pestaña **Formato** (pincel).

Abajo tienes las pestañas de las páginas. **Doble clic** sobre «Página 1» para renombrarla y **+** para añadir otra.

### 4.1 Preparación: dos medidas de color y una de ventas
Para pintar en rojo o verde según el valor, Power BI usa medidas que devuelven un **código de color**. Créalas en `_Medidas` (cada una en su *Nueva medida*):

```
Color Gap = IF ( [Gap EBITDA vs Ppto] < 0, "#C0392B", "#1E8449" )
```
```
Color Desviacion = IF ( [Desv. vs Ppto] < 0, "#C0392B", "#1E8449" )
```
```
Color Fondo PyG = IF ( SELECTEDVALUE ( dCuenta[Tipo] ) = "Subtotal", "#E8EEF4" )
```
```
Ventas Ppto = CALCULATE ( [PyG Ppto], dCuenta[IdCuenta] = "VEN" )
```
`#C0392B` es rojo, `#1E8449` es verde y `#E8EEF4` es un gris azulado claro para las filas de subtotal.

---

### 4.2 Página 1 · «Resumen ejecutivo»
Renombra la página: doble clic en «Página 1» → `Resumen`.

**Paso 1 · Filtro de año para toda la página** (importante: sin él, los KPI de «cierre» sumarían todos los años)
1. Haz clic en una zona vacía del lienzo.
2. En el panel *Filtros*, arrastra `dCalendario[Año]` a la zona **«Filtros en esta página»**.
3. Marca solo **2026**.

**Paso 2 · Las 4 tarjetas**
1. Clic en vacío → en *Visualizaciones*, icono **Tarjeta** (un rectángulo con «123»). Si tu versión tiene «Tarjeta (nueva)», también vale.
2. Arrastra `Ventas Cierre` al hueco **Campos** (o **Datos**).
3. Pincel → **Valor de la llamada** (o *Valores*) → *Unidades de visualización*: **Millones** · *Decimales*: **1**.
4. Pincel → **General → Título**: actívalo y escribe «Ventas cierre 2026».
5. Repite con `EBITDA Cierre`, `Margen EBITDA %` (sin unidades, 1 decimal) y `Gap EBITDA vs Ppto`.
6. **Gap en rojo:** selecciona la tarjeta del Gap → Pincel → *Valor de la llamada* → junto a *Color*, pulsa el icono **fx** → *Estilo de formato*: **Valor de campo** → *¿En qué campo deberíamos basarnos?*: **`Color Gap`** → *Aceptar*.
7. Colócalas en fila en la parte de arriba de la página.

**Paso 3 · Segmentación de escenario**
1. Clic en vacío → icono **Segmentación de datos** (un embudo con una tabla).
2. Arrastra `dEscenario[Escenario]` a **Campo**.
3. Pincel → *Configuración de segmentación* → *Opciones* → **Estilo: Mosaico** (botones) y **Selección única: activado**.
4. Selecciona «Base». Prueba a cambiar a «Optimista»: las tarjetas deben cambiar.

**Paso 4 · Deslizador de ajuste de ventas**
1. Si Power BI ya te creó la segmentación al crear el parámetro, úsala. Si no: clic en vacío → **Segmentación de datos** → arrastra `'Ajuste Ventas'[Ajuste Ventas]` (o `[Value]` si lo hiciste con DAX).
2. Pincel → *Configuración de segmentación* → *Estilo*: **Valor único**. Aparece el deslizador.
3. Prueba a moverlo a +5 %: las ventas y el EBITDA de cierre suben.

**Paso 5 · Matriz de escenarios** (los tres escenarios uno al lado de otro)
1. Clic en vacío → icono **Matriz** (una tabla con una cuadrícula).
2. Arrastra `dEscenario[Escenario]` a **Columnas**.
3. Arrastra a **Valores**, en este orden: `Ventas Cierre`, `EBITDA Cierre`, `Margen EBITDA %` y `Gap EBITDA vs Ppto`.
4. Así sale «al revés», con las medidas en columnas. Para ponerlas en filas: Pincel → **Valores** → *Opciones* → **Cambiar valores a filas**: activado. En algunas versiones se llama «Mostrar en filas».
5. Pincel → *Subtotales de columna*: **desactivado**.
6. **Que la segmentación no la filtre:** si eliges «Base», la matriz solo mostraría Base. Para evitarlo, selecciona la **segmentación de escenario** → en la cinta, **Formato → Editar interacciones**. Aparecen unos iconos encima de cada objeto visual: en la matriz, pulsa el **⊘ (Ninguno)**. Vuelve a pulsar *Editar interacciones* para salir.

✅ La matriz debe mostrar un EBITDA de cierre de 12,9 M (Base), 13,5 M (Optimista) y 11,7 M (Pesimista).

---

### 4.3 Página 2 · «Cuenta de resultados»
Pulsa **+** abajo → renombra a `PyG`. Repite el **filtro de página Año = 2026** (paso 1 de 4.2).

**Paso 1 · La matriz**
1. Clic en vacío → **Matriz**.
2. Arrastra `dCuenta[Cuenta]` a **Filas**.
3. Arrastra a **Valores**: `PyG Real Año Anterior`, `PyG Ppto`, `PyG Cierre`, `Desv. vs Ppto` y `Desv. % vs Ppto`.
4. Comprueba el orden de las filas: Ventas, Coste de ventas, Margen bruto… Si salen por orden alfabético, revisa el paso de la Fase 2: `dCuenta[Cuenta]` → *Ordenar por columna* → `Orden`. Y en la matriz, haz clic en los «…» del objeto visual → *Ordenar por* → **Cuenta** → *Orden ascendente*.
5. Pincel → *Subtotales de fila*: **desactivado**. La fila «Total» no tiene sentido en una cuenta de resultados: ya tienes el EBIT.

**Paso 2 · Renombra las columnas** (sin cambiar las medidas)
En *Generar objeto visual*, haz doble clic sobre cada campo de *Valores* y escribe un nombre corto: `Real 2025`, `Ppto 2026`, `Cierre 2026`, `Desv. €` y `Desv. %`.

**Paso 3 · Desviaciones en rojo o verde**
1. En *Valores*, haz clic en la flecha ▾ junto a `Desv. €` → **Formato condicional** → **Color de fuente**.
2. *Estilo de formato*: **Valor de campo** → campo: **`Color Desviacion`** → *Aceptar*.
3. Haz lo mismo con `Desv. %`, usando también `Color Desviacion`.

**Paso 4 · Subtotales destacados**
Para cada una de las 5 columnas: ▾ → **Formato condicional** → **Color de fondo** → *Valor de campo* → **`Color Fondo PyG`**. Margen bruto, EBITDA y EBIT quedarán con fondo gris claro.

**Paso 5 · Formato de números**
Pincel → *Valores* → unidades **Miles**, 0 decimales. Así se lee «88.548» en lugar de «88548348,39».

---

### 4.4 Página 3 · «Tendencia»
**+** → renombra a `Tendencia`. **No** pongas filtro de año: aquí queremos ver todos los meses.

**Paso 1 · Gráfico de líneas mensual**
1. Clic en vacío → icono **Gráfico de líneas**.
2. Arrastra `dCalendario[AñoMes]` al **Eje X**.
3. Arrastra `Real`, `Forecast` y `Ppto` al **Eje Y**.
4. **Filtra a ventas:** con el gráfico seleccionado, en *Filtros* → **«Filtros en este objeto visual»** → arrastra `dCuenta[Cuenta]` y marca solo **Ventas**.
5. **Forecast en discontinua:** Pincel → **Líneas** → en *Serie*, elige **Forecast** → *Estilo de línea*: **Discontinua**.
6. Pincel → *Eje Y* → unidades **Millones**.
7. Título: «Ventas mensuales: real, forecast y presupuesto».

Verás que la línea del real acaba en septiembre de 2026 y la del forecast empieza en octubre. El presupuesto solo existe en 2026.

💡 Si quieres ver el EBITDA en lugar de las ventas, duplica el gráfico (Ctrl+C, Ctrl+V) y en su filtro marca, en lugar de Ventas, todas las cuentas de detalle por encima del EBITDA: Ventas, Coste de ventas, Personal, Marketing, Alquileres y Otros gastos.

**Paso 2 · Barras de ventas por línea de negocio**
1. Clic en vacío → icono **Gráfico de barras agrupadas** (barras horizontales).
2. Arrastra `dLinea[Linea]` al **Eje Y**.
3. Arrastra `Ventas Cierre` y `Ventas Ppto` al **Eje X**.
4. *Filtros en este objeto visual*: `dCalendario[Año]` = **2026** y `dLinea[Linea]`: desmarca **Corporativo** (no tiene ventas).
5. Pincel → *Etiquetas de datos*: activadas, en millones.

---

### 4.5 Acabado (para que parezca de director financiero)
- **Tema:** *Vista → Temas* → elige uno sobrio (por ejemplo «Ejecutivo») o personaliza un color corporativo.
- **Título en cada página:** *Insertar → Cuadro de texto* → «Grupo Power Tower · Rolling forecast 2026».
- **Títulos que cuenten la conclusión** en lugar de describir: «El EBITDA de cierre queda 2,3 M€ por debajo del presupuesto» es mejor que «EBITDA por escenario».
- **Alinear:** selecciona varios objetos visuales con Ctrl → *Formato → Alinear*.
- **Guarda** (Ctrl+S) y haz una **captura de cada página** para la carpeta `img/` de tu GitHub.

✅ **Comprobación final:** en la página Resumen, con «Base» y ajuste 0 %, las tarjetas muestran 88,5 M de ventas, 12,9 M de EBITDA, un margen del 14,6 % y un gap de −2,3 M en rojo.

## FASE 5 · Hallazgos para el README
1. ¿Cuánto EBITDA falta para llegar al presupuesto en el escenario base? ¿Y en el optimista? ¿Hay algún escenario en el que se cumpla?
2. ¿Qué **línea de negocio** explica la desviación de ventas? ¿Y en costes, qué grupo?
3. **Sensibilidad:** mueve el deslizador a −5 % y a +5 %. ¿Cuántos euros de EBITDA de cierre 2026 vale cada 1 % de ventas? ¿Por qué el efecto es mucho mayor en el forecast a 12 meses que en el cierre de 2026?
4. Compara el margen EBITDA del forecast a 12 meses con el de 2025: ¿mejora o empeora y por qué? *(Pista: ¿qué crece más, las ventas o el coste?)*

## Retos extra (nivel intermedio-alto)
- **Grupo de cálculo** `Vista temporal` con los elementos *Mes* (`SELECTEDMEASURE()`) y *YTD* (`CALCULATE ( SELECTEDMEASURE (), DATESYTD ( dCalendario[Fecha] ) )`). Te ahorra duplicar todas las medidas en versión YTD.
- Drivers **por línea de negocio**: añade `IdLinea` a `fDrivers` y adapta el `LOOKUPVALUE`.
- Que el usuario edite los drivers: muévelos a un Excel aparte y documenta en el README cómo se cambia un supuesto y se actualiza el informe.
