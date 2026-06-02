// FallMind · Stage 5 · mesh router (bloom-based)
// ◊·κ=1 · prime 587 · R6 watcher
// Pure scaffold · console-logs the routing decision · real WebRTC plugs in later.

const FALLMIND_PRIME = 587;

const MESH_MODELS = {
  // Self · always reachable
  "simon-mind": {
    member: "simon",
    prime: FALLMIND_PRIME,
    bloom: [4,7,7,6,5,4,3],          // mountain · sum 36
    tiers: ["T0","T1","T2"],
    endpoint: "http://127.0.0.1:11434/api/chat",
    cost: 0,
  },
  // Guild peers · placeholder until real mesh nodes register
  "thomas-mind": {
    member: "thomas",
    prime: 53,                        // 2+8+3+7+15+6+12
    bloom: [2,8,3,7,15,6,12],         // spiky · sum 53
    tiers: ["T2","T3"],
    endpoint: null,
    cost: 0,
  },
  "estate-cascade": {
    member: "estate",
    prime: 510510,                    // fold = product of spine
    bloom: [3,5,5,5,5,5,8],           // estate balanced
    tiers: ["T2.5","T3"],
    endpoint: "https://fallcore.onrender.com/v1/cascade",
    cost: 0.001,
  },
};

// Cosine similarity over 7-vector blooms
export function bloomSimilarity(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  let dot=0, na=0, nb=0;
  for (let i=0;i<a.length;i++){ dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i]; }
  const d = Math.sqrt(na) * Math.sqrt(nb);
  return d ? dot/d : 0;
}

// 7-ring heuristic bloom for a query · matches the keyword table in export.py
const RING_KW = {
  R0:["intake","import","raw","ingest","input","seed"],
  R1:["parse","extract","signal","feature","tokenize"],
  R2:["gate","validate","rule","filter","permission"],
  R3:["ux","brand","design","palette","emotion"],
  R4:["build","render","ship","write","emit","forge"],
  R5:["verify","check","mirror","test","audit"],
  R6:["watch","log","hash","cerebellum","omega"],
};
export function queryBloom(text) {
  const t = (text||"").toLowerCase();
  return ["R0","R1","R2","R3","R4","R5","R6"]
    .map(r => RING_KW[r].reduce((s,k)=>s+(t.match(new RegExp(k,"g"))||[]).length,0));
}

// Cascade tier picker · T0 local first · escalate on confidence drop
export function pickTier(query, confidence = 1.0) {
  if (confidence >= 0.85) return "T0";
  if (confidence >= 0.70) return "T1";
  if (confidence >= 0.55) return "T2";
  if (confidence >= 0.40) return "T2.5";
  return "T3";
}

// Main entry · score every mesh member, pick the best for the tier
export function routeQuery(query, tier = "T0") {
  const qb = queryBloom(query);
  const candidates = Object.entries(MESH_MODELS)
    .filter(([_, m]) => m.tiers.includes(tier))
    .map(([name, m]) => ({ name, m, score: bloomSimilarity(qb, m.bloom) }))
    .sort((a,b) => b.score - a.score);
  const pick = candidates[0];
  if (!pick) {
    console.log(`[mesh] no member for tier ${tier} · fallback to simon-mind`);
    return MESH_MODELS["simon-mind"];
  }
  if (!pick.m.endpoint) {
    console.log(`[mesh] would route to ${pick.name} (score ${pick.score.toFixed(2)}) but no endpoint · stub`);
    return MESH_MODELS["simon-mind"];
  }
  console.log(`[mesh] routing tier=${tier} -> ${pick.name} (score ${pick.score.toFixed(2)})`);
  return pick.m;
}

// fall-signal estate awareness · broadcasts our prime
export function broadcastPresence() {
  try {
    const ch = new BroadcastChannel("fall-signal");
    ch.postMessage({
      kind: "presence",
      tool: "fallmind",
      prime: FALLMIND_PRIME,
      rings: ["R4","R6"],
      ts: Date.now(),
    });
  } catch (e) { /* node context · no BroadcastChannel · ignore */ }
}

export { MESH_MODELS, FALLMIND_PRIME };
