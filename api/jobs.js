const fallbackJobs = [
  {
    company: "Optimspace",
    role: "Web Developer Intern",
    platform: "Indeed",
    location: "Remote",
    salary: "₹7,500 - ₹15,000/month",
    description:
      "Build responsive websites using HTML, CSS, JavaScript. React, Angular, or Node.js preferred. Internship certificate and portfolio projects.",
    required_skills: ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    apply_link: "https://in.indeed.com/q-web-dev-intern-l-remote-jobs.html",
  },
  {
    company: "SproutXP",
    role: "Backend Developer Intern",
    platform: "Indeed",
    location: "Remote",
    salary: "₹15,000 - ₹20,000/month",
    description:
      "Assist in backend services, REST APIs, databases, Git/GitHub. Skills: Java, Python, JavaScript, Node.js, Spring Boot, SQL, MongoDB, Postman.",
    required_skills: ["Java", "REST APIs", "SQL", "Git", "Spring Boot", "Node.js"],
    apply_link: "https://in.indeed.com/q-remote-java-developer-intern-jobs.html",
  },
  {
    company: "Emoolar Technology",
    role: "Full Stack Development Intern",
    platform: "Web",
    location: "Remote",
    salary: "₹18,000/month",
    description:
      "Remote paid full stack internship for building web applications with HTML, CSS, JavaScript, frontend and backend development.",
    required_skills: ["HTML", "CSS", "JavaScript", "Full Stack Development", "REST APIs"],
    apply_link:
      "https://www.collegesearch.in/internships/full-stack-development-work-from-home-jobinternship-at-emoolar-technology-private-limited-3139825",
  },
  {
    company: "VedhaAI Infotech",
    role: "Full Stack Developer Intern",
    platform: "Indeed",
    location: "Remote",
    salary: "₹5,000 - ₹9,500/month",
    description:
      "Full stack internship with HTML, CSS, JavaScript, React, Angular, Vue, Node, Python, Java, MySQL, MongoDB, and Git.",
    required_skills: ["HTML", "CSS", "JavaScript", "React", "Java", "Git", "MySQL"],
    apply_link: "https://in.indeed.com/m/jobs?l=India&q=Internship+Full+Stack+Java+Developer",
  },
  {
    company: "Keshav Kingdom",
    role: "Java Backend Developer Intern",
    platform: "LinkedIn",
    location: "Remote",
    salary: "₹5,000/month",
    description:
      "Remote paid internship for Java backend development. Work with Java, Spring Boot, RESTful APIs, databases, Git, OOP.",
    required_skills: ["Java", "Spring Boot", "REST APIs", "Git", "OOP", "MySQL"],
    apply_link:
      "https://in.linkedin.com/jobs/view/back-end-developer-intern-at-keshav-kingdom-4329972282",
  },
  {
    company: "Indian Institute of Robotics",
    role: "Full Stack Development Intern",
    platform: "Web",
    location: "Remote",
    salary: "₹12,000/month",
    description:
      "Work from home internship using React, Next.js, TypeScript, Tailwind, Node, NestJS, REST APIs, and PostgreSQL.",
    required_skills: ["React", "Next.js", "TypeScript", "Node.js", "REST APIs", "PostgreSQL"],
    apply_link:
      "https://www.collegesearch.in/internships/full-stack-development-work-from-home-jobinternship-at-indian-institute-of-robotics-3121614",
  },
  {
    company: "Infrabyte Consulting",
    role: "Junior Java Developer Intern",
    platform: "Web",
    location: "Remote",
    salary: "₹18,500/month",
    description:
      "Java internship focused on backend logic, APIs, Spring, Spring Boot, and practical software development.",
    required_skills: ["Java", "Spring Boot", "REST APIs", "Backend Development", "Git"],
    apply_link:
      "https://bebee.com/in/jobs/junior-java-developer-intern-infrabyte-consulting--theirstack-663645498",
  },
  {
    company: "Marketlist Media",
    role: "Web Developer Intern",
    platform: "Indeed",
    location: "Remote",
    salary: "₹5,000 - ₹100,000/month",
    description:
      "Web development internship using HTML, CSS, JavaScript, React, Django, PHP, Git, APIs, and database basics.",
    required_skills: ["HTML", "CSS", "JavaScript", "React", "Git", "REST APIs"],
    apply_link: "https://in.indeed.com/viewjob?cmp=Marketlist-Media&jk=0ed53372a33f08f1",
  },
  {
    company: "Myraid",
    role: "Full Stack Development Intern",
    platform: "Web",
    location: "Remote",
    salary: "₹2,500/month",
    description:
      "Full stack development internship using Node.js, Next.js, Redis, WebSockets, SQL, and NoSQL databases.",
    required_skills: ["Node.js", "Next.js", "JavaScript", "SQL", "NoSQL", "WebSockets"],
    apply_link:
      "https://www.collegesearch.in/internships/full-stack-development-work-from-home-jobinternship-at-myraid-3133068",
  },
  {
    company: "Remote Startup",
    role: "Frontend Developer Intern",
    platform: "Web",
    location: "Remote",
    salary: "Paid internship",
    description:
      "Frontend internship for students and freshers. Build responsive interfaces with HTML, CSS, JavaScript, React, Git, and REST APIs.",
    required_skills: ["HTML", "CSS", "JavaScript", "React", "Git", "REST APIs"],
    apply_link: "https://www.linkedin.com/jobs/search/?keywords=frontend%20developer%20intern%20remote%20paid",
  },
];

const searchRoles = [
  "remote paid web developer intern India",
  "remote paid Java developer intern India",
  "remote paid full stack developer intern India",
];

export default async function handler(request, response) {
  const jobs = await liveJobs();
  response.setHeader("Cache-Control", "s-maxage=600, stale-while-revalidate=1800");
  response.status(200).json({
    source: process.env.SERPAPI_API_KEY ? "live-search-with-fallback" : "curated-fallback",
    updated_at: new Date().toISOString(),
    jobs: dedupe([...jobs, ...fallbackJobs]).slice(0, 25),
  });
}

async function liveJobs() {
  const apiKey = process.env.SERPAPI_API_KEY;
  if (!apiKey) return [];

  const found = [];
  for (const role of searchRoles) {
    const url = new URL("https://serpapi.com/search.json");
    url.searchParams.set("engine", "google");
    url.searchParams.set("q", `${role} LinkedIn Indeed Internshala apply`);
    url.searchParams.set("num", "10");
    url.searchParams.set("api_key", apiKey);

    const result = await fetch(url);
    if (!result.ok) continue;
    const payload = await result.json();
    for (const item of payload.organic_results || []) {
      found.push({
        company: guessCompany(item.title || ""),
        role: guessRole(item.title || "", role),
        platform: platformFromUrl(item.link || ""),
        location: "Remote / India",
        salary: guessSalary(item.snippet || ""),
        description: item.snippet || "",
        required_skills: guessSkills(`${item.title || ""} ${item.snippet || ""}`),
        apply_link: item.link || "",
      });
    }
  }
  return found;
}

function dedupe(jobs) {
  const seen = new Set();
  return jobs.filter((job) => {
    const key = (job.apply_link || `${job.company}-${job.role}`).toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function platformFromUrl(url) {
  const value = url.toLowerCase();
  if (value.includes("linkedin")) return "LinkedIn";
  if (value.includes("indeed")) return "Indeed";
  if (value.includes("internshala")) return "Internshala";
  if (value.includes("instagram")) return "Instagram";
  return "Web";
}

function guessCompany(title) {
  if (title.includes(" at ")) return title.split(" at ").at(-1).split("|")[0].trim();
  return "Company not listed";
}

function guessRole(title, fallback) {
  if (title.includes(" at ")) return title.split(" at ")[0].trim();
  return fallback.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function guessSalary(text) {
  if (text.includes("₹") || /stipend|paid/i.test(text)) return "Mentioned in listing";
  return "";
}

function guessSkills(text) {
  const skills = ["HTML", "CSS", "JavaScript", "React", "Node.js", "Java", "Spring Boot", "MySQL", "Git", "REST APIs"];
  const lowered = text.toLowerCase();
  return skills.filter((skill) => lowered.includes(skill.toLowerCase()));
}
