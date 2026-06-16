#!/usr/bin/env node
/* clean-demo-branches.js — delete all local edit/* branches the demo
   created. Safe: only touches branches under the edit/ namespace, and
   never the branch you currently have checked out. */
"use strict";
const { execFileSync } = require("child_process");
const path = require("path");
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");
function git(args) { return execFileSync("git", args, { cwd: REPO_ROOT, encoding: "utf8" }).trim(); }

const current = git(["rev-parse", "--abbrev-ref", "HEAD"]);
const branches = git(["branch", "--list", "edit/*", "--format=%(refname:short)"])
  .split("\n").map((s) => s.trim()).filter(Boolean);

if (!branches.length) { console.log("No edit/* demo branches to clean."); process.exit(0); }

let n = 0;
for (const b of branches) {
  if (b === current) { console.log(`skip ${b} (checked out)`); continue; }
  git(["branch", "-D", b]);
  console.log(`deleted ${b}`);
  n++;
}
console.log(`\nRemoved ${n} demo branch${n === 1 ? "" : "es"}.`);
