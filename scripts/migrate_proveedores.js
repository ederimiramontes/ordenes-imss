/**
 * migrate_proveedores.js
 * Migra PROVEEDORES_CAT del JS estático a la tabla proveedores_catalogo en Supabase.
 * Ejecutar UNA SOLA VEZ: node scripts/migrate_proveedores.js
 */

const SUPABASE_URL = 'https://igosubejkzrxgpuqmbpo.supabase.co';
const SUPABASE_ANON = 'sb_publishable_GCm3UUZIy7g13M9jcD7VvQ_bG2GhEi6';

const PROVEEDORES = [
  {"consecutivo":1,"razon_social":"Jose de Jesus Almendra Molina","rfc":"AEMJ921010MG9","domicilio":"Aquiles Serdan 4 Col. Granjas Fam.Div Norte Tijuana Baja California México","ret_isr":false},
  {"consecutivo":2,"razon_social":"JOSE AMEZCUA PEREZ","rfc":"AEPJ440830482","domicilio":"77","ret_isr":false},
  {"consecutivo":3,"razon_social":"Ramon Amezcua Pérez","rfc":"AEPR591002GM8","domicilio":"C. Serafin 3 Los Puestos Tlaquepaque Jalisco México 45638","ret_isr":false},
  {"consecutivo":4,"razon_social":"RAMON AMEZCUA PEREZ","rfc":"AEPR591003GM8","domicilio":"SERAFIN,3,LOS PUESTOS, CP 45638 TLAQUEPAQUE-TLAQUEPAQUE-JALISCO-MEXICO.","ret_isr":false},
  {"consecutivo":5,"razon_social":"FRANCISCO ACOSTA MENDOZA","rfc":"AOMF450126","domicilio":"AV. FELIPE ANGELES 1191 COL. BENITO JUAREZ MEXICALI BC México 21250","ret_isr":false},
  {"consecutivo":6,"razon_social":"ASESORIA Y PROVEEDORA DE EQUIPOS PARA LABORATORIO S.A. DE C.V.","rfc":"APE950801FJ4","domicilio":"AV MÉXICO 2522 FRACC. LADRÓN DE GUEVARA GUADALAJARA JALISCO MÉXICO 44600","ret_isr":false},
  {"consecutivo":7,"razon_social":"Anzher Solutions","rfc":"ASO060718JA1","domicilio":"Santa Martha 620 Buena Vista Tijuana Baja California México","ret_isr":false},
  {"consecutivo":8,"razon_social":"Maribel del Carmen Bayardo Guzman","rfc":"BAGM6705071M6","domicilio":"Av.Paseo Guaycura 4405 Ampliacion Guaycura Tijuana Baja California México 22214","ret_isr":false},
  {"consecutivo":9,"razon_social":"KAREN MONSERRAT BENDIMEZ PATTERSON","rfc":"BEPK7302165X4","domicilio":"AV. CARROCEROS 2098-A COL. BUROCRATA MEXICALI BAJA CALIFORNIA MÉXICO 21020","ret_isr":false},
  {"consecutivo":10,"razon_social":"CHAVIRA BONILLA HECTOR MANUEL","rfc":"CABH780411KP8","domicilio":"CALZADA CONSTITUCION Y CJON. SONORA 207 COL. RUIZ CORTINES SAN LUIS RIO COLORADO SONORA MEXICO 83439","ret_isr":false},
  {"consecutivo":11,"razon_social":"OCTAVIO CAMPOY FLORES","rfc":"CAFO730726QD7","domicilio":"LOMAS DEL MONTE 1610 FRACC. LOMAS DE AGUA CALIENTE TIJUANA BAJA CALIFORNIA MÉXICO 22440","ret_isr":false},
  {"consecutivo":12,"razon_social":"Caes Arquitectos SA de CV","rfc":"CAR170620TL7","domicilio":"C. Valentin Gomez Farias 1660 Col. Nueva Mexicali Baja California México 21100","ret_isr":false},
  {"consecutivo":13,"razon_social":"CARLOS ALBERTO CASTAÑOS VAZQUEZ","rfc":"CAVC711105DHA","domicilio":"OAXACA 801-2 COL. PUEBLO NUEVO MEXICALI BAJA CALIFORNIA MEXICO 21120","ret_isr":false},
  {"consecutivo":14,"razon_social":"CPS COMERCIALIZADORA DE PRODUCTOS Y PROVEEDORA DE SERVICIOS DE LIMPIEZA SA DE CV","rfc":"CCP1303022Y3","domicilio":"AV. TIBURON 508 EDIFICIO 2DO PISO MZ 53 LT23 FRACCIONAMIENTO COSTA DE ORO BOCA DEL RÍO VERACRUZ MÉXICO 94299","ret_isr":false},
  {"consecutivo":15,"razon_social":"CPS Comercializadora de Productos y Proveedora de Servicios de Limpieza S.A. de C.V.","rfc":"CCP130322Y3","domicilio":"Calle Venus 32 Jardines de Mocambo Boca del Rio Veracruz México","ret_isr":false},
  {"consecutivo":16,"razon_social":"Carlos Cervantes Rodriguez","rfc":"CER430716C3A","domicilio":"C. 6ta 2 Cienega Poniente Tijuana Baja California México 22114","ret_isr":false},
  {"consecutivo":17,"razon_social":"CTG Ingenieria y Construcción, S.A. de C.V.","rfc":"CIC170531DI1","domicilio":"Puerto México 47 Col. San Jeronimo Chicahualco Metepec México 22210","ret_isr":false},
  {"consecutivo":18,"razon_social":"JAVIER FRANCISCO CORTEZ BARAJAS","rfc":"COBJ860113SX2","domicilio":"AV. RIO SANTA MARIA 1962 VALLE DORADO MEXICALI BAJA CALIFORNIA MEXICO 21399","ret_isr":false},
  {"consecutivo":19,"razon_social":"SINHUE COVARRUBIAS JUAREZ","rfc":"COJS810722NU6","domicilio":"EUCARIO LEON 1039 CUCAPAH INFONAVIT MEXICALI BAJA CALIFORNIA 21340","ret_isr":false},
  {"consecutivo":20,"razon_social":"Manuel Humberto Covarrubias Lopez","rfc":"COLM690527793A","domicilio":"Paseo del bosque 26236 Int. 5 Col. Residencial del Bosque Tijuana Baja California 22204","ret_isr":false},
  {"consecutivo":21,"razon_social":"DISTRIBUIDORA ELECTRICA DIAZ ARMENTA S.A. DE C.V.","rfc":"DED840131HZ4","domicilio":"CALLE 6 Y CALLEJON MADERO SN COL. COMERCIAL SAN LUIS RIO COLORADO SONORA MEXICO 83449","ret_isr":false},
  {"consecutivo":22,"razon_social":"Distribuidora Internacional Hospitalaria","rfc":"DIH020515AZA","domicilio":"C. fresa Mz 1 Lote 17 S/N Col. Granjas Independencia Ecatepec de Morelos México 55290","ret_isr":false},
  {"consecutivo":23,"razon_social":"DISTRIBUIDORA INTERNACIONAL HOSPITALARIA S.A. DE C.V.","rfc":"DIK020515AZA","domicilio":"CLL. FRESA MZ. 1 LOTE 17 SN COL. GRANJAS INDEPENDENCIA ECATEPEC ESTADO DE MÉXICO MÉXICO 55290","ret_isr":false},
  {"consecutivo":24,"razon_social":"JESUS ABRAHAM DIMAS MARTINEZ","rfc":"DIMJ9201167GA","domicilio":"CALLE PERU 702 AVIACIÓN SAN LUIS RIO COLORADO SONORA MÉXICO 83470","ret_isr":false},
  {"consecutivo":25,"razon_social":"DP3 MEXICALI SA DE CV","rfc":"DME101027L32","domicilio":"AV.JESUS CARRANZA 128 COL. BENITO JUAREZ MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":false},
  {"consecutivo":26,"razon_social":"DRAGER MEDICAL MEXICO SA DE CV","rfc":"DMM040206NG8","domicilio":"AV.SANTA FE 170 5-4-14 COL. LOMAS DE SANTA FE CIUDAD DE MÉXICO CDMX MÉXICO 1210","ret_isr":false},
  {"consecutivo":27,"razon_social":"DISTRIBUIDORA DE RODAMIENTOS Y COMPONENTES INDUSTRIALES S DE RL DE CV","rfc":"DRC0801282S2","domicilio":"CALZADA ROBLEDO INDUSTRIAL 363 COL. EL ROBLEDO MEXICALI BAJA CALIFORNIA MÉXICO 21384","ret_isr":false},
  {"consecutivo":28,"razon_social":"ESI & SUPPLY S R.L DE C.V.","rfc":"EAS2104128M8","domicilio":"ARQUITECTOS 2201 UNIVERSITARIO MEXICALI BAJA CALIFORNIA MEXICO 21180","ret_isr":false},
  {"consecutivo":29,"razon_social":"ELEVADORES EV INTERNACIONAL","rfc":"EEI000627D47","domicilio":"AV. TODOS LOS SANTOS 7560 COL.PARQUE INDUSTRIAL PACIFICO TIJUANA BAJA CALIFORNIA MÉXICO 22643","ret_isr":false},
  {"consecutivo":30,"razon_social":"ELEVADORES OTIS S DE RL DE CV","rfc":"EOT631205877","domicilio":"AV. REVOLUCION 507 PISO 3 COL. SAN PEDRO DE LOS PINOS DELEG. BENITO JUAREZ CD. DE MEXICO MÉXICO 3800","ret_isr":false},
  {"consecutivo":31,"razon_social":"ELEVADORES OTIS S DE RL DE CV (Sucursal)","rfc":"EOT631205877","domicilio":"CALLE 10 145 2DO PISO COL. SAN PEDRO DE LOS PINOS DELEGACIÓN ALVARO OBREGÓN CIUDAD DE MÉXICO MÉXICO 1180","ret_isr":false},
  {"consecutivo":32,"razon_social":"ENRIQUEZ SERVICIOS, OBRAS Y SUMINISTROS, S.A. DE C.V.","rfc":"ESO0908286F2","domicilio":"NEZAHUALCOYOTL COL. BOSQUES DE ARAGON C.P. 57170 ESTADO DE MÉXICO MÉXICO","ret_isr":false},
  {"consecutivo":33,"razon_social":"ELEKTRONIK UND ASTRONOMIE, S.A. DE C.V.","rfc":"EUA151127H88","domicilio":"CALLE LIBERTAD 1870 A AMERICANA GUADALAJARA JALISCO MEXICO 44160","ret_isr":false},
  {"consecutivo":34,"razon_social":"Francisco Miguel Flores Delgado","rfc":"FODF660201UX0","domicilio":"Paseos del Pacifico 3 Paseos del Pacifico-La Presa Tijuana Baja California México 22644","ret_isr":false},
  {"consecutivo":35,"razon_social":"ALEJANDRO GARCIA LUNA","rfc":"GALA620730PI2","domicilio":"AV.RIO BLANCO 3248 COL. GONZÁLEZ ORTEGA NORTE MEXICALI BAJA CALIFORNIA MÉXICO 21396","ret_isr":false},
  {"consecutivo":36,"razon_social":"LUIS MIGUEL GRIJALVA ESTRELLA","rfc":"GIEL830521NW4","domicilio":"","ret_isr":false},
  {"consecutivo":37,"razon_social":"Grupo MCIT","rfc":"GMC140103928","domicilio":"Paseo del Gaycura 4405 Ampliacion Guaycura Tijuana Baja California","ret_isr":false},
  {"consecutivo":38,"razon_social":"MANUEL HORACIO GOMEZ LEDEZMA","rfc":"GOLM811226TM6","domicilio":"AV. SALAMANCA 2359 ESPERANZA MEXICALI BAJA CALIFORNIA MEXICO 21350","ret_isr":false},
  {"consecutivo":39,"razon_social":"ANA CLAUDIA GONZALEZ ORTIZ","rfc":"GOOA760420NM3","domicilio":"20 DE OCTUBRE 2039 NUEVA MADERO MONTERREY NUEVO LEON MEXICO 64560","ret_isr":true},
  {"consecutivo":40,"razon_social":"Ana Claudia Gonzalez Ortiz","rfc":"GOOA760420NM3","domicilio":"C. 20 de Noviembre No. 2039 Col. Nueva Madero Monterrey Nuevo León C.P. 64560","ret_isr":true},
  {"consecutivo":41,"razon_social":"GE Sistemas Médicos de México, S.A. de C.V.","rfc":"GSM920409JL6","domicilio":"C. Antonio Dovali Jaime No. 70 Torre B Piso 4 Col. Santa FE Alcaldia Alvaro Obregon Cd de México C.P. 01210","ret_isr":true},
  {"consecutivo":42,"razon_social":"Raul Hernández Carrillo","rfc":"HECR5011269N2","domicilio":"C. Begonia No. 29 Fortin de las Flores Col. La Mesa Tijuana Baja California México C.P. 22114","ret_isr":true},
  {"consecutivo":43,"razon_social":"PORTACOOL MEXICALI, ANTONIO HURTADO NUÑEZ","rfc":"HUNA921019815","domicilio":"CUAUHTEMOC 8/1. CUAUHTEMOC SUR CP.21200 MEXICALI BAJA CALIFORNIA","ret_isr":true},
  {"consecutivo":44,"razon_social":"INSTRUMENTOS Y ACCESORIOS AUTOMATIZADOS SA DE CV","rfc":"IAA980126MD4","domicilio":"CALLE 1 NO. 314 COL. DEPORTIVA PENSIL CP. 11470 MIGUEL HIDALGO CD. DE MEXICO","ret_isr":true},
  {"consecutivo":45,"razon_social":"INGENIERIA EN ESTERILIZACION Y CONTROL S.A. DE C.V.","rfc":"IEC020212736","domicilio":"CALLE 6 96 C03 AGRICOLA PANTITLAN IZTACALCO CDMX. CP. 08100","ret_isr":true},
  {"consecutivo":46,"razon_social":"JOSE ANGEL LIZARRAGA MEZA","rfc":"IMS421231I45","domicilio":"AV. RIO VILLA VERDE No. 3596 COL. VILLAS DE LA REPUBLICA C.P. 21298 MEXICALI BAJA CALIFORNIA","ret_isr":true},
  {"consecutivo":47,"razon_social":"INTECHNO SA DE CV","rfc":"INT9701288E9","domicilio":"AGUSTIN CASTRO SUR 382 ALAMEDA C.P.21215 MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":true},
  {"consecutivo":48,"razon_social":"JESUS ARMANDO JAQUEZ CONTRERAS","rfc":"JACJ700225V60","domicilio":"AV.LEON TOLSTOI 2462 FRACC. JUSTO SIERRA MEXICALI BAJA CALIFORNIA MÉXICO C.P. 21230","ret_isr":true},
  {"consecutivo":49,"razon_social":"RAUL JACOBO TORRES","rfc":"JATR680327QU4","domicilio":"AV. ANDALUZ NO. 164 COL TERRAZAS DEL SOL MEXICALI BAJA CALIFORNIA MEXICO CP. 21353","ret_isr":true},
  {"consecutivo":50,"razon_social":"JUNTAS INDUSTRIALES DEL NOROESTE SA DE CV","rfc":"JIN920331Q79","domicilio":"CALZADA HECTOR TERAN TERAN KM 1.5 S/N XOCHIMILCO MEXICALI BAJA CALIFORNIA","ret_isr":true},
  {"consecutivo":51,"razon_social":"Laboratorios Certificados S.A. de C.V.","rfc":"LCE9107108XA","domicilio":"Carretera Cuautitlan Teoloyucan No. 4 Fracc. Industrial Xhala Mexico C.P. 54750","ret_isr":true},
  {"consecutivo":52,"razon_social":"JOSE ANGEL LIZARRAGA MEZA (2)","rfc":"LIMA7101053GA","domicilio":"RIO VERDE 3596 VILLAS DE LA REPUBLICA CP. 22299 MEXICALI BAJA CALIFORNIA MEXICO","ret_isr":true},
  {"consecutivo":53,"razon_social":"LOPEZ COSSIO MARIA BEATRIZ","rfc":"LOCB840110NX0","domicilio":"Av. Argentina 204 Cuauhtémoc Norte Mexicali Baja California México 21200","ret_isr":true},
  {"consecutivo":54,"razon_social":"MARIA BEATRIZ LOPEZ COSSIO","rfc":"LOCB8440110NX0","domicilio":"AV. ARGENTINA 204 CUAUHTÉMOC NORTE MEXICALI BAJA CALIFORNIA MÉXICO 21200","ret_isr":true},
  {"consecutivo":55,"razon_social":"GILBERTO LÓPEZ DIAZ","rfc":"LODG530128N56","domicilio":"ARGENTINA No498 No INT 2 COL. CUAUHTEMOC NORTE MEXICALI B.C. C.P. 21200","ret_isr":true},
  {"consecutivo":56,"razon_social":"RAMON ANDRES LOAIZA LONGORIA","rfc":"LOLR9510281J3","domicilio":"AV. REFORMA 476 COL. JUAREZ DELEGACION CUAUHTEMOC CIUDAD DE MEXICO MEXICO","ret_isr":true},
  {"consecutivo":57,"razon_social":"SALVADOR LOPEZ LOPEZ","rfc":"LOLS460515N31","domicilio":"AV. LAGO TANGAÑICA No.1348 COL. JARDINES DEL LAGO C.P. 21330 MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":true},
  {"consecutivo":58,"razon_social":"IGNACIO ALBERTO LOAIZA PRIETO","rfc":"LOPI610730A27","domicilio":"DELANTE NO. 289 INT. 1 COL. BUENAVENTURA ENSENADA BAJA CALIFORNIA C.P. 22880","ret_isr":true},
  {"consecutivo":59,"razon_social":"GUILLERMO ANTONIO LONGORIA ROMERO","rfc":"LORG711117T49","domicilio":"BLVD. DÍAZ ORDAZ 1111 110 FRACCIONAMIENTO LOS ARBOLES C.P. 22117 TIJUANA BAJA CALIFORNIA MÉXICO","ret_isr":true},
  {"consecutivo":60,"razon_social":"JAVIER ALEJANDRO LOAIZA VELEZ","rfc":"LOVJ791109LC0","domicilio":"AV. XAJAY 1951 1 CALAFIA C.P. 21040 MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":true},
  {"consecutivo":61,"razon_social":"JAVIER ALEJANDRO LOAIZA VELEZ (2)","rfc":"LOVJ91109LC0","domicilio":"AV. XAJAY 1951 -1 COL. FRACC CALAFIA CP. 21040","ret_isr":true},
  {"consecutivo":62,"razon_social":"MACO, S.A.","rfc":"MAC600430GI3","domicilio":"AVE. ZARAGOZA No. 1715 COLONIA NUEVA C.P. 21100 MEXICALI BAJA CALIFORNIA","ret_isr":true},
  {"consecutivo":63,"razon_social":"MATHEDO","rfc":"MAT160620UH1","domicilio":"","ret_isr":true},
  {"consecutivo":64,"razon_social":"SAIDA ELIZEMA MEDINA BOJORQUEZ","rfc":"MEBS801223885","domicilio":"AV. RIO USUMACINTA SUR NO. 3340. MEXICALI II MEXICALI BAJA CALIFORNIA MEXICO CP. 21395","ret_isr":true},
  {"consecutivo":65,"razon_social":"RAMON JAVIER MENENDEZ PEREZ","rfc":"MEPR870831SK0","domicilio":"CALLEJON EBANISTAS NO. 1433 Col. INDUSTRIAL MEXICALI BC MEX C.P. 21010","ret_isr":false},
  {"consecutivo":66,"razon_social":"Jose Julio Mendoza Santiago","rfc":"MESJ6312044T7","domicilio":"Circuito Arcos No. 19131 Int A Col. Otay Galerias Tijuana Baja California México C.P. 22436","ret_isr":false},
  {"consecutivo":67,"razon_social":"MADERERIA Y FERRETERIA RIO COLORADO SA DE CV","rfc":"MFR820303K4A","domicilio":"CONSTITUCION S/N CJON VICENTE GRO. Y 1RA. COL. LA MESA SAN LUIS RIO COLORADO SONORA C.P. 83420 MEXICO","ret_isr":false},
  {"consecutivo":68,"razon_social":"MADERAS Y MATERIALES DE SAN LUIS","rfc":"MMS760317HW6","domicilio":"AVE. LIBERTAD Y CALLE 7 S/N COL. COMERCIAL SAN LUIS RIO COLORADO SONORA C.P. 83449 MEXICO","ret_isr":false},
  {"consecutivo":69,"razon_social":"Maria Angelica Moreno Araujo","rfc":"MOAA801227W4","domicilio":"C. ixtlacihuatl No. 12220 Col Camino Verde Tijuana Baja California México C.P 22680","ret_isr":false},
  {"consecutivo":70,"razon_social":"CLAUDIA BELEN NUÑEZ GARCIA","rfc":"NUGC791205GT5","domicilio":"","ret_isr":false},
  {"consecutivo":71,"razon_social":"FEDERICO NUÑO GUTIERREZ","rfc":"NUGF681118N33","domicilio":"CALLE CUARTA 1183 INT D COL GONZALEZ ORTEGA CP. 21397 MEXICALI BC","ret_isr":false},
  {"consecutivo":72,"razon_social":"FRANCISCO OLVERA ORTEGA","rfc":"OEOF4007025E9","domicilio":"AV. IGNACIO COMONFORT No. 654 COL. PROHOGAR C.P. 21240 MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":false},
  {"consecutivo":73,"razon_social":"ARMANDO OLEA SANCHEZ","rfc":"OESA620904QG1","domicilio":"CALLEJON ZARAGOZA 14611 CENTRO CIVICO CP 21000 BAJA CALIFORNIA MEXICO","ret_isr":false},
  {"consecutivo":74,"razon_social":"BALTAZAR OLIVAS SILLAS","rfc":"OISB740920527","domicilio":"","ret_isr":false},
  {"consecutivo":75,"razon_social":"JOSE DE JESUS OLMOS CAMACHO","rfc":"OOCJ5808088S3","domicilio":"AV HUAPANGO 12237 FRACC. LOMAS DE LA PRESA CP 22125 TIJUANA BAJA CALIFORNIA","ret_isr":false},
  {"consecutivo":76,"razon_social":"FERNANDO ALEXIS PAVON ROJAS","rfc":"PARF010509H98","domicilio":"AV. CAPUCHINA 2477 SOLIDARIDAD VIRREYES MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":false},
  {"consecutivo":77,"razon_social":"PEST CONTROL BAJA, S.A. DE C.V.","rfc":"PCB900924348","domicilio":"CALLEJON EBANISTAS NO. 1433 Col. INDUSTRIAL MEXICALI BC MEX C.P. 21010","ret_isr":false},
  {"consecutivo":78,"razon_social":"PEST CONTROL BAJA, S.A. DE C.V. (Ensenada)","rfc":"PCB900924348","domicilio":"ALDAMA No.254 MEX C.P. 22840","ret_isr":false},
  {"consecutivo":79,"razon_social":"Pest Control, Baja, S.A. de C.V.","rfc":"PCB900924348","domicilio":"C. Aldama No. 254 Col. Independencia Ensenada Baja California México C.P. 22840","ret_isr":false},
  {"consecutivo":80,"razon_social":"Juan de Dios Peña Bayardo","rfc":"PEBJ9703085X2","domicilio":"Av. Paseo Guaycura No. 20535 Ampliacion Guaycura Tijuana Baja California México C.P. 22214","ret_isr":false},
  {"consecutivo":81,"razon_social":"PRO LAB RX, S.A. DE C.V.","rfc":"PLR020930F82","domicilio":"CALLE EJIDO LA CANDELARIA No.84 COL. AMPLIACIÓN SAN FRANCISCO CULHUACAN DELEGACIÓN COYOACAN MÉXICO D.F. C.P. 04420","ret_isr":false},
  {"consecutivo":82,"razon_social":"MARISELA PONCE BORBOA","rfc":"POBM7907019H0","domicilio":"CARR. SAN LUIS RIO COLORADO 11500 KM GONZALEZ ORTEGA MEXICALI B.C. MEXICO","ret_isr":false},
  {"consecutivo":83,"razon_social":"PROFE-PART, S.A. DE C.V.","rfc":"PPA971213NE3","domicilio":"AVENIDA PUEBLA 1099 COLONIA LOMA LINDA CP 21140","ret_isr":false},
  {"consecutivo":84,"razon_social":"PROFE-PART, S.A. DE C.V. (San Luis)","rfc":"PPA971213NE3","domicilio":"AV. 5 DE MAYO NO.602 ENTRE 6 Y 7 C.P. 83449 SAN LUIS RIO COLORADO SONORA","ret_isr":false},
  {"consecutivo":85,"razon_social":"PINTURAS REM DE MEXICALI SA DE CV","rfc":"PRM151028TH8","domicilio":"SUCURSAL: TIERRA BLANCA","ret_isr":false},
  {"consecutivo":86,"razon_social":"QUIMICA MEXICANA INDUSTRIAL","rfc":"QMI640701EPA","domicilio":"CARRETERA CUAUTITLÁN TEOLOYUCAN NO. 4 FRACCIONAMIENTO INDUSTRIAL XHALA MÉXICO C.P. 54750","ret_isr":false},
  {"consecutivo":87,"razon_social":"CARLOS ENRIQUE RAMIREZ ARREDONDO","rfc":"RAAC940128IT1","domicilio":"MARBELLA 311 VILLA DEL REY QUINTA ETAPA C.P. 21355 MEXICALI BAJA CALIFORNIA","ret_isr":false},
  {"consecutivo":88,"razon_social":"MARIO LUIS REYES GUTIERREZ","rfc":"REGM610825MJ5","domicilio":"CALLE DEL MAGISTERIO NO. 2008 COL. VILLA BONITA C.P. 21379 MEXICALI BAJA CALIFORNIA","ret_isr":false},
  {"consecutivo":89,"razon_social":"DANIEL REMIGIO SALCIDO","rfc":"RESD870619A64","domicilio":"RIO PRESIDIO No. 2021 CONSTITUCIÓN MEXICALI BAJA CALIFORNIA MÉXICO C.P. 21250","ret_isr":false},
  {"consecutivo":90,"razon_social":"MAGDALENA ROJAS MORALES","rfc":"ROMM730411385","domicilio":"AV. CAPUCHINAS 2477 SOLIDARIDAD VIRREYES","ret_isr":false},
  {"consecutivo":91,"razon_social":"JAIME ROMERO RUBIO","rfc":"RORJ551103H59","domicilio":"ANGEL SALDIVAR No. 914 CUCAPAH INFONAVIT MEXICALI BAJA CALIFORNIA MÉXICO C.P. 21340","ret_isr":false},
  {"consecutivo":92,"razon_social":"YAZMIN SERRANO ARIAS","rfc":"SEAY930817R1A","domicilio":"LAGO DE TORONTO SUR 698 COL. LAGUNA CAMPESTRE MEXICALI BAJA CALIFORNIA MÉXICO C.P. 21387","ret_isr":false},
  {"consecutivo":93,"razon_social":"SERVICIOS MÉDICOS Y TÉCNICOS SA DE CV","rfc":"SMT010905FL0","domicilio":"CALLE FERNANDO AMILPA No. 48 INT: 1ER PISO COL. CTM EL RISCO C.P. 07090 GUSTAVO A MADERO CIUDAD DE MÉXICO MÉXICO","ret_isr":false},
  {"consecutivo":94,"razon_social":"Ma. Lidia Solorzano Trinidad","rfc":"SOTL600804848","domicilio":"C. Josefa Ortiz de Dominguez No. 7470 Col. La Cima Tijuana Baja California México C.P. 22616","ret_isr":false},
  {"consecutivo":95,"razon_social":"SERVICIO Y SOPORTE BIOMEDICO SA DE CV","rfc":"SSB100323G33","domicilio":"Monte Elbruz No. ext.132 Int. Piso 6 604 Col. Lomas de Chapultepec Deleg. Miguel Hidalgo C. P. 11000 CDMX México","ret_isr":false},
  {"consecutivo":96,"razon_social":"SAFETY SUPPLY DEL PACIFICO SA DE CV","rfc":"SSP1712145G2","domicilio":"INSURGENTES 694 COL. BUSTAMANTE ENSENADA BAJA CALIFORNIA","ret_isr":false},
  {"consecutivo":97,"razon_social":"VICTOR HUGO UREÑA BELTRAN","rfc":"UEBV6702174F1","domicilio":"AV. DE LOS MAGISTRADOS No. EXT. 399 COL. FRACC. MISION SANTO DOMINGO C.P. 21298 MEXICALI BAJA CALIFORNIA MÉXICO","ret_isr":false},
  {"consecutivo":98,"razon_social":"ANA MERIDA URIAS ACUNA","rfc":"UIAA710910LT7","domicilio":"CALLE SOMBRERETE NO. 340 COLONIA DEL RASTRO MEXICALI BAJA CALIFORNIA MÉXICO C.P. 21090","ret_isr":false},
  {"consecutivo":99,"razon_social":"VIASIS SERVICIO, S.A. DE C.V.","rfc":"VSE1505131U0","domicilio":"LUIS SPOTA NO. 5 COL. SAN SIMÓN TICUMAC ALCALDÍA: BENITO JUÁREZ C.P. 03660 CDMX","ret_isr":false}
];

async function migrar() {
  console.log(`Migrando ${PROVEEDORES.length} proveedores a Supabase...`);

  // Preparar payload con campos de la tabla
  const payload = PROVEEDORES.map(p => ({
    consecutivo:  p.consecutivo,
    razon_social: p.razon_social,
    rfc:          p.rfc || null,
    domicilio:    p.domicilio || null,
    ret_isr:      p.ret_isr,
    iva_rate:     0.08,
    activo:       true,
    zona:         null,
    constancia_url: null
  }));

  const res = await fetch(`${SUPABASE_URL}/rest/v1/proveedores_catalogo`, {
    method: 'POST',
    headers: {
      'apikey':        SUPABASE_ANON,
      'Authorization': `Bearer ${SUPABASE_ANON}`,
      'Content-Type':  'application/json',
      'Prefer':        'return=minimal'
    },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    console.log(`✅ ${PROVEEDORES.length} proveedores migrados correctamente.`);
  } else {
    const err = await res.text();
    console.error('❌ Error:', res.status, err);
  }
}

migrar();
