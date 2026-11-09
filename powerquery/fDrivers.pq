let
    Origen = Excel.Workbook(File.Contents(RutaDatos & "maestros.xlsx"), null, true),
    Drivers_Sheet = Origen{[Item="Drivers",Kind="Sheet"]}[Data],
    #"Encabezados promovidos" = Table.PromoteHeaders(Drivers_Sheet, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos",{{"Variacion", type number}})
in
    #"Tipo cambiado"
