import { useEffect, useState } from "react";
import { api, Group, MatchResult, User } from "./api";
import ProfileForm from "./components/ProfileForm";
import FindGroupForm from "./components/FindGroupForm";
import GroupView from "./components/GroupView";

type Step = "profile" | "find" | "waiting" | "group";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [requestId, setRequestId] = useState<number | null>(null);
  const [group, setGroup] = useState<Group | null>(null);
  const [step, setStep] = useState<Step>("profile");

  function handleMatch(r: MatchResult) {
    if (r.matched && r.group) {
      setGroup(r.group);
      setStep("group");
    } else {
      setRequestId(r.request.id);
      setStep("waiting");
    }
  }

  useEffect(() => {
    if (step !== "waiting" || requestId == null) return;
    const t = setInterval(async () => {
      const r = await api.getMatchRequest(requestId);
      if (r.matched && r.group) {
        setGroup(r.group);
        setStep("group");
      }
    }, 3000);
    return () => clearInterval(t);
  }, [step, requestId]);

  return (
    <div className="app">
      <header>
        <h1>PlusOne</h1>
        <p className="tagline">You'll always have people to go with.</p>
      </header>

      {step === "profile" && (
        <ProfileForm
          onDone={(u) => {
            setUser(u);
            setStep("find");
          }}
        />
      )}

      {step === "find" && user && (
        <FindGroupForm user={user} onMatch={handleMatch} />
      )}

      {step === "waiting" && (
        <div className="card center">
          <span className="badge">Searching</span>
          <h2>Looking for your group…</h2>
          <p className="muted">
            We're waiting for enough compatible attendees for this event.
            You'll be matched into a small group automatically — keep this
            tab open.
          </p>
          <div className="spinner" />
        </div>
      )}

      {step === "group" && group && user && (
        <GroupView group={group} me={user} />
      )}

      <footer className="muted">
        A social coordination layer for events — embeds into ticketing &
        discovery platforms.
      </footer>
    </div>
  );
}
