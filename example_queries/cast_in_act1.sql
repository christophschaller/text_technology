SELECT cast_item_id FROM cast_stage_association as asso
JOIN stage on stage.id = asso.stage_id
JOIN scene on stage.scene_id = scene.id
JOIN act on act.id = scene.act_id
WHERE act.content IN ('ACT 1')
GROUP BY cast_item_id