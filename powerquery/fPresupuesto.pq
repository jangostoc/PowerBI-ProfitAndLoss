let
    Origen = Excel.Workbook(File.Contents(RutaDatos & "presupuesto_2026.xlsx"), null, true),
    Ppto2026_Sheet = Origen{[Item="Ppto2026",Kind="Sheet"]}[Data],
    #"Encabezados promovidos" = Table.PromoteHeaders(Ppto2026_Sheet, [PromoteAllScalars=true]),
    #"Otras columnas con anulación de dinamización" = Table.UnpivotOtherColumns(#"Encabezados promovidos", {"IdCuenta", "IdLinea"}, "Atributo", "Valor"),
    #"Columnas con nombre cambiado" = Table.RenameColumns(#"Otras columnas con anulación de dinamización",{{"Valor", "Importe"}, {"Atributo", "Mes"}}),
    #"Personalizada agregada" = Table.AddColumn(#"Columnas con nombre cambiado", "Personalizado", each #date(2026, List.PositionOf({"ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"}, [Mes]) + 1, 1)),
    #"Columnas quitadas" = Table.RemoveColumns(#"Personalizada agregada",{"Mes"}),
    #"Columnas con nombre cambiado1" = Table.RenameColumns(#"Columnas quitadas",{{"Personalizado", "Fecha"}}),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Columnas con nombre cambiado1",{{"Importe", Currency.Type}, {"Fecha", type date}})
in
    #"Tipo cambiado"
