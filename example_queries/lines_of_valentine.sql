SELECT GROUP_CONCAT(token.content SEPARATOR ' ') as content,
       line.id, speech.id, cast.id FROM token
JOIN line on line.id = token.line_id
JOIN speech on speech.id = line.speech_id
JOIN cast_item as cast on cast.id = speech.cast_item_id
WHERE cast.id IN ('Valentine_TGV')
GROUP BY line.id