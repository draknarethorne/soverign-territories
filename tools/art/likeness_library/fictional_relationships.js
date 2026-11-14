/* Manually authored fiction only. No matcher, photo, or inferred-family inputs. */
"use strict";
(() => {
  const FILE = ".fictional-relationships.json";
  const ROLES = ["ally", "rival", "mentor", "student", "companion", "spouse",
    "sibling", "parent", "child", "other"];
  const MAX_BYTES = 8 * 1024 * 1024, MAX_EVENTS = 2000;
  const copy = value => JSON.parse(JSON.stringify(value));
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const fail = message => { throw new Error(message); };
  const keys = (value, names) => {
    if (!value || typeof value !== "object" || Array.isArray(value) ||
        Object.keys(value).sort().join(",") !== names.slice().sort().join(",")) fail("Unexpected document fields.");
  };
  const text = (value, max) => {
    if (typeof value !== "string" || !value.trim() || value.length > max ||
        /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)) fail("Invalid or oversized text.");
  };
  const empty = () => ({schemaVersion: 1, revision: 0, history: []});
  const relationId = id => {
    if (typeof id !== "string" || !/^rel_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id))
      fail("Invalid relationship ID.");
  };
  function relationship(value, people) {
    keys(value, ["id", "first", "second", "role", "note", "status", "rejectionReason"]);
    relationId(value.id);
    for (const id of [value.first, value.second]) {
      text(id, 160);
      if (!people.has(id)) fail("Unknown person ID. Regenerate this report if the catalogue changed.");
    }
    if (value.first === value.second || !ROLES.includes(value.role)) fail("Invalid characters or fictional role.");
    text(value.note, 2000);
    if (!["active", "rejected"].includes(value.status)) fail("Invalid assignment status.");
    if (value.status === "rejected") text(value.rejectionReason, 1000);
    else if (value.rejectionReason !== "") fail("An active assignment cannot have a rejection reason.");
  }
  function duplicate(states, after) {
    if (!after) return;
    for (const value of states.values()) {
      if (value.id !== after.id && value.role === after.role &&
          [value.first, value.second].sort().join("\0") === [after.first, after.second].sort().join("\0"))
        fail("This pair and role already exist, possibly rejected. Edit or undo that entry instead.");
    }
  }
  function validate(doc, people) {
    keys(doc, ["schemaVersion", "revision", "history"]);
    if (doc.schemaVersion !== 1 || !Array.isArray(doc.history) || doc.history.length > MAX_EVENTS ||
        !Number.isSafeInteger(doc.revision) || doc.revision !== doc.history.length) fail("Invalid revision or history limit.");
    const states = new Map(), latest = new Map(), used = new Set();
    doc.history.forEach((event, index) => {
      keys(event, ["revision", "at", "action", "relationshipId", "before", "after", "undoOf"]);
      if (event.revision !== index + 1 || typeof event.at !== "string" ||
          !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(event.at) ||
          !Number.isFinite(Date.parse(event.at))) fail("Invalid history sequence or timestamp.");
      relationId(event.relationshipId);
      const before = states.get(event.relationshipId) || null;
      if (event.before) relationship(event.before, people);
      if (event.after) relationship(event.after, people);
      if (!same(event.before, before) || [event.before, event.after].some(v => v && v.id !== event.relationshipId))
        fail("History does not replay exactly.");
      if (event.action === "create") {
        if (used.has(event.relationshipId) || before || !event.after || event.after.status !== "active")
          fail("Invalid creation.");
      } else if (event.action === "edit") {
        if (!before || !event.after || event.after.status !== before.status ||
            event.after.rejectionReason !== before.rejectionReason) fail("Invalid edit.");
      } else if (event.action === "reject") {
        if (!before || before.status !== "active" || !event.after ||
            !same({...event.after, status: before.status, rejectionReason: before.rejectionReason}, before) ||
            event.after.status !== "rejected") fail("Invalid rejection.");
      } else if (event.action === "undo") {
        const previous = latest.get(event.relationshipId);
        if (!previous || event.undoOf !== previous.revision || !same(event.after, previous.before))
          fail("Undo must exactly restore this relationship's preceding snapshot.");
      } else fail("Unknown history action.");
      if (event.action !== "undo" && event.undoOf !== null) fail("Unexpected undo reference.");
      duplicate(states, event.after);
      used.add(event.relationshipId);
      if (event.after) states.set(event.relationshipId, copy(event.after));
      else states.delete(event.relationshipId);
      latest.set(event.relationshipId, event);
    });
    return {states, latest};
  }
  function parse(raw, people) {
    if (new TextEncoder().encode(raw).length > MAX_BYTES) fail("Narrative file exceeds the 8 MiB limit.");
    const doc = raw === "" ? empty() : JSON.parse(raw);
    validate(doc, people);
    return doc;
  }
  function change(doc, command, people) {
    const {states, latest} = validate(doc, people);
    relationId(command.id);
    const before = states.get(command.id) || null;
    let after, undoOf = null;
    if (command.action === "create") {
      after = {id: command.id, first: command.first, second: command.second,
        role: command.role, note: command.note, status: "active", rejectionReason: ""};
    } else if (command.action === "edit") {
      if (!before) fail("Assignment no longer exists.");
      after = {...before, first: command.first, second: command.second, role: command.role, note: command.note};
    } else if (command.action === "reject") {
      if (!before) fail("Assignment no longer exists.");
      after = {...before, status: "rejected", rejectionReason: command.reason};
    } else if (command.action === "undo") {
      const previous = latest.get(command.id);
      if (!previous) fail("No history to undo.");
      after = copy(previous.before);
      undoOf = previous.revision;
    } else fail("Unknown command.");
    const next = copy(doc);
    next.revision++;
    next.history.push({revision: next.revision, at: new Date().toISOString(), action: command.action,
      relationshipId: command.id, before: copy(before), after, undoOf});
    validate(next, people);
    if (new TextEncoder().encode(JSON.stringify(next)).length > MAX_BYTES) fail("Narrative history is full.");
    return next;
  }
  async function read(handle) {
    const file = await handle.getFile();
    if (file.size > MAX_BYTES) fail("Narrative file exceeds the 8 MiB limit.");
    return file.text();
  }
  async function persist(session, command) {
    if (!session.handle || session.raw === null) fail("Connect the library narrative file before saving.");
    const raw = await read(session.handle);
    if (raw !== session.raw) fail("Stale file conflict. Reload and review the current file before trying again.");
    const next = change(parse(raw, session.people), command, session.people);
    const output = JSON.stringify(next, null, 2) + "\n";
    if (new TextEncoder().encode(output).length > MAX_BYTES) fail("Narrative history is full.");
    let writer;
    try {
      writer = await session.handle.createWritable({mode: "exclusive"});
      if (await read(session.handle) !== raw) fail("Stale file conflict before write. Reload first.");
      await writer.write(output);
      if (await read(session.handle) !== raw) fail("Stale file conflict during write. Reload first.");
      await writer.close();
      writer = null;
      if (await read(session.handle) !== output) fail("Write verification failed. Reconnect and inspect the file.");
      session.raw = output;
      session.doc = next;
      return next;
    } catch (error) {
      if (writer) { try { await writer.abort(); } catch (_) { /* Preserve original failure. */ } }
      throw error;
    }
  }
  globalThis.FictionalRelationships = {FILE, ROLES, empty, validate, parse, change, persist, read};
  if (typeof document === "undefined") return;
  const $ = id => document.getElementById(id);
  const labels = JSON.parse($("fictional-people").textContent);
  const people = new Set(labels.map(p => p.id)), names = new Map(labels.map(p => [p.id, p.name]));
  const session = {people, handle: null, raw: null, doc: empty()};
  let editing = null, busy = false;
  const say = (message, error = false) => {
    $("connection").textContent = message;
    $("connection").className = error ? "error" : "";
  };
  const clear = () => {
    editing = null;
    $("relationship-form").reset();
    $("editing").textContent = "New assignment";
    $("save").textContent = "Save active fictional assignment";
  };
  function selectors() {
    const query = $("search").value.toLocaleLowerCase();
    const matches = labels.filter(p => (p.name + " " + p.id).toLocaleLowerCase().includes(query));
    for (const id of ["first", "second"]) {
      const select = $(id), previous = select.value;
      const visible = labels.filter(p => matches.includes(p) || p.id === previous);
      select.replaceChildren(new Option("Choose a fictional character", ""));
      for (const p of visible) select.add(new Option(p.name + " · " + p.id, p.id));
      select.value = previous;
    }
    $("matches").textContent = `${matches.length} matching characters; current selections retained.`;
  }
  function draw() {
    const {states, latest} = validate(session.doc, people);
    $("history").textContent = JSON.stringify(session.doc.history, null, 2);
    $("assignments").replaceChildren();
    const button = (parent, title, action, needsFile = true) => {
      const b = document.createElement("button");
      b.type = "button"; b.textContent = title;
      b.disabled = busy || (needsFile && !session.handle);
      b.onclick = action; parent.append(b);
    };
    for (const [id, event] of latest) {
      const r = states.get(id), article = document.createElement("article");
      const heading = document.createElement("h3");
      heading.textContent = r ? `${names.get(r.first)} → ${names.get(r.second)} · ${r.role} · ${r.status}` :
        `${id} · removed by undo (history retained)`;
      article.append(heading);
      if (r) {
        const note = document.createElement("p");
        note.textContent = `${r.first} → ${r.second}\n${r.note}` +
          (r.status === "rejected" ? `\nRejection reason: ${r.rejectionReason}` : "");
        note.style.whiteSpace = "pre-wrap"; article.append(note);
        button(article, "Edit fictional assignment", () => {
          editing = id; $("search").value = ""; selectors();
          for (const key of ["first", "second", "role", "note"]) $(key).value = r[key];
          $("editing").textContent = `Editing ${id} (${r.status}; status retained)`;
          $("save").textContent = `Save edit (${r.status})`;
          $("first").focus();
        });
        if (r.status === "active") button(article, "Reject fictional assignment", () =>
          mutate({id, action: "reject", reason: $("reason").value}));
      }
      button(article, `Undo latest change (#${event.revision})`, () => mutate({id, action: "undo"}));
      $("assignments").append(article);
    }
    if (!latest.size) $("assignments").textContent = "No fictional assignments. No inferred relationships have been imported.";
    $("save").disabled = busy || !session.handle;
    $("connect").disabled = busy;
    $("reload").disabled = busy || !session.handle;
    $("import").disabled = busy;
    $("new").disabled = busy;
    $("export").disabled = busy;
  }
  async function operation(work) {
    if (busy) return;
    busy = true; draw();
    try { await work(); }
    catch (error) { say(`Not saved / operation failed: ${error.message}`, true); }
    finally { busy = false; draw(); }
  }
  async function mutate(command) {
    return operation(async () => {
      if (!navigator.locks) fail("Guarded saves require Web Locks support.");
      await navigator.locks.request("sovereign-fictional-relationships", {mode: "exclusive"}, () => persist(session, command));
      clear();
      say(`Saved and verified in ${FILE} · revision ${session.doc.revision}. Assignments are active unless rejected or undone.`);
    });
  }
  $("connect").onclick = () => operation(async () => {
    if (!window.showDirectoryPicker || !navigator.locks) fail("Direct file access unavailable. Import is read-only; export is only a copy.");
    const directory = await window.showDirectoryPicker({mode: "readwrite", id: "sovereign-narrative-library"});
    const handle = await directory.getFileHandle(FILE, {create: true});
    const raw = await read(handle), doc = parse(raw, people);
    session.handle = handle; session.raw = raw; session.doc = doc;
    clear();
    say(`Connected to ${directory.name}\\${FILE} · revision ${doc.revision}. ` +
      (raw === "" ? "Empty file; no narrative document saved yet." : "Loaded persisted history."));
  });
  $("reload").onclick = () => operation(async () => {
    const raw = await read(session.handle), doc = parse(raw, people);
    session.raw = raw; session.doc = doc; clear();
    say(`Reloaded connected narrative file · revision ${doc.revision}.`);
  });
  $("import").onchange = () => operation(async () => {
    const file = $("import").files[0];
    if (!file) return;
    const raw = await read({getFile: async () => file}), doc = parse(raw, people);
    session.handle = null; session.raw = null; session.doc = doc; clear();
    say("Imported for read-only inspection. NOT connected or saved to the library; reconnect to edit.");
  });
  $("export").onclick = () => {
    const blob = new Blob([JSON.stringify(session.doc, null, 2) + "\n"], {type: "application/json"});
    const url = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = url; a.download = "fictional-relationships-copy.json"; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    say("Exported a history copy for download. This is NOT a library save; check your browser downloads.");
  };
  $("relationship-form").onsubmit = event => {
    event.preventDefault();
    mutate({action: editing ? "edit" : "create", id: editing || "rel_" + crypto.randomUUID(),
      first: $("first").value, second: $("second").value, role: $("role").value, note: $("note").value});
  };
  $("new").onclick = clear;
  $("search").oninput = selectors;
  for (const role of ROLES) $("role").add(new Option(role, role));
  selectors(); draw();
})();
