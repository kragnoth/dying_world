// pass 9-48: Foundry Residue - only gathered while the player sees the Occult Foundry (Wasteland Vision tag wv_occult_foundry).
// It ramps with the Incursion quests: each quest's reward adds a tag gh_residue_<tier>; the highest one counts.
// Released players (gh_escaped, lens on) also find Distilled Residue. Tune everything in RESIDUE_TIERS / DISTILLED_CHANCE.
const RESIDUE_TIERS = {           // [deepslate mined, undead killed]
  1: [0.005, 0.02],               // The Apprentice (tinker's workshop)
  2: [0.01, 0.04],                // The Gatehouse (research gate)
  3: [0.02, 0.06],                // Requisitions / The Tidewell / The Listening Post
  4: [0.03, 0.08],                // Station Below / Far Station
  5: [0.03, 0.08]                 // Hollowed (plus Foundry Revenants: 1-2 each)
}
const DISTILLED_CHANCE = { undead: 0.02, revenant: 0.25, deepslate: 0.004 }
const RESIDUE_ID = 'gearwrights:foundry_residue', DISTILLED_ID = 'gearwrights:distilled_residue'
const RESIDUE_BLOCKS = ['minecraft:deepslate', 'minecraft:cobbled_deepslate']

function residueTier(p) {
  for (let t = 5; t >= 1; t--) if (p.tags.contains('gh_residue_' + t)) return t
  return 0
}

function gathers(p) {
  return global.GH_PROGRESSION.hollowEndgame && !p.isCreative() && p.tags.contains('wv_occult_foundry')
}

BlockEvents.broken(event => {
  const p = event.player
  if (!p || RESIDUE_BLOCKS.indexOf(String(event.block.id)) < 0 || !gathers(p)) return
  const t = residueTier(p)
  if (t > 0 && Math.random() < RESIDUE_TIERS[t][0]) event.block.popItem(Item.of(RESIDUE_ID))
  if (p.tags.contains('gh_escaped') && Math.random() < DISTILLED_CHANCE.deepslate) event.block.popItem(Item.of(DISTILLED_ID))
})

EntityEvents.death(event => {
  const p = event.source.player
  const e = event.entity
  if (!p || !e.isLiving() || !gathers(p)) return
  const t = residueTier(p)
  const revenant = String(e.type) == 'incision:skeletoncultist' && String(e.level.dimension) == 'minecraft:overworld'
  if (t >= 5 && revenant) e.block.popItem(Item.of(RESIDUE_ID, 1 + Math.floor(Math.random() * 2)))
  else if (t > 0 && e.isInvertedHealAndHarm() && Math.random() < RESIDUE_TIERS[t][1]) e.block.popItem(Item.of(RESIDUE_ID))
  if (p.tags.contains('gh_escaped') && (revenant ? Math.random() < DISTILLED_CHANCE.revenant
                                                 : e.isInvertedHealAndHarm() && Math.random() < DISTILLED_CHANCE.undead)) {
    e.block.popItem(Item.of(DISTILLED_ID))
  }
})
