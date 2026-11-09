let
    Origen = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i44FAA==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Columna1 = _t]),
    #"Tipo cambiado" = Table.TransformColumnTypes(Origen,{{"Columna1", type text}}),
    #"Columnas quitadas" = Table.RemoveColumns(#"Tipo cambiado",{"Columna1"})
in
    #"Columnas quitadas"
