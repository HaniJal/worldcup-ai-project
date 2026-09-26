"""
Fact-checked source text for the Wikipedia RAG enrichment.

Every paragraph below was taken from Wikipedia's "2026 FIFA World Cup
final" article and cross-checked against the seeded database (winner,
score, Man of the Match, date, and runner-up all confirmed to match) before
inclusion. One correction was made to the original source during
transcription: the Argentina-Jordan group match description was corrected
to credit the actual three different goalscorers (Lo Celso, Martinez,
Messi) rather than an earlier paraphrase that incorrectly attributed two
goals to Messi.

Do not add further web-sourced text to this file without doing the same
kind of cross-check against the database first.
"""

FINAL_MATCH_NARRATIVE = """
Spain dominated possession and created numerous goal-scoring opportunities throughout the match, with Argentina goalkeeper Emiliano Martinez repeatedly denying its offensive efforts. Argentina, reduced to ten players after Enzo Fernandez was sent off in the second half, failed to register a single shot in regulation time, a first for a World Cup final. The goalless deadlock carried into extra time, during which Ferran Torres scored from a Nico Williams header to secure a 1-0 victory for Spain. With a few minutes left, Argentina missed multiple opportunities to equalize the score. After the match, a brawl broke out between the two teams.

Spain's win earned the country its second World Cup title and its first since 2010. Torres was named the man of the match, and Emiliano Martinez's 11 saves set a record for the most saves by a goalkeeper in a World Cup final. The match was the first ever World Cup final to include a halftime show, which caused the full halftime break to last over 27 minutes, against IFAB protocol. Spain became the first country to simultaneously hold the men's and women's World Cup titles, having won the FIFA Women's World Cup in 2023.

In the awards ceremony after the match, Spain's Rodri was awarded the Golden Ball as the best player of the tournament, while his teammate Unai Simon was awarded the Golden Glove as the best goalkeeper. Spain's Pau Cubarsi won the FIFA Young Player Award as the best young player of the tournament. Lionel Messi won the Silver Ball as the second-best player of the tournament, and the Silver Boot as the second-top goalscorer, with eight goals.

Messi became the second player in history to play in three World Cup finals, after Cafu of Brazil. Spain also became the second European nation to win a World Cup held in the Americas, following Germany in 2014, and the second nation to win a World Cup co-hosted by multiple countries after Brazil in 2002.
"""

SPAIN_ROUTE_NARRATIVE = """
En route to the final, Spain finished first in Group H with two wins and a draw, before defeating Austria in the round of 32, Portugal in the round of 16, Belgium in the quarterfinal, and France in the semifinal. Spain's first match was against Cape Verde in Atlanta on June 15, ending in a goalless draw due to a strong defensive performance from Cape Verde and its goalkeeper, Vozinha. Spain's second match was against Saudi Arabia on June 21: Lamine Yamal opened the scoring, Mikel Oyarzabal added two more goals, and an own goal sealed a 4-0 win. Spain's last group game was a 1-0 win over Uruguay, with Alex Baena's shot slipping through the goalkeeper's hands. Spain advanced as group winners with seven points.

In the round of 32, Spain faced Austria on July 2 and won 3-0, with two goals from Mikel Oyarzabal and one from Pedro Porro. In the round of 16 against Portugal on July 6, Mikel Merino scored the only goal of the game in second-half stoppage time to eliminate Portugal and Cristiano Ronaldo.

Spain faced Belgium in the quarterfinal on July 10. Fabian Ruiz gave Spain a 1-0 lead, Charles De Ketelaere equalized for Belgium, and Merino scored the winning goal two minutes before the end of regulation time for a 2-1 victory. On July 14, Spain beat France 2-0 in the semifinal, with a first-half penalty from Oyarzabal and a second goal from Porro, progressing to the final for the first time since 2010.
"""

ARGENTINA_ROUTE_NARRATIVE = """
Argentina finished first in Group J with three wins, after which it defeated Cape Verde in the round of 32, Egypt in the round of 16, Switzerland in the quarterfinal, and England in the semifinal. In its first match against Algeria on June 16, Argentina won 3-0 through a hat trick by Lionel Messi. Their second match was against Austria on June 22: Messi scored twice, including a goal that made him the all-time top goalscorer at World Cup tournaments with 17 goals, surpassing Miroslav Klose, in a 2-0 win. Argentina's last group game was against Jordan on June 27: Giovani Lo Celso converted a free kick, Lautaro Martinez scored a penalty, and Messi added a late free kick goal to seal a 3-1 win. Argentina qualified as group winners with nine points.

Argentina faced Cape Verde in the round of 32 on July 3. Messi opened the scoring, Cape Verde equalized, the match went to extra time, and after Cape Verde tied it again, a deflected header off Diney Borges's arm gave Argentina a 3-2 win. In the round of 16 against Egypt on July 7, Egypt led 2-0, but Argentina scored three goals in the final fifteen minutes for a dramatic 3-2 comeback win.

Argentina's quarterfinal was against Switzerland on July 11. Alexis Mac Allister opened the scoring, Switzerland equalized, and Argentina won 3-1 in extra time through a long-distance strike by Julian Alvarez. In the semifinal against England on July 15, England took the lead, but Messi provided assists for Enzo Fernandez's equalizing goal and for Martinez's game-winning header in stoppage time, sending Argentina to their second consecutive World Cup final with a 2-1 win.
"""
