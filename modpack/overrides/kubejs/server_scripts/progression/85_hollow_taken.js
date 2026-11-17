// pass 9-51: "what waits there is wearing their face". The heavier a player's Hollow, the more friendly and neutral mobs that spawn
// near them come up wrong: tagged gh_hollow_taken, which the Mob Rules rule dying_world:hollow_taken turns hostile.
// Weight = the player's residue tier (from the tinker's workshop on) + days held since the Hollow. Released players weigh nothing.
const TAKEN_BY_TIER = { 0: 0, 1: 0.02, 2: 0.05, 3: 0.08, 4: 0.12, 5: 0.15 }   // gh_residue_<tier>; 5 = Hollowed
const TAKEN_PER_DAY_HELD = 0.03, TAKEN_CAP = 0.5, TAKEN_RADIUS = 48
const TAKEN_WEIGHTS = {}                                                        // player uuid -> weight, refreshed every 5 s

// Weight per player, worked out every 100 ticks (not per spawn): tier tags + the gh_held_day scoreboard (60_the_hollow.js).
function hollowWeight(p) {
  if (!global.GH_PROGRESSION.hollowEndgame || p.tags.contains('gh_escaped')) return 0
  let tier = 0
  for (let t = 5; t >= 1; t--) if (p.tags.contains('gh_residue_' + t)) { tier = t; break }
  let w = TAKEN_BY_TIER[tier]
  const heldDay = Math.max(0, p.server.runCommandSilent(`scoreboard players get ${p.username} gh_held_day`))
  if (heldDay > 0) w += Math.max(0, Math.floor(p.server.overworld().gameTime / 24000) + 1 - heldDay) * TAKEN_PER_DAY_HELD
  return Math.min(TAKEN_CAP, w)
}

PlayerEvents.tick(event => {
  const p = event.player
  if (p.age % 100 == 0) TAKEN_WEIGHTS[String(p.uuid)] = hollowWeight(p)
})

EntityEvents.spawned(event => {
  const e = event.entity
  if (event.level.isClientSide() || !e.isLiving() || e.isPlayer()) return
  if (String(e.getType().getCategory().getName()) != 'creature') return
  if (e.tags.contains('gh_hollow_seen')) return                 // each animal is judged once (chunk reloads fire this again)
  e.addTag('gh_hollow_seen')
  if (e.isBaby() || e.hasCustomName()) return
  if (e.getOwnerUUID && e.getOwnerUUID() != null) return       // tamed pets stay loyal
  const p = event.level.getNearestPlayer(e, TAKEN_RADIUS)
  if (p == null) return
  const w = TAKEN_WEIGHTS[String(p.uuid)]
  if (w && Math.random() < w) e.addTag('gh_hollow_taken')
})
