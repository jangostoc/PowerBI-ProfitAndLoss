let
    Origen = Csv.Document(File.Contents(RutaDatos & "real_ERP.csv"),[Delimiter=";", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Encabezados promovidos" = Table.PromoteHeaders(Origen, [PromoteAllScalars=true]),
    #"Personalizada agregada" = Table.AddColumn(#"Encabezados promovidos", "Fecha", each #date(Number.FromText(Text.Start([Periodo], 4)), Number.FromText(Text.End([Periodo], 2)), 1)),
    #"Tipo cambiado" = Table.TransformColumnTypes(#"Personalizada agregada",{{"Fecha", type date}}),
    #"Columnas quitadas" = Table.RemoveColumns(#"Tipo cambiado",{"Periodo"}),
    #"Tipo cambiado1" = Table.TransformColumnTypes(#"Columnas quitadas",{{"Importe", Currency.Type}})
in
    #"Tipo cambiado1"
