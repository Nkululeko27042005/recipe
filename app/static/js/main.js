/* ============================================================
   RecipE — Frontend interactions
   - Like / Dislike / Save (AJAX)
   - Follow / Unfollow
   - Comment post / reply / delete
   - Recipe form dynamic lists
   - Toast notifications
   - Mobile nav toggle
   ============================================================ */

(function () {
  "use strict";

  /* -------------------- Helpers -------------------- */
  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const authed  = document.body.dataset.authed === "true";
  const myUserId = document.body.dataset.userId || null;

  function toast(message, kind = "info") {
    const stack = $("#toast-stack");
    if (!stack) return;
    const el = document.createElement("div");
    el.className = `toast toast--${kind}`;
    el.textContent = message;
    stack.appendChild(el);
    setTimeout(() => el.classList.add("toast--in"), 10);
    setTimeout(() => {
      el.classList.remove("toast--in");
      setTimeout(() => el.remove(), 250);
    }, 2600);
  }

  async function request(url, { method = "GET", body = null, form = null } = {}) {
    const opts = { method, credentials: "same-origin", headers: {} };
    if (body) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    if (form) {
      opts.body = form; // FormData
    }
    if (!body && !form && method !== "GET") {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify({});
    }
    const res = await fetch(url, opts);
    let data;
    try { data = await res.json(); } catch { data = { success: res.ok }; }
    return { ok: res.ok, status: res.status, data };
  }

  function requireAuth() {
    if (!authed) {
      toast("Please log in first.", "warning");
      return false;
    }
    return true;
  }

  /* -------------------- Mobile Nav -------------------- */
  document.addEventListener("click", (e) => {
    if (e.target.matches("[data-nav-toggle]")) {
      $("[data-nav]")?.classList.toggle("site-nav--open");
    }
  });

/* -------------------- Theme Toggle -------------------- */
(function initTheme() {
  const saved = localStorage.getItem("recipe-theme");
  if (saved === "dark") document.body.classList.add("theme-dark");
  document.addEventListener("click", (e) => {
    if (!e.target.closest("[data-theme-toggle]")) return;
    document.body.classList.toggle("theme-dark");
    const isDark = document.body.classList.contains("theme-dark");
    localStorage.setItem("recipe-theme", isDark ? "dark" : "light");
    $$("[data-theme-toggle]").forEach(b => b.textContent = isDark ? "☀" : "🌙");
  });
  // sync icon on load
  if (document.body.classList.contains("theme-dark")) {
    $$("[data-theme-toggle]").forEach(b => b.textContent = "☀");
  }
})();

  /* -------------------- Reactions (Like / Dislike) -------------------- */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action='like'], [data-action='dislike']");
    if (!btn) return;
    e.preventDefault();
    if (!requireAuth()) return;

    const recipeId = btn.dataset.recipeId;
    const isLike   = btn.dataset.action === "like";
    const already  = btn.classList.contains("is-active");
    const value    = already ? 0 : (isLike ? 1 : -1);

    const { ok, data } = await request(`/reactions/recipe/${recipeId}`, {
      method: "POST",
      body: { value },
    });
    if (!ok || !data.success) return toast(data.message || "Could not update.", "danger");

    const bar = btn.closest("[data-action-bar]");
    if (bar) {
      bar.querySelector(".likes-count").textContent    = data.data.likes;
      bar.querySelector(".dislikes-count").textContent = data.data.dislikes;
      $$("[data-action='like'],[data-action='dislike']", bar)
        .forEach((b) => b.classList.remove("is-active"));
      if (data.data.my_reaction === 1)  bar.querySelector("[data-action='like']").classList.add("is-active");
      if (data.data.my_reaction === -1) bar.querySelector("[data-action='dislike']").classList.add("is-active");
    }
  });

  /* -------------------- Save / Unsave -------------------- */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action='save']");
    if (!btn) return;
    e.preventDefault();
    if (!requireAuth()) return;

    const recipeId = btn.dataset.recipeId;
    const already  = btn.classList.contains("is-active");
    const url      = `/recipes/${recipeId}/save`;

    const { ok, data } = await request(url, { method: already ? "DELETE" : "POST" });
    if (!ok || !data.success) return toast(data.message || "Could not save.", "danger");

    const isSaved = data.data?.is_saved ?? !already;
    btn.classList.toggle("is-active", isSaved);
    toast(isSaved ? "Saved to your cookbook." : "Removed from saved.", "success");
  });

  /* -------------------- Follow / Unfollow -------------------- */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action='follow']");
    if (!btn) return;
    e.preventDefault();
    if (!requireAuth()) return;

    const userId    = btn.dataset.userId;
    const following = btn.dataset.following === "true";
    const url       = `/follows/${userId}`;

    const { ok, data } = await request(url, { method: following ? "DELETE" : "POST" });
    if (!ok || !data.success) return toast(data.message || "Could not update follow.", "danger");

    btn.dataset.following = String(!following);
    btn.textContent = following ? "Follow" : "Unfollow";
    btn.classList.toggle("btn--ghost", !following);
    btn.classList.toggle("btn--green", following);
    toast(following ? "Unfollowed." : "Followed!", "success");
  });

  /* -------------------- Comments -------------------- */
  document.addEventListener("submit", async (e) => {
    const form = e.target.closest("[data-comment-form]");
    if (!form) return;
    e.preventDefault();

    const recipeId  = form.dataset.recipeId;
    const bodyField = form.querySelector("[name='body']");
    const body      = bodyField.value.trim();
    if (!body) return;

    const { ok, data } = await request(`/comments/recipe/${recipeId}`, {
      method: "POST",
      body: { body },
    });
    if (!ok || !data.success) return toast(data.message || "Could not post.", "danger");

    bodyField.value = "";
    toast("Comment posted.", "success");
    await reloadComments(recipeId);
  });

  document.addEventListener("click", async (e) => {
    const replyBtn = e.target.closest("[data-action='reply']");
    if (replyBtn) {
      e.preventDefault();
      if (!requireAuth()) return;
      const commentId = replyBtn.dataset.commentId;
      const text = prompt("Your reply:");
      if (!text) return;

      const wrapper = replyBtn.closest("[data-recipe-id]") || document;
      const recipeId = wrapper.dataset.recipeId
                    || $("[data-comment-list]")?.dataset.recipeId;
      if (!recipeId) return;

      const { ok, data } = await request(`/comments/recipe/${recipeId}`, {
        method: "POST",
        body: { body: text, parent_id: commentId },
      });
      if (!ok || !data.success) return toast(data.message || "Could not reply.", "danger");
      toast("Reply added.", "success");
      await reloadComments(recipeId);
      return;
    }

    const delBtn = e.target.closest("[data-action='delete-comment']");
    if (delBtn) {
      e.preventDefault();
      if (!requireAuth()) return;
      if (!confirm("Delete this comment?")) return;
      const commentId = delBtn.dataset.commentId;

      const { ok, data } = await request(`/comments/${commentId}`, { method: "DELETE" });
      if (!ok || !data.success) return toast(data.message || "Could not delete.", "danger");
      toast("Comment deleted.", "success");

      const list = $("[data-comment-list]");
      if (list) await reloadComments(list.dataset.recipeId);
    }
  });

  async function reloadComments(recipeId) {
    const list = $(`[data-comment-list][data-recipe-id='${recipeId}']`);
    if (!list) return;
    const res = await fetch(`/comments/recipe/${recipeId}`, { credentials: "same-origin" });
    if (!res.ok) return;
    const comments = await res.json();

    list.innerHTML = comments.length
      ? comments.map(renderComment).join("")
      : '<p class="muted">No comments yet — be the first.</p>';
  }

  function renderComment(c) {
    const replies = (c.replies || []).map((r) => `
      <div class="comment reply" data-comment-id="${r.id}">
        <div class="meta"><strong>${escapeHtml(r.author.username)}</strong> · ${formatDate(r.created_at)}</div>
        <div class="comment-body">${escapeHtml(r.body)}</div>
        ${myUserId && String(r.author.id) === String(myUserId) ? `
          <button class="btn btn--sm btn--danger mt-1" data-action="delete-comment" data-comment-id="${r.id}">Delete</button>
        ` : ""}
      </div>`).join("");

    return `
      <div class="comment" data-comment-id="${c.id}">
        <div class="meta"><strong>${escapeHtml(c.author.username)}</strong> · ${formatDate(c.created_at)}</div>
        <div class="comment-body">${escapeHtml(c.body)}</div>
        ${myUserId ? `
          <div class="row mt-1">
            <button class="btn btn--sm btn--ghost" data-action="reply" data-comment-id="${c.id}">Reply</button>
            ${String(c.author.id) === String(myUserId) ? `
              <button class="btn btn--sm btn--danger" data-action="delete-comment" data-comment-id="${c.id}">Delete</button>
            ` : ""}
          </div>` : ""}
        ${replies ? `<div class="comment-replies">${replies}</div>` : ""}
      </div>`;
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, (s) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[s]));
  }

  function formatDate(iso) {
    try { return new Date(iso).toLocaleString(); } catch { return iso; }
  }

  /* -------------------- Delete Recipe -------------------- */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-action='delete-recipe']");
    if (!btn) return;
    e.preventDefault();
    if (!confirm("Delete this recipe permanently?")) return;

    const id = btn.dataset.recipeId;
    const { ok, data } = await request(`/recipes/${id}`, { method: "DELETE" });
    if (!ok || !data.success) return toast(data.message || "Could not delete.", "danger");
    toast("Recipe deleted.", "success");
    setTimeout(() => (window.location.href = "/"), 700);
  });

  /* -------------------- Recipe Form — Dynamic Lists -------------------- */
  document.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add-row]");
    if (addBtn) {
      e.preventDefault();
      const kind = addBtn.dataset.addRow;
      const list = document.querySelector(`[data-list='${kind}']`);
      if (!list) return;
      const row = kind === "ingredients" ? ingredientRow() : stepRow();
      list.appendChild(row);
      row.querySelector("input,textarea")?.focus();
      return;
    }

    const removeBtn = e.target.closest("[data-remove-row]");
    if (removeBtn) {
      e.preventDefault();
      const row = removeBtn.closest(".dynamic-row");
      const list = row.parentElement;
      row.remove();
      if (list && list.dataset.list === "steps") renumberSteps(list);
    }
  });

  function ingredientRow() {
    const li = document.createElement("li");
    li.className = "dynamic-row";
    li.innerHTML = `
      <input type="text" name="ing_name[]" placeholder="Name" required />
      <input type="text" name="ing_qty[]" placeholder="Qty" />
      <input type="text" name="ing_unit[]" placeholder="Unit" />
      <input type="text" name="ing_weight[]" placeholder="Weight" />
      <input type="text" name="ing_notes[]" placeholder="Notes" />
      <button type="button" class="btn btn--sm btn--danger" data-remove-row>✖</button>
    `;
    return li;
  }

  function stepRow() {
    const li = document.createElement("li");
    li.className = "dynamic-row";
    li.innerHTML = `
      <textarea name="step_text[]" rows="2" placeholder="Describe this step…" required></textarea>
      <button type="button" class="btn btn--sm btn--danger" data-remove-row>✖</button>
    `;
    return li;
  }

  function renumberSteps(list) {
    /* purely visual: the CSS uses a counter, so no attribute rewrite needed */
  }

  /* -------------------- Recipe Form Submit (multipart) -------------------- */
  document.addEventListener("submit", async (e) => {
    const form = e.target.closest("[data-recipe-form]");
    if (!form) return;
    e.preventDefault();

    const fd = new FormData();
    fd.append("title", form.querySelector("#title").value);
    fd.append("description", form.querySelector("#description").value || "");
    fd.append("category", form.querySelector("#category").value || "");

    // Ingredients
    const ingNames   = form.querySelectorAll("[name='ing_name[]']");
    const ingQtys    = form.querySelectorAll("[name='ing_qty[]']");
    const ingUnits   = form.querySelectorAll("[name='ing_unit[]']");
    const ingWeights = form.querySelectorAll("[name='ing_weight[]']");
    const ingNotes   = form.querySelectorAll("[name='ing_notes[]']");
    const ingredients = [];
    ingNames.forEach((el, i) => {
      if (!el.value.trim()) return;
      ingredients.push({
        name:     el.value.trim(),
        quantity: ingQtys[i]?.value || "",
        unit:     ingUnits[i]?.value || "",
        weight:   ingWeights[i]?.value || "",
        notes:    ingNotes[i]?.value || "",
      });
    });
    fd.append("ingredients", JSON.stringify(ingredients));

    // Steps
    const steps = Array.from(form.querySelectorAll("[name='step_text[]']"))
      .map((el) => ({ instruction: el.value.trim() }))
      .filter((s) => s.instruction);
    fd.append("steps", JSON.stringify(steps));

    // Images
    form.querySelectorAll("[name='images']").forEach((inp) => {
      Array.from(inp.files || []).forEach((f) => fd.append("images", f));
    });

    // Removals
    form.querySelectorAll("[name='remove_image_ids[]']:checked").forEach((cb) => {
      fd.append("remove_image_ids", cb.value);
    });

    // Video
    const videoInput = form.querySelector("[name='video']");
    if (videoInput && videoInput.files[0]) fd.append("video", videoInput.files[0]);

    const url = form.getAttribute("action");
    const isEdit = /\/recipes\/\d+$/.test(url);
    const { ok, data } = await request(url, { method: isEdit ? "PUT" : "POST", form: fd });
    if (!ok || !data.success) {
      return toast(data.message || "Could not save recipe.", "danger");
    }
    toast("Recipe saved.", "success");
    setTimeout(() => {
      window.location.href = `/recipes/${data.data.id}/view`;
    }, 500);
  });
/* -------------------- Recipe Scaling -------------------- */
function parseQty(s) {
  if (!s) return null;
  s = s.trim();
  // "1/2", "1 1/2", "2", "2.5", "400"
  if (/^\d+\s+\d+\/\d+$/.test(s)) {
    const [whole, frac] = s.split(/\s+/);
    const [n, d] = frac.split("/").map(Number);
    return Number(whole) + n / d;
  }
  if (/^\d+\/\d+$/.test(s)) {
    const [n, d] = s.split("/").map(Number);
    return n / d;
  }
  const f = parseFloat(s);
  return isNaN(f) ? null : f;
}

function formatQty(n) {
  if (n == null) return "";
  // Snap to nearest 1/4 if close
  const whole = Math.floor(n);
  const frac = n - whole;
  const fractions = [
    [0, ""], [0.25, " 1/4"], [0.5, " 1/2"], [0.75, " 3/4"], [1, ""],
  ];
  let best = fractions[0], bestDiff = Infinity;
  for (const [v, label] of fractions) {
    const d = Math.abs(v - frac);
    if (d < bestDiff) { bestDiff = d; best = [v, label]; }
  }
  const rounded = whole + (best[0] === 1 ? 1 : 0);
  return `${rounded}${best[0] === 1 ? "" : best[1]}`.trim() || "0";
}

document.addEventListener("DOMContentLoaded", () => {
  document.documentElement.classList.remove("theme-dark-pre");
});

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-scale]");
  if (!btn) return;
  const factor = parseFloat(btn.dataset.scale);
  const list = $("[data-scalable]");
  if (!list) return;

  // Toggle active button
  $$("[data-scale]").forEach(b => b.classList.remove("btn--primary"));
  $$("[data-scale]").forEach(b => b.classList.add("btn--ghost"));
  btn.classList.add("btn--primary");
  btn.classList.remove("btn--ghost");

  $$("[data-original-qty]", list).forEach((el) => {
    const orig = el.dataset.originalQty;
    const origWeight = el.dataset.originalWeight || "";
    const n = parseQty(orig);
    if (n == null) return;
    el.childNodes[0].nodeValue = formatQty(n * factor);
  });
});
  /* -------------------- Settings forms -------------------- */

  /* Live avatar preview when a file is selected */
  document.addEventListener("change", (e) => {
    if (e.target.id !== "avatar") return;
    const file = e.target.files[0];
    if (!file) return;
    const previewEl = $("#avatar-preview");
    if (!previewEl) return;
    const url = URL.createObjectURL(file);
    if (previewEl.tagName === "IMG") {
      previewEl.src = url;
    } else {
      /* Replace placeholder div with an img */
      const img = document.createElement("img");
      img.id = "avatar-preview";
      img.src = url;
      img.alt = "Avatar preview";
      previewEl.replaceWith(img);
    }
  });

  document.addEventListener("submit", async (e) => {
    const settingsForm = e.target.closest("[data-settings-form]");
    if (settingsForm) {
      e.preventDefault();
      const fd = new FormData(settingsForm);
      const { ok: isOk, data } = await request("/users/me", { method: "PUT", form: fd });
      toast(isOk && data.success ? "Profile saved." : (data.message || "Save failed."),
            isOk ? "success" : "danger");
      if (isOk && data.success) {
        setTimeout(() => window.location.reload(), 600);
      }
      return;
    }

    const prefsForm = e.target.closest("[data-prefs-form]");
    if (prefsForm) {
      e.preventDefault();
      const toList = (v) => v.split(",").map((s) => s.trim()).filter(Boolean);
      const body = {
        categories: toList(prefsForm.querySelector("#categories").value),
        dietary:    toList(prefsForm.querySelector("#dietary").value),
      };
      const { ok, data } = await request("/users/me/preferences", { method: "PUT", body });
      toast(ok && data.success ? "Preferences saved." : (data.message || "Save failed."),
            ok ? "success" : "danger");
    }
  });

})();