let
    Origen = Excel.Workbook(File.Contents(RutaDatos & "maestros.xlsx"), null, true),
    Cuentas_Sheet = Origen{[Item="Cuentas",Kind="Sheet"]}[Data],
    #"Encabezados promovidos" = Table.PromoteHeaders(Cuentas_Sheet, [PromoteAllScalars=true]),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Encabezados promovidos",{{"Orden", Int64.Type}})
in
    #"Tipo cambiado"
