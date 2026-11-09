let
    Origen = Excel.Workbook(File.Contents(RutaDatos & "maestros.xlsx"), null, true),
    Lineas_Sheet = Origen{[Item="Lineas",Kind="Sheet"]}[Data],
    #"Encabezados promovidos" = Table.PromoteHeaders(Lineas_Sheet, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos",{{"IdLinea", type text}, {"Linea", type text}, {"Descripcion", type text}})
in
    #"Tipo cambiado"
