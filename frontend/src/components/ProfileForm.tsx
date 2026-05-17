import { useState } from "react";
import { api, User } from "../api";

export default function ProfileForm({ onDone }: { onDone: (u: User) => void }) {
  const [form, setForm] = useState({
    name: "",
    age: 25,
    gender: "unspecified",
    bio: "",
    instagram: "",
    linkedin: "",
    spotify: "",
    phone_verified: false,
  });
  const [err, setErr] = useState("");

  const set = (k: string, v: unknown) => setForm({ ...form, [k]: v });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      onDone(await api.createUser(form));
    } catch (e) {
      setErr((e as Error).message);
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>Create your profile</h2>
      <p className="muted">
        Lightweight social proof helps your group feel comfortable before
        meeting.
      </p>
      <label>Name
        <input required value={form.name}
          onChange={(e) => set("name", e.target.value)} />
      </label>
      <div className="row">
        <label>Age
          <input type="number" min={16} max={99} value={form.age}
            onChange={(e) => set("age", Number(e.target.value))} />
        </label>
        <label>Gender
          <select value={form.gender}
            onChange={(e) => set("gender", e.target.value)}>
            <option value="unspecified">Prefer not to say</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="nonbinary">Non-binary</option>
          </select>
        </label>
      </div>
      <label>Short bio
        <textarea value={form.bio}
          onChange={(e) => set("bio", e.target.value)}
          placeholder="First-time raver, love indie rock, easygoing." />
      </label>
      <div className="row">
        <label>Instagram
          <input value={form.instagram} placeholder="@handle"
            onChange={(e) => set("instagram", e.target.value)} />
        </label>
        <label>LinkedIn
          <input value={form.linkedin} placeholder="profile url"
            onChange={(e) => set("linkedin", e.target.value)} />
        </label>
      </div>
      <div className="row">
        <label>Spotify
          <input value={form.spotify} placeholder="profile / top artist"
            onChange={(e) => set("spotify", e.target.value)} />
        </label>
        <label className="check">
          <input type="checkbox" checked={form.phone_verified}
            onChange={(e) => set("phone_verified", e.target.checked)} />
          Phone verified
        </label>
      </div>
      {err && <p className="err">{err}</p>}
      <button type="submit">Continue</button>
    </form>
  );
}
