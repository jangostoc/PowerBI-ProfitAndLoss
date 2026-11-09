let
    Origen = Excel.Workbook(File.Contents(RutaDatos & "maestros.xlsx"), null, true),
    Escenarios_Sheet = Origen{[Item="Escenarios",Kind="Sheet"]}[Data],
    #"Encabezados promovidos" = Table.PromoteHeaders(Escenarios_Sheet, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos",{{"Orden", Int64.Type}})
in
    #"Tipo cambiado"
