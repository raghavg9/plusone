import { useState } from "react";
import { api, MatchResult, User } from "../api";

export default function FindGroupForm({
  user,
  onMatch,
}: {
  user: User;
  onMatch: (r: MatchResult) => void;
}) {
  const [ev, setEv] = useState({
    external_url: "",
    title: "",
    category: "concert",
    location: "",
  });
  const [pref, setPref] = useState({
    vibe: "casual",
    age_band: "any",
    gender_preference: "any",
    social_anxiety_friendly: false,
    first_timer: false,
  });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      const event = await api.createEvent(ev);
      const result = await api.createMatchRequest({
        user_id: user.id,
        event_id: event.id,
        ...pref,
      });
      onMatch(result);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>Find a group</h2>
      <p className="muted">
        Paste the event you're eyeing and tell us the kind of group you want.
      </p>
      <label>Event link
        <input required type="url" placeholder="https://tickets..."
          value={ev.external_url}
          onChange={(e) => setEv({ ...ev, external_url: e.target.value })} />
      </label>
      <div className="row">
        <label>Event name
          <input required value={ev.title}
            onChange={(e) => setEv({ ...ev, title: e.target.value })} />
        </label>
        <label>Category
          <select value={ev.category}
            onChange={(e) => setEv({ ...ev, category: e.target.value })}>
            {["concert", "nightlife", "festival", "hike", "meetup",
              "sports", "conference", "other"].map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </label>
      </div>
      <label>Location
        <input value={ev.location}
          onChange={(e) => setEv({ ...ev, location: e.target.value })} />
      </label>

      <h3>Group preferences</h3>
      <div className="row">
        <label>Vibe
          <select value={pref.vibe}
            onChange={(e) => setPref({ ...pref, vibe: e.target.value })}>
            {["casual", "party", "networking", "chill"].map((v) => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </label>
        <label>Age band
          <select value={pref.age_band}
            onChange={(e) =>
              setPref({ ...pref, age_band: e.target.value })}>
            <option value="any">Any age</option>
            <option value="20s">20s</option>
            <option value="30s">30s</option>
            <option value="40plus">40+</option>
          </select>
        </label>
      </div>
      <label>Group composition
        <select value={pref.gender_preference}
          onChange={(e) =>
            setPref({ ...pref, gender_preference: e.target.value })}>
          <option value="any">Open to anyone</option>
          <option value="women_only">Women only</option>
          <option value="men_only">Men only</option>
        </select>
      </label>
      <label className="check">
        <input type="checkbox" checked={pref.social_anxiety_friendly}
          onChange={(e) =>
            setPref({ ...pref, social_anxiety_friendly: e.target.checked })} />
        Low-pressure / social-anxiety friendly
      </label>
      <label className="check">
        <input type="checkbox" checked={pref.first_timer}
          onChange={(e) =>
            setPref({ ...pref, first_timer: e.target.checked })} />
        First-timer
      </label>
      {err && <p className="err">{err}</p>}
      <button type="submit" disabled={busy}>
        {busy ? "Matching…" : "Match me with people going"}
      </button>
    </form>
  );
}
