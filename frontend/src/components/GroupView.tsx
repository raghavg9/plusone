import { useEffect, useRef, useState } from "react";
import { api, ChatMessage, Group, User } from "../api";

export default function GroupView({
  group,
  me,
}: {
  group: Group;
  me: User;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [body, setBody] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const m = await api.getMessages(group.id);
        if (alive) setMessages(m);
      } catch {
        /* ignore transient poll errors */
      }
    };
    load();
    const t = setInterval(load, 3000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [group.id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const nameOf = (uid: number) =>
    group.members.find((m) => m.user.id === uid)?.user.name ?? "Someone";

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    const sent = await api.postMessage(group.id, me.id, body.trim());
    setMessages((prev) => [...prev, sent]);
    setBody("");
  }

  return (
    <div className="card">
      <span className="badge">Matched</span>
      <h2>Your group for {group.event.title}</h2>
      <p className="muted">
        {group.event.category} · {group.event.location || "location TBD"} ·
        {group.vibe} vibe
      </p>

      <div className="members">
        {group.members.map(({ user }) => (
          <div key={user.id} className="member">
            <div className="member-head">
              <strong>{user.name}</strong>
              <span className="muted">
                {user.age} · {user.gender}
              </span>
              {user.phone_verified && (
                <span className="badge small">verified</span>
              )}
            </div>
            {user.bio && <p className="bio">{user.bio}</p>}
            <div className="socials">
              {user.instagram && <span>IG {user.instagram}</span>}
              {user.linkedin && <span>in {user.linkedin}</span>}
              {user.spotify && <span>Spotify {user.spotify}</span>}
            </div>
          </div>
        ))}
      </div>

      <h3>Group chat</h3>
      <p className="muted">
        Coordinate a meetup spot, arrival time, and rides before the event.
      </p>
      <div className="chat">
        {messages.length === 0 && (
          <p className="muted">No messages yet — say hi!</p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={m.user_id === me.id ? "msg mine" : "msg"}
          >
            <span className="msg-author">{nameOf(m.user_id)}</span>
            <span>{m.body}</span>
          </div>
        ))}
        <div ref={endRef} />
      </div>
      <form className="chat-form" onSubmit={send}>
        <input
          value={body}
          onChange={(e) => setBody(e.target.value)}
          placeholder="Message your group…"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
