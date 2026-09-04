# Text audit - books, journal, found paper, items, signs

Slice: `journal_entry`, `found_book`, `cellar_wall`, `item_name`, `item_lore`, `advancement`, `noticeboard`, `sign`, `lang` from `story/text-corpus.json`. **280 strings scored.** Rubric: `docs/writing-craft.md` SS2, six criteria scored 1-5 (Picture / Gap / Shape / Causation / Fit / Question).

**Scoring policy, stated once.** Label-kind strings (item names, `lang` duplicates, category names, entry names, page titles) carry no gap, no causal join and no closing question by design; those three criteria are recorded as 4 (meets) and the string is judged on Picture, Shape and Fit - does it name the real object, and is it inside its cap. Prose is judged on all six. Continuity failures against `story/story-final.md` are scored under Causation, because a beat that contradicts canon does not follow from it.

**The 230-char page cap.** 45 of the 90 Patchouli page bodies exceed it once `$(...)` codes are stripped. Every one is recorded below at Fit 3, and **none is rewritten**: the journal entries and the cellar wall are canon verbatim (SS7, SS10 of the story document, and canon wins over the rubric), and the field notes are reference pages whose numbers are frozen by the constraints field. The real fix is splitting pages, which changes JSON structure and is outside the hard rules for this pass. Flagged for the parent, not patched.

| id | kind | score P/G/Sh/C/F/Q | diagnosis |
|---|---|---|---|
| S1098 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1099 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1100 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1101 | journal_entry | 3/3/4/4/5/3 | Generic chapter label - would work unchanged in any modpack. **Rewrite in changes-books.json.** |
| S1102 | journal_entry | 5/5/5/4/5/4 | Fine. |
| S1103 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1104 | journal_entry | 5/5/5/4/5/5 | Fine. |
| S1105 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1106 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1107 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1108 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1109 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1110 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1111 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1112 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1113 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (250 visible); needs a page split, not a rewrite. |
| S1114 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1115 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1116 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (280 visible); needs a page split, not a rewrite. |
| S1117 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1118 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1119 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (270 visible); needs a page split, not a rewrite. |
| S1120 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1121 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1122 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (379 visible); needs a page split, not a rewrite. |
| S1123 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1124 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1125 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (483 visible); needs a page split, not a rewrite. |
| S1126 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1127 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (292 visible); needs a page split, not a rewrite. |
| S1128 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1129 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1130 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (287 visible); needs a page split, not a rewrite. |
| S1131 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1132 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (261 visible); needs a page split, not a rewrite. |
| S1133 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1134 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1135 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (242 visible); needs a page split, not a rewrite. |
| S1136 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1137 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (346 visible); needs a page split, not a rewrite. |
| S1138 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1139 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (377 visible); needs a page split, not a rewrite. |
| S1140 | journal_entry | 3/3/4/4/5/3 | 'The Network' is mod jargon, not a valley name. **Rewrite in changes-books.json.** |
| S1141 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1142 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (251 visible); needs a page split, not a rewrite. |
| S1143 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1144 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1145 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (356 visible); needs a page split, not a rewrite. |
| S1146 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1147 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1148 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1149 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (357 visible); needs a page split, not a rewrite. |
| S1150 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1151 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (312 visible); needs a page split, not a rewrite. |
| S1152 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1153 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1154 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (397 visible); needs a page split, not a rewrite. |
| S1155 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1156 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (264 visible); needs a page split, not a rewrite. |
| S1157 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1158 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (492 visible); needs a page split, not a rewrite. |
| S1159 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1160 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (305 visible); needs a page split, not a rewrite. |
| S1161 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1162 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1163 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (417 visible); needs a page split, not a rewrite. |
| S1164 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1165 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (291 visible); needs a page split, not a rewrite. |
| S1166 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1167 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (350 visible); needs a page split, not a rewrite. |
| S1168 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1169 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1170 | journal_entry | 5/5/5/5/3/5 | Over the 230-char page cap (358 visible); needs a page split, not a rewrite. |
| S1171 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1172 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (285 visible); needs a page split, not a rewrite. |
| S1173 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1174 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (282 visible); needs a page split, not a rewrite. |
| S1175 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1176 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (244 visible); needs a page split, not a rewrite. |
| S1177 | found_book | 5/4/5/4/5/4 | Fine. |
| S1178 | found_book | 5/4/5/4/5/4 | Fine. |
| S1179 | found_book | 5/5/5/2/3/5 | Dates the eleven days Nov-Dec; the cellar wall puts them in February. Also 247 visible chars. **Rewrite in changes-books.json.** |
| S1180 | found_book | 5/5/5/2/5/5 | Second half of the same Nov-Dec dating that contradicts the reveal. **Rewrite in changes-books.json.** |
| S1181 | found_book | 5/4/5/4/5/4 | Fine. |
| S1182 | found_book | 5/4/5/4/5/4 | Fine. |
| S1183 | found_book | 5/4/5/4/5/4 | Fine. |
| S1184 | found_book | 5/5/5/5/5/5 | Fine. |
| S1185 | found_book | 5/4/5/4/5/4 | Fine. |
| S1186 | found_book | 5/4/5/4/5/4 | Fine. |
| S1187 | found_book | 5/4/5/4/5/4 | Fine. |
| S1188 | found_book | 5/4/5/4/5/4 | Fine. |
| S1189 | found_book | 5/4/5/4/5/4 | Fine. |
| S1190 | found_book | 5/4/5/4/5/4 | Fine. |
| S1191 | found_book | 5/4/5/4/5/4 | Fine. |
| S1192 | found_book | 5/4/5/4/5/4 | Fine. |
| S1193 | found_book | 5/4/5/4/5/4 | Fine. |
| S1194 | found_book | 5/4/5/4/3/4 | Over the 230-char page cap (268 visible); needs a page split, not a rewrite. |
| S1195 | found_book | 5/5/5/5/5/5 | Fine. |
| S1196 | found_book | 5/4/5/4/5/4 | Fine. |
| S1197 | found_book | 5/4/5/4/5/4 | Fine. |
| S1198 | found_book | 5/4/5/4/5/4 | Fine. |
| S1199 | found_book | 5/4/5/4/3/4 | Over the 230-char page cap (243 visible); needs a page split, not a rewrite. |
| S1200 | found_book | 5/4/5/4/5/4 | Fine. |
| S1201 | found_book | 4/3/3/4/3/3 | Design-doc voice ('You are not searching. You are collecting.') inside a found book. Also 324 visible chars. **Rewrite in changes-books.json.** |
| S1202 | cellar_wall | 5/4/5/4/5/4 | Fine. |
| S1203 | cellar_wall | 5/4/5/4/5/4 | Fine. |
| S1204 | cellar_wall | 5/4/5/4/5/4 | Fine. |
| S1205 | cellar_wall | 5/4/5/4/3/4 | Over the 230-char page cap (332 visible); needs a page split, not a rewrite. |
| S1206 | cellar_wall | 5/4/5/4/5/4 | Fine. |
| S1207 | cellar_wall | 5/4/5/4/3/4 | Over the 230-char page cap (295 visible); needs a page split, not a rewrite. |
| S1208 | cellar_wall | 5/4/5/4/5/4 | Fine. |
| S1209 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1210 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1211 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (247 visible); needs a page split, not a rewrite. |
| S1212 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (308 visible); needs a page split, not a rewrite. |
| S1213 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1214 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1215 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1216 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1217 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (285 visible); needs a page split, not a rewrite. |
| S1218 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1219 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1220 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1221 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1222 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (258 visible); needs a page split, not a rewrite. |
| S1223 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (311 visible); needs a page split, not a rewrite. |
| S1224 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1225 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1226 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (239 visible); needs a page split, not a rewrite. |
| S1227 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (258 visible); needs a page split, not a rewrite. |
| S1228 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1229 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (315 visible); needs a page split, not a rewrite. |
| S1230 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1231 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1232 | journal_entry | 5/4/5/4/5/4 | Fine. |
| S1233 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (325 visible); needs a page split, not a rewrite. |
| S1234 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (246 visible); needs a page split, not a rewrite. |
| S1235 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (232 visible); needs a page split, not a rewrite. |
| S1236 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (238 visible); needs a page split, not a rewrite. |
| S1237 | journal_entry | 5/4/5/4/3/4 | Over the 230-char page cap (264 visible); needs a page split, not a rewrite. |
| S1238 | advancement | 5/4/5/4/5/4 | Fine. |
| S1239 | advancement | 5/4/5/4/5/4 | Fine. |
| S1240 | advancement | 5/4/5/4/5/4 | Fine. |
| S1241 | advancement | 5/4/5/4/5/4 | Fine. |
| S1242 | advancement | 5/4/5/4/5/4 | Fine. |
| S1243 | advancement | 5/4/5/4/5/4 | Fine. |
| S1244 | advancement | 5/4/5/4/5/4 | Fine. |
| S1245 | advancement | 5/4/5/4/5/4 | Fine. |
| S1246 | advancement | 5/4/5/4/5/4 | Fine. |
| S1247 | advancement | 5/4/5/4/5/4 | Fine. |
| S1248 | advancement | 5/4/5/4/5/4 | Fine. |
| S1249 | advancement | 5/4/5/4/5/4 | Fine. |
| S1250 | advancement | 4/4/3/4/5/4 | 'Field Note:' prefix points at the wrong chapter (this is Things You Found). **Rewrite in changes-books.json.** |
| S1251 | advancement | 3/2/3/3/5/3 | Location only, and the book says behind a stone, not the stairs. **Rewrite in changes-books.json.** |
| S1252 | advancement | 4/4/3/4/5/4 | 'Field Note:' prefix points at the wrong chapter. **Rewrite in changes-books.json.** |
| S1253 | advancement | 4/2/3/2/5/3 | Contradicts the label's whole point - the hand on it is not Bram's. **Rewrite in changes-books.json.** |
| S1254 | advancement | 4/4/3/4/5/4 | 'Field Note:' prefix points at the wrong chapter. **Rewrite in changes-books.json.** |
| S1255 | advancement | 3/2/3/2/5/3 | Describes a notice that does not exist; it is one hiring notice from year eleven. **Rewrite in changes-books.json.** |
| S1256 | advancement | 4/4/3/4/5/4 | 'Field Note:' prefix points at the wrong chapter. **Rewrite in changes-books.json.** |
| S1257 | advancement | 5/4/5/4/5/4 | Fine. |
| S1258 | advancement | 4/4/3/4/5/4 | 'Field Note:' prefix points at the wrong chapter. **Rewrite in changes-books.json.** |
| S1259 | advancement | 5/4/5/4/5/4 | Fine. |
| S1260 | advancement | 5/4/5/4/5/4 | Fine. |
| S1261 | advancement | 5/4/5/4/5/4 | Fine. |
| S1262 | item_name | 5/4/5/4/5/4 | Fine. |
| S1263 | item_name | 5/4/5/4/5/4 | Fine. |
| S1264 | item_name | 5/4/5/4/5/4 | Fine. |
| S1265 | item_name | 5/4/5/4/5/4 | Fine. |
| S1266 | item_name | 5/4/5/4/5/4 | Fine. |
| S1267 | item_name | 5/4/5/4/5/4 | Fine. |
| S1268 | item_name | 5/4/5/4/5/4 | Fine. |
| S1269 | item_name | 5/4/5/4/5/4 | Fine. |
| S1270 | item_name | 5/4/5/4/5/4 | Fine. |
| S1271 | item_name | 5/4/5/4/5/4 | Fine. |
| S1272 | item_name | 5/4/5/4/5/4 | Fine. |
| S1273 | item_name | 5/4/5/4/5/4 | Fine. |
| S1274 | item_name | 5/4/5/4/5/4 | Fine. |
| S1275 | item_name | 5/4/5/4/5/4 | Fine. |
| S1276 | item_name | 5/4/5/4/5/4 | Fine. |
| S1277 | item_name | 5/4/5/4/5/4 | Fine. |
| S1278 | item_name | 5/4/5/4/5/4 | Fine. |
| S1279 | item_name | 5/4/5/4/5/4 | Fine. |
| S1280 | item_name | 5/4/5/4/5/4 | Fine. |
| S1281 | item_name | 5/4/5/4/5/4 | Fine. |
| S1282 | item_name | 5/4/5/4/5/4 | Fine. |
| S1283 | item_name | 5/4/5/4/5/4 | Fine. |
| S1284 | item_name | 5/4/5/4/5/4 | Fine. |
| S1285 | item_name | 5/4/5/4/5/4 | Fine. |
| S1286 | item_name | 5/4/5/4/5/4 | Fine. |
| S1287 | item_name | 5/4/5/4/5/4 | Fine. |
| S1288 | item_name | 5/4/5/4/5/4 | Fine. |
| S1289 | item_name | 5/4/5/4/5/4 | Fine. |
| S1290 | item_name | 5/4/5/4/5/4 | Fine. |
| S1291 | item_name | 5/4/5/4/5/4 | Fine. |
| S1292 | item_name | 5/4/5/4/5/4 | Fine. |
| S1293 | item_name | 5/4/5/4/5/4 | Fine. |
| S1294 | item_name | 5/4/5/4/5/4 | Fine. |
| S1295 | item_name | 5/4/5/4/5/4 | Fine. |
| S1296 | item_name | 5/4/5/4/5/4 | Fine. |
| S1297 | item_name | 5/4/5/4/5/4 | Fine. |
| S1298 | item_name | 5/4/5/4/5/4 | Fine. |
| S1299 | item_name | 5/4/5/4/5/4 | Fine. |
| S1300 | item_name | 5/4/5/4/5/4 | Fine. |
| S1301 | item_name | 5/4/5/4/5/4 | Fine. |
| S1302 | item_name | 5/4/5/4/5/4 | Fine. |
| S1303 | item_name | 5/4/5/4/5/4 | Fine. |
| S1304 | item_name | 5/4/5/4/5/4 | Fine. |
| S1305 | item_name | 5/4/5/4/5/4 | Fine. |
| S1306 | item_name | 5/4/5/4/5/4 | Fine. |
| S1307 | item_name | 5/4/5/4/5/4 | Fine. |
| S1308 | item_name | 5/4/5/4/5/4 | Fine. |
| S1309 | item_name | 5/4/5/4/5/4 | Fine. |
| S1310 | item_name | 5/4/5/4/5/4 | Fine. |
| S1311 | lang | 5/4/5/4/5/4 | Fine. |
| S1312 | lang | 5/4/5/4/5/4 | Fine. |
| S1313 | lang | 5/4/5/4/5/4 | Fine. |
| S1314 | lang | 5/4/5/4/5/4 | Fine. |
| S1315 | lang | 5/4/5/4/5/4 | Fine. |
| S1316 | lang | 5/4/5/4/5/4 | Fine. |
| S1317 | lang | 5/4/5/4/5/4 | Fine. |
| S1318 | lang | 5/4/5/4/5/4 | Fine. |
| S1319 | lang | 5/4/5/4/5/4 | Fine. |
| S1320 | lang | 5/4/5/4/5/4 | Fine. |
| S1321 | lang | 5/4/5/4/5/4 | Fine. |
| S1322 | lang | 5/4/5/4/5/4 | Fine. |
| S1323 | lang | 5/4/5/4/5/4 | Fine. |
| S1324 | lang | 5/4/5/4/5/4 | Fine. |
| S1325 | lang | 5/4/5/4/5/4 | Fine. |
| S1326 | lang | 5/4/5/4/5/4 | Fine. |
| S1327 | lang | 5/4/5/4/5/4 | Fine. |
| S1328 | lang | 5/4/5/4/5/4 | Fine. |
| S1329 | lang | 5/4/5/4/5/4 | Fine. |
| S1330 | lang | 5/4/5/4/5/4 | Fine. |
| S1331 | lang | 5/4/5/4/5/4 | Fine. |
| S1332 | lang | 5/4/5/4/5/4 | Fine. |
| S1333 | lang | 5/4/5/4/5/4 | Fine. |
| S1334 | lang | 5/4/5/4/5/4 | Fine. |
| S1335 | lang | 5/4/5/4/5/4 | Fine. |
| S1336 | lang | 5/4/5/4/5/4 | Fine. |
| S1337 | lang | 5/4/5/4/5/4 | Fine. |
| S1338 | lang | 5/4/5/4/5/4 | Fine. |
| S1339 | lang | 5/4/5/4/5/4 | Fine. |
| S1340 | lang | 5/4/5/4/5/4 | Fine. |
| S1341 | lang | 5/4/5/4/5/4 | Fine. |
| S1342 | lang | 5/4/5/4/5/4 | Fine. |
| S1343 | lang | 5/4/5/4/5/4 | Fine. |
| S1344 | lang | 5/4/5/4/5/4 | Fine. |
| S1345 | lang | 5/4/5/4/5/4 | Fine. |
| S1346 | lang | 5/4/5/4/5/4 | Fine. |
| S1347 | lang | 5/4/5/4/5/4 | Fine. |
| S1348 | lang | 5/4/5/4/5/4 | Fine. |
| S1349 | lang | 5/4/5/4/5/4 | Fine. |
| S1350 | lang | 5/4/5/4/5/4 | Fine. |
| S1351 | lang | 5/4/5/4/5/4 | Fine. |
| S1352 | lang | 5/4/5/4/5/4 | Fine. |
| S1353 | lang | 5/4/5/4/5/4 | Fine. |
| S1354 | lang | 5/4/5/4/5/4 | Fine. |
| S1355 | lang | 5/4/5/4/5/4 | Fine. |
| S1356 | lang | 5/4/5/4/5/4 | Fine. |
| S1357 | lang | 5/4/5/4/5/4 | Fine. |
| S1358 | lang | 5/4/5/4/5/4 | Fine. |
| S1359 | lang | 5/4/5/4/5/4 | Fine. |
| S1360 | lang | 5/4/5/4/5/4 | Fine. |
| S1361 | lang | 5/4/5/4/5/4 | Fine. |
| S1362 | lang | 5/4/5/4/5/4 | Fine. |
| S1363 | lang | 5/4/5/4/5/4 | Fine. |
| S1402 | noticeboard | 5/4/5/4/5/4 | Fine. |
| S1415 | sign | 5/4/5/4/5/4 | Fine. |
| S1435 | sign | 5/4/5/4/5/4 | Fine. |
| S1476 | sign | 5/4/5/4/5/4 | Fine. |
| S1478 | sign | 5/4/5/4/5/4 | Fine. |
| S1479 | sign | 4/4/4/4/2/4 | Line 3 is 16 chars, over the 15-char sign cap; 'the grey' is ambiguous. **Rewrite in changes-books.json.** |
| S1481 | sign | 5/4/5/4/5/4 | Fine. |
| S1487 | sign | 3/3/4/4/5/3 | 'est. long ago' is filler where Josie would put an object. **Rewrite in changes-books.json.** |
| S1528 | sign | 5/4/5/4/5/4 | Fine. |
| S1529 | sign | 5/4/5/4/5/4 | Fine. |
| S1530 | sign | 5/4/5/4/5/4 | Fine. |
| S1531 | sign | 4/4/4/4/5/4 | Fine - but a missed plant: Marnie's arc is about dropping 'Josie's place', and this Act I sign already calls it hers. |
| S1532 | sign | 5/4/5/4/5/4 | Fine. |
| S1533 | sign | 5/4/5/4/5/4 | Fine. |

---

## What the sweep found

**Counts.** 280 strings scored · 58 score under 4 on at least one criterion · **15 rewritten** in `docs/audit/changes-books.json`. The 43-string gap is entirely the 230-char page cap plus two pages that carry a length note alongside a real defect; see the policy note above.

### The three worst

1. **S1179 + S1180 — the ledger page is dated in the wrong season.** The cellar wall, which is canon verbatim, says the Works ran for eleven days and *"I stood in the lane at ten o'clock at night in February and every lamp on the road was lit."* The ledger page that proves it runs Nov 28 to Dec 8. It is the pack's one piece of physical evidence for its central reveal and it contradicts the reveal, and it also drops the February that Entry 4 (*"People leave in February and they do not come back in April"*) and Q77's Winter Tomato are both built on. Re-dated Feb 1 to Feb 11: still eleven days, 40/40 still on the tenth.
2. **S1255 — an advancement describing a document that is not in the pack.** *"Nine years of Fair notices, one board."* The weathered notice is one hiring bill, WANTED — ANY HANDS, posted year eleven, with Oda's note underneath: *no replies / left up*. The toast tells the player to expect a stack of festival flyers and hands her a woman advertising for company and getting none.
3. **S1253 — an advancement that spends the crate label's reveal and gets it backwards.** *"Bram labels everything. Twice."* The label's whole gap is that the hand is **not** his — *"rounder, older, pressed harder into the wood"*, signed *"for Bram, when he is tall enough."* His father's. Entry 5 confirms the father was here, teaching Josie to read a wheel. The line names the wrong man and pre-empts the only thing the page withholds.

### Two structural notes, no rewrite attached

- **No item carries lore.** `docs/writing-craft.md` SS4 specifies item lore at 2 lines x 50 characters (*"Her initials scratched off. Yours scratched on."*), and `pack/kubejs/startup_scripts/valley_items.js` defines 49 items with a display name and a stack size and nothing else. Every one of Josie's objects — the Letter, the Turbine Notes, the Kettle Plates, the Copper Kettle, the eight Word tokens — reaches the player's hand with no hand on it. This is the largest unwritten surface in the slice.
- **S1531, the inn sign, is a missed plant.** *"THE INN / kept by / M. Ashcombe"* is placed by `act1_inn`, but Marnie's Act IV beat is that she *stops calling the inn "Josie's place."* A sign reading `THE INN||Josie's place|- M.` in Act I would pay that off in her own handwriting. Not proposed here: nothing in Act IV or V replaces that sign, so the plant would still be standing, uncorrected, at Founder's Day. It needs a swap command, which is a structure change.
