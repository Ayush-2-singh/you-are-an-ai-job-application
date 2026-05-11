let availableJobs = [];

const avoidTerms = ["unpaid", "senior", "lead", "manager", "registration fee", "training fee"];
const preferredTerms = ["paid", "stipend", "remote", "fresher", "student", "intern"];

const fields = {
  roles: document.querySelector("#roles"),
  skills: document.querySelector("#skills"),
  remote: document.querySelector("#remote"),
  minimumScore: document.querySelector("#minimumScore"),
  rankButton: document.querySelector("#rankButton"),
  jobList: document.querySelector("#jobList"),
  summary: document.querySelector("#summary"),
  count: document.querySelector("#count"),
  template: document.querySelector("#jobCardTemplate"),
};

fields.rankButton.addEventListener("click", loadJobs);
loadJobs();

async function loadJobs() {
  fields.rankButton.disabled = true;
  fields.rankButton.textContent = "Refreshing...";
  fields.summary.textContent = "Fetching internship opportunities...";

  try {
    const result = await fetch(`/api/jobs?ts=${Date.now()}`);
    if (!result.ok) throw new Error("Could not fetch jobs");
    const payload = await result.json();
    availableJobs = payload.jobs || [];
    renderRankedJobs(payload.source);
  } catch (error) {
    fields.summary.textContent = "Could not refresh jobs. Try again in a moment.";
    fields.jobList.replaceChildren();
    fields.count.textContent = "0";
  } finally {
    fields.rankButton.disabled = false;
    fields.rankButton.textContent = "Refresh and rank";
  }
}

function renderRankedJobs(source = "current-results") {
  const profile = getProfile();
  const ranked = availableJobs
    .map((job) => scoreJob(job, profile))
    .filter((item) => item.score >= profile.minimumScore)
    .sort((a, b) => b.score - a.score);

  fields.jobList.replaceChildren();
  fields.count.textContent = ranked.length;
  fields.summary.textContent =
    ranked.length === 1
      ? `1 role is ready for review from ${source}.`
      : `${ranked.length} roles are ready for review from ${source}.`;

  ranked.forEach(({ job, score, reason }) => {
    const card = fields.template.content.cloneNode(true);
    card.querySelector(".platform").textContent = job.platform;
    card.querySelector("h3").textContent = job.role;
    card.querySelector(".company").textContent = job.company;
    card.querySelector(".score").textContent = `${score}`;
    card.querySelector(".salary").textContent = job.salary || "Not listed";
    card.querySelector(".location").textContent = job.location || "Not listed";
    card.querySelector(".skills").textContent = job.required_skills.join(", ");
    card.querySelector(".reason").textContent = reason;
    card.querySelector(".message").textContent = recruiterMessage(job, profile);
    card.querySelector(".why").textContent = whyHire(profile);
    const link = card.querySelector(".apply");
    link.href = job.apply_link;
    link.textContent = "Review listing";
    fields.jobList.append(card);
  });
}

function getProfile() {
  return {
    roles: toList(fields.roles.value).map((item) => item.toLowerCase()),
    skills: toList(fields.skills.value),
    remote: fields.remote.value,
    minimumScore: Number(fields.minimumScore.value || 65),
  };
}

function scoreJob(job, profile) {
  const text = [
    job.company,
    job.role,
    job.platform,
    job.location,
    job.salary,
    job.description,
    job.required_skills.join(" "),
  ]
    .join(" ")
    .toLowerCase();

  const resumeSkills = new Set(profile.skills.map((skill) => skill.toLowerCase()));
  const jobSkills = job.required_skills.map((skill) => skill.toLowerCase());
  const overlap = jobSkills.filter((skill) => resumeSkills.has(skill));
  const roleHit = profile.roles.some((role) => text.includes(role.replace("internship", "intern")));
  const preferredHits = preferredTerms.filter((term) => text.includes(term));
  const avoidHits = avoidTerms.filter((term) => text.includes(term));

  let score = 25;
  score += Math.round(35 * (overlap.length / Math.max(jobSkills.length, 1)));
  if (roleHit) score += 10;
  if (profile.remote !== "remote" || text.includes("remote") || text.includes("work from home")) score += 8;
  if (text.includes("₹") || text.includes("stipend") || text.includes("paid")) score += 8;
  if (text.includes("intern") || text.includes("fresher") || text.includes("student")) score += 7;
  score += Math.min(10, preferredHits.length * 2);
  score -= avoidHits.length * 25;

  const safeScore = Math.max(0, Math.min(100, score));
  const reasonParts = [];
  if (overlap.length) reasonParts.push(`Strong overlap: ${titleCaseList(overlap)}.`);
  if (preferredHits.length) reasonParts.push(`Preference match: ${preferredHits.slice(0, 4).join(", ")}.`);
  if (job.salary) reasonParts.push(`Compensation listed: ${job.salary}.`);
  if (avoidHits.length) reasonParts.push(`Review carefully: ${avoidHits.join(", ")}.`);

  return {
    job,
    score: safeScore,
    reason: reasonParts.join(" ") || "Relevant role based on your preferences.",
  };
}

function recruiterMessage(job, profile) {
  return `Hi, I'm Ayush Singh. I'm interested in the ${job.role} role at ${job.company}. I have hands-on experience with ${profile.skills
    .slice(0, 8)
    .join(", ")}, including deployed web projects and internship work. I'd be grateful if you could review my profile for this opportunity.`;
}

function whyHire(profile) {
  return `You should hire me because I have hands-on web development experience, live deployed projects, and a strong learning mindset. My background in ${profile.skills
    .slice(0, 8)
    .join(", ")} helps me build responsive, practical applications, and I can contribute consistently as an intern while improving quickly through feedback.`;
}

function toList(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function titleCaseList(items) {
  return items.map((item) => item.replace(/\b\w/g, (letter) => letter.toUpperCase())).join(", ");
}
